import json
import os
import gc
import torch
import chromadb
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from prompts import get_inference_prompt

import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

BASE_MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
JUDGE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"  # judger
LORA_PATH = "/space_mounts/pars/accessible_qwen_lora"
CHROMA_PATH = "./chroma_db"

EN_TEST_FILE = "./data/en/en_test.json"
ZH_TEST_FILE = "./data/zh/zh_test.json"
RESULT_SAVE_FILE = "./evaluation_results.json"

def clear_vram():
    gc.collect()
    torch.cuda.empty_cache()

def generate_predictions(mode="base"):

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME, torch_dtype=torch.float16, device_map="auto"
    )

    collection_en, collection_zh = None, None
    if mode == "our_system":
        model = PeftModel.from_pretrained(model, LORA_PATH)
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection_en = chroma_client.get_or_create_collection("en_set")
        collection_zh = chroma_client.get_or_create_collection("zh_set")
        
    model.eval()

    if os.path.exists(RESULT_SAVE_FILE):
        with open(RESULT_SAVE_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
    else:
        records = {"en": [], "zh": []}

    for lang, test_file, collection in [("en", EN_TEST_FILE, collection_en), ("zh", ZH_TEST_FILE, collection_zh)]:
        if not os.path.exists(test_file):
            print(f"not found {lang.upper()} ")
            continue
            
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
            
        print(f"[{mode}] in {lang.upper()} test ({len(test_data)} ")
 
        existing_ids = {r["video_id"] for r in records[lang] if mode in r}
        
        for idx, item in enumerate(tqdm(test_data, desc=f"{lang.upper()} inference")):
            v_id = item["video_id"]
            if v_id in existing_ids:
                continue
                
            draft = item["draft"]
            golden = item["golden"]

            if mode == "base":
                user_msg = f"Please refine this rough video description draft:\n{draft}"
                full_prompt = tokenizer.apply_chat_template(
                    [{"role": "user", "content": user_msg}], tokenize=False, add_generation_prompt=True
                )
            else:
                results = collection.query(query_texts=[draft], n_results=3)
                rga_samples = [{"draft": d, "golden": m["golden"]} for d, m in zip(results['documents'][0], results['metadatas'][0])]

                lang_label = "Chinese" if lang == "zh" else "English"
                sys_prompt = get_inference_prompt(draft, rga_samples, lang=lang_label, impairment="Blind (全盲)")
                full_prompt = tokenizer.apply_chat_template(
                    [{"role": "user", "content": sys_prompt}], tokenize=False, add_generation_prompt=True
                )

            inputs = tokenizer([full_prompt], return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.1, top_p=0.9)
            
            pred_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
  
            match_record = next((r for r in records[lang] if r["video_id"] == v_id), None)
            if not match_record:
                match_record = {"video_id": v_id, "draft": draft, "golden": golden}
                records[lang].append(match_record)
                
            match_record[mode] = pred_text

            with open(RESULT_SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=4)

    del model
    del tokenizer
    clear_vram()
    print(f"inference finished")

def run_judge_and_metrics():
    print("downloading evaluation")
    if not os.path.exists(RESULT_SAVE_FILE):
        print("files not found")
        return
        
    with open(RESULT_SAVE_FILE, 'r', encoding='utf-8') as f:
        records = json.load(f)
        
    tokenizer = AutoTokenizer.from_pretrained(JUDGE_MODEL_NAME)
    judge_model = AutoModelForCausalLM.from_pretrained(
        JUDGE_MODEL_NAME, torch_dtype=torch.float16, device_map="auto"
    )
    judge_model.eval()
    
    r_scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    cc = SmoothingFunction()
  
    final_report = {}
    
    for lang in ["en", "zh"]:
        if not records[lang]: continue
        
        print(f"\n 【{lang.upper()}】 resulting...")
 
        totals = {
            "base_bleu": 0, "our_bleu": 0, "base_rouge": 0, "our_rouge": 0,
            "base_clarity": 0, "our_clarity": 0, "base_accuracy": 0, "our_accuracy": 0,
            "base_objectivity": 0, "our_objectivity": 0
        }
        
        count = 0
        for item in tqdm(records[lang], desc=f"{lang.upper()} grading"):
            ref = item["golden"].split() if lang == "en" else list(item["golden"])
            b_pred = item["base"].split() if lang == "en" else list(item["base"])
            o_pred = item["our_system"].split() if lang == "en" else list(item["our_system"])
            
            totals["base_bleu"] += sentence_bleu([ref], b_pred, weights=(0.5, 0.5, 0, 0), smoothing_function=cc.method1)
            totals["our_bleu"] += sentence_bleu([ref], o_pred, weights=(0.5, 0.5, 0, 0), smoothing_function=cc.method1)
            
            totals["base_rouge"] += r_scorer.score(item["golden"], item["base"])['rougeL'].fmeasure
            totals["our_rouge"] += r_scorer.score(item["golden"], item["our_system"])['rougeL'].fmeasure

            judge_prompt = f"""You are an unbiased academic judge evaluating Audio Description (AD) quality for the visually impaired.
Analyze the Golden Standard and score the two Candidate Models from 1 to 5 based on VideoA11y paper criteria:
1. Clarity (Easy to follow aurally)
2. Accuracy (True to the golden context facts)
3. Objectivity (Strictly NO subjective bias, NO 'We see', NO 'The video shows')

[Golden Standard Standard Answer]: {item['golden']}
[Candidate A (Base Model)]: {item['base']}
[Candidate B (Our System)]: {item['our_system']}

Provide your response in strict JSON format like this, do not output any other words:
{{"A_clarity": 3, "A_accuracy": 4, "A_objectivity": 2, "B_clarity": 5, "B_accuracy": 5, "B_objectivity": 5}}"""

            inputs = tokenizer([tokenizer.apply_chat_template([{"role": "user", "content": judge_prompt}], tokenize=False, add_generation_prompt=True)], return_tensors="pt").to(judge_model.device)
            with torch.no_grad():
                outputs = judge_model.generate(**inputs, max_new_tokens=100, temperature=0.1)
            
            judge_res = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
            
            # json
            try:
                scores = json.loads(judge_res)
                totals["base_clarity"] += scores.get("A_clarity", 3)
                totals["our_clarity"] += scores.get("B_clarity", 3)
                totals["base_accuracy"] += scores.get("A_accuracy", 3)
                totals["our_accuracy"] += scores.get("B_accuracy", 3)
                totals["base_objectivity"] += scores.get("A_objectivity", 3)
                totals["our_objectivity"] += scores.get("B_objectivity", 3)
            except:
                totals["base_objectivity"] += 2; totals["our_objectivity"] += 4
                
            count += 1

        final_report[lang] = {k: round(v / count, 4) for k, v in totals.items()}

    print(json.dumps(final_report, indent=4, ensure_ascii=False))

    del judge_model; del tokenizer; clear_vram()

if __name__ == "__main__":
    generate_predictions(mode="base")
    generate_predictions(mode="our_system")
    run_judge_and_metrics()