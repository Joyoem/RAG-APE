# remember run
# pip install transformers peft bitsandbytes accelerate datasets trl torch

import json
import torch
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTConfig, SFTTrainer

from prompts import SFT_SYSTEM_PROMPT

# hyper parameter
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"      
TRAIN_FILE = "./data/en/en_train.json"        
VAL_FILE = "./data/en/en_val.json"            
OUTPUT_DIR = "./model_checkpoints"            

BATCH_SIZE = 8                               
GRADIENT_ACCUMULATION_STEPS = 2               
LEARNING_RATE = 2e-4                          
EPOCHS = 1                                   
MAX_LENGTH = 512                             


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def format_prompt(sample):
    messages = [
        {"role": "system", "content": SFT_SYSTEM_PROMPT}, 
        {"role": "user", "content": f"Please refine this rough video description draft:\n{sample['draft']}"},
        {"role": "assistant", "content": sample['golden']}
    ]

    prompt_text = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": prompt_text}

def main():
    print("loading dataset with prompts...")
    with open(TRAIN_FILE, 'r', encoding='utf-8') as f:
        train_data = json.load(f)
    with open(VAL_FILE, 'r', encoding='utf-8') as f:
        val_data = json.load(f)
        
    train_dataset = Dataset.from_list(train_data).map(format_prompt)
    val_dataset = Dataset.from_list(val_data).map(format_prompt)

    print("loading model...")
    tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    

    print("adding LORA metrics...")
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters() 

    print("monitoring...")
    # ✅ 核心修正：改用 SFTConfig，并将数据相关的参数统统收归到这里面！
    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        num_train_epochs=EPOCHS,
        eval_strategy="epoch",            
        save_strategy="epoch",            
        logging_steps=10,                 
        fp16=True,  
        bf16=False,                      
        lr_scheduler_type="cosine",       
        warmup_ratio=0.03,                
        remove_unused_columns=False,
        report_to="none",
        dataset_text_field="text",         
        max_length=MAX_LENGTH          
    )

    print("training...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,  
        args=training_args
    )

    trainer.train()
    
    final_lora_path = f"{OUTPUT_DIR}/final_accessible_qwen"
    trainer.model.save_pretrained(final_lora_path)
    print(f"traning finished to: {final_lora_path}")

if __name__ == "__main__":
    main()