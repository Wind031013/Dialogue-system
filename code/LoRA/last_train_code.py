import json
import os
from dataclasses import dataclass
import torch
from datasets import Dataset
import gc
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
)

from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training

# 配置路径
OUTPUT_DIR = "lora_Qwen3-8B_yaolao"
YAOLAO_JSON = "/root/yaolao/data_head_revise.json"
MODEL_NAME = "/model/ModelScope/Qwen/Qwen3-8B"

# 训练超参
NUM_EPOCHS = 3                              # 训练轮数
LEARNING_RATE = 2e-4                        # 学习率        
PER_DEVICE_BATCH_SIZE = 12                  # 每个设备的批大小（取决于显存）
GRAD_ACCUM_STEPS = 3                        # 梯度累积步数   
WEIGHT_DECAY = 0.0                          # 权重衰减
LOGGING_STEPS = 50                          # 日志记录步数
SAVE_STEPS = 500                            # 模型保存步数
MAX_LENGTH = 1024                           # 最大输入长度

# LoRA 配置
LORA_R = 16                                 # 秩（rank）
LORA_ALPHA = 32                             # alpha         （缩放因子）
LORA_DROPOUT = 0.05                         # dropout       （丢弃率）

def find_all_linear_names(model):
    cls = torch.nn.Linear
    lora_module_names = set()
    for name, module in model.named_modules():
        if isinstance(module, cls):
            names = name.split('.')
            lora_module_names.add(names[0] if len(names) == 1 else names[-1])
    # 过滤掉不适合的模块
    exclude = {'lm_head'}
    lora_module_names = [name for name in lora_module_names if name not in exclude]
    return lora_module_names

def load_data(json_path: str):
    """从json文件中加载数据"""
    with open(json_path, "r") as f:
        conversations = json.load(f)
    return conversations

def build_examples(conversations:list[dict], system_prompt: str = "你是药老"):
    """从conversations中构建单轮对话训练样本"""
    examples = []
    for conv in conversations:
        if not conv or 'user' not in conv or 'assistant' not in conv:
            continue

        examples.append([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": conv['user']},
            {"role": "assistant", "content": conv['assistant']}
        ])
    return examples


def train_qwen_load_data(tokenizer):
    examples_all = {"conversations": []}
    conversations = load_data(YAOLAO_JSON)
    print("数据集加载完成")
    
    for i in range(0, len(conversations)):
        examples_all["conversations"].extend(build_examples(conversations[i]['conversations']))
        
    # 创建Dataset
    dataset = Dataset.from_dict({"conversations": examples_all['conversations']})
    
    def tokenize_function(examples):
        # 应用chat模板
        texts = tokenizer.apply_chat_template(
            examples['conversations'],
            tokenize=False
        )
        
        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            max_length=MAX_LENGTH,
            padding=False
        )
        
        # 对于语言模型，labels通常就是input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
    # 处理数据集
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    print(f"构造了 {len(tokenized_dataset)} 个训练样本")
    return tokenized_dataset

def main():
    # 加载分词器
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    print("分词器加载完成")
    
    # 加载对话数据
    examples_all = train_qwen_load_data(tokenizer)
    
    # 模型加载
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,                     # 使用自定义代码
        device_map="auto",                          # 自动分配设备
        load_in_8bit=True,                          # 8-bit 模型
        torch_dtype=torch.float16                   # 使用半精度浮点数
    )
    print("模型加载完成")
    
    # 查找所有线性层名称
    TARGET_MODULES = find_all_linear_names(model)
    print(f"找到的线性层模块: {TARGET_MODULES}")
    
    # 使模型为 k-bit/8bit 微调做好准备
    model = prepare_model_for_kbit_training(model)
    
    # 配置 LoRA
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=TARGET_MODULES,
    )
    model = get_peft_model(model, peft_config)
    
    # 使用Data collator 进行填充
    data_collator = DataCollatorForSeq2Seq(
        tokenizer, 
        model=model, 
        padding=True,
        pad_to_multiple_of=8  # 优化GPU效率
    )
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,                               # 输出目录
        # 批次大小相关
        per_device_train_batch_size=PER_DEVICE_BATCH_SIZE,   # 每个GPU的批次大小
        gradient_accumulation_steps=GRAD_ACCUM_STEPS,        # 梯度累积步数
        # 学习率
        warmup_ratio=0.03,                                   # 学习率warmup比例（前3%的step进行warmup）
        learning_rate=LEARNING_RATE,                         # 初始学习率
        # 训练周期
        num_train_epochs=NUM_EPOCHS,                         # 训练的总轮数
        # 混合精度训练
        fp16=True,                                           # 使用FP16混合精度训练，减少显存使用，加快训练速度
        # 日志与保存策略
        logging_steps=LOGGING_STEPS,                         # 每多少步记录一次日志
        save_strategy="steps",                               # 保存策略 ： 按步数保存模型
        save_steps=SAVE_STEPS,                               # 每多少步保存一次模型
        save_total_limit=3,                                  # 最多保存模型数量
        # 数据列处理
        remove_unused_columns=False,                         # 不要移除未使用的列
        report_to="none",                                    # 不使用任何报告工具（如 WandB）
        # 优化器配置
        optim="paged_adamw_8bit",                            # 使用 8-bit Adam 优化器
    )
    
    # 训练器
    trainer = Trainer(
        model=model,                    
        args=training_args,
        train_dataset=examples_all,
        data_collator=data_collator,
    )

    # 开始训练
    trainer.train()

    # 保存 LoRA 权重
    model.save_pretrained(OUTPUT_DIR)
    print(f"训练完成并将 LoRA 权重保存到 {OUTPUT_DIR}")
    
    # 清理内存
    del model, trainer
    torch.cuda.empty_cache()
    gc.collect()

if __name__ == "__main__":
    main()