import os
import torch
import chromadb
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from prompts import get_inference_prompt

class FullADSystem:
    def __init__(self):
        print("📥 1. 正在连接本地高速向量数据库 (ChromaDB)...")
        # 对应你全局配置里的 CHROMA_PATH = "./chroma_db"
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_en = self.chroma_client.get_or_create_collection("en_set")
        self.collection_zh = self.chroma_client.get_or_create_collection("zh_set")
        
        print("🤖 2. 正在加载 1.5B 基础大脑模型...")
        base_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        
        # 自动适配本地硬件（Mac的M芯片用mps，英伟达显卡用cuda，普通轻薄本用cpu）
        if torch.cuda.is_available():
            device_str = "cuda"
            dtype = torch.float16
        elif torch.backends.mps.is_available():
            device_str = "mps"
            dtype = torch.float16
        else:
            device_str = "cpu"
            dtype = torch.float32
            
        print(f"🖥️ 系统检测：正在将本地 Demo 部署在 [{device_str.upper()}] 上运行...")
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name, torch_dtype=dtype, device_map=device_str
        )
        
        print("🧬 3. 正在缝合本地 LoRA 无障碍基因权重...")
        # 对应你全局配置里的 LORA_PATH
        lora_path = "./final_accessible_qwen"
        if os.path.exists(lora_path):
            self.model = PeftModel.from_pretrained(base_model, lora_path)
        else:
            print("⚠️ 未在本地找到 LoRA 权重，降级为原厂模型 + RAG 运行。")
            self.model = base_model
            
        self.model.eval()
        print("🎉 前端专属实时推理引擎组装就位！")

    def generate_accessible_ad(self, draft, lang="English", impairment="Blind (全盲)"):
        """这个函数完美继承了你 evaluate.py 里的 if/else 推理神髓，但专门服务于网页单条实时生成"""
        collection = self.collection_zh if lang == "Chinese" else self.collection_en
        
        rga_samples = []
        try:
            # 完美的 RAG 捞针逻辑
            results = collection.query(query_texts=[draft], n_results=3)
            rga_samples = [{"draft": d, "golden": m["golden"]} for d, m in zip(results['documents'][0], results['metadatas'][0])]
        except:
            rga_samples = [] # 强力保命防御，库坏了也绝不闪退
            
        lang_label = "Chinese" if lang == "Chinese" else "English"
        sys_prompt = get_inference_prompt(draft, rga_samples, lang=lang_label, impairment=impairment)
        full_prompt = self.tokenizer.apply_chat_template([{"role": "user", "content": sys_prompt}], tokenize=False, add_generation_prompt=True)
        
        inputs = self.tokenizer([full_prompt], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=200, temperature=0.1, top_p=0.9)
            
        pred_text = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()
        return pred_text