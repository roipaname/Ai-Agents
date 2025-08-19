import os, json
from dataclasses import dataclass
from typing import Dict, List
from datasets import load_dataset
from transformers import (AutoTokenizer, AutoModelForCausalLM,
                          DataCollatorForLanguageModeling, Trainer, TrainingArguments)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from dotenv import load_dotenv

load_dotenv()
BASE_MODEL=os.getenv("BASE_MODEL","gpt3")
print(f"using model for finetuning :{BASE_MODEL}")
DATA_PATH = "data/lecture_instructions.jsonl"
OUT_DIR = "models/lora-lecture-gpt2"
"""
Loading tokenizer and setting eos for tokenizer
"""
tokenizer=AutoTokenizer.from_pretrained(BASE_MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token=tokenizer.eos_token

"""
Setting up model
"""
model=AutoModelForCausalLM.from_pretrained(BASE_MODEL,device_map="auto")

lora_cfg=LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05,
    bias="none", task_type="CAUSAL_LM",
    target_modules=["c_attn","c_proj"]
)
model=get_peft_model(model,lora_cfg)
"""
loading dataset
"""
dataset=load_dataset(
    "json",
    data_files=DATA_PATH,
    split="train"
)

def format_example(ex):
    # supervised fine-tuning: concatenate prompt + response
    text = ex["prompt"].strip() + "\n" + ex["response"].strip()
    return {"text": text}
dataset=dataset.map(format_example,remove_columns=dataset.column_names)

def tokenize(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        max_length=1024,
        padding="max_length",
        return_tensors=None,
    )
tokenized=dataset.map(tokenize,batched=True,remove_columns=["text"])

data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)
"""
Training arguments set up
"""

args = TrainingArguments(
    output_dir=OUT_DIR,
    num_train_epochs=2,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    weight_decay=0.01,
    logging_steps=50,
    save_steps=500,
    save_total_limit=2,
    bf16=False,
    fp16=False,
    report_to="none",
)
trainer=Trainer(
    model=model,
    args=args,
    data_collator=data_collator,
    train_dataset=tokenized
)

trainer.train()
# 5) Save adapter + tokenizer
trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)
print(f"Saved LoRA adapter to {OUT_DIR}")