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
model=AutoModelForCausalLM.from_pretrained(BASE_MODEL,device_map="auto")

lora_cfg=LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05,
    bias="none", task_type="CAUSAL_LM",
    target_modules=["c_attn","c_proj"]
)