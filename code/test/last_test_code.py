import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json

# 配置路径
MODEL_NAME = "/model/ModelScope/Qwen/Qwen3-8B"
LORA_WEIGHTS_PATH = "lora_Qwen3-8B_yaolao"  # 你训练保存的LoRA权重路径

class YaolaoTester:
    def __init__(self, base_model_path, lora_weights_path, device="auto"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(
            base_model_path, 
            trust_remote_code=True
        )
        
        # 如果pad_token不存在，设置为eos_token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 加载基础模型
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map=device,
            low_cpu_mem_usage=True
        )
        
        # 加载LoRA权重
        self.model = PeftModel.from_pretrained(
            self.base_model,
            lora_weights_path,
            torch_dtype=torch.float16
        )
        
        self.model.eval()
        print("模型加载完成！")
    
    def generate_response(self, user_input, system_prompt="你是药老",RAGcontent=None ,max_length=512, temperature=0.7, top_p=0.9):
        """生成回复"""
        if RAGcontent:
            Augmented_system_prompt = f"{system_prompt}\n根据以下相关知识来回答问题：\n{RAGcontent}"
        else:
            Augmented_system_prompt = system_prompt
        # 构建对话格式
        messages = [
            {"role": "system", "content": Augmented_system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # 应用聊天模板
        text = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Tokenize
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        
        # 生成参数
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # 解码回复
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        )
        return response.strip()
    
    def batch_test(self, test_cases, system_prompt="你是药老"):
        """批量测试多个案例"""
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"\n{'='*50}")
            print(f"测试案例 {i+1}/{len(test_cases)}")
            print(f"用户输入: {test_case}")
            
            response = self.generate_response(test_case, system_prompt)
            print(f"模型回复: {response}")
            
            results.append({
                "input": test_case,
                "output": response
            })
        
        return results
    
def load_test_cases():
    """加载测试案例，如果没有提供文件则使用默认测试案例"""
    # 默认测试案例 - 可以根据你的"药老"角色特点调整
    test_cases = [
        "我的父亲叫什么名字?",
        "斗气大陆将功法分为几个等级？",
        "怎么判断丹药品质？",
        "帮我写一份Python代码实现快速排序。",
        "老师，您知道iPhone怎么升级系统吗？",
    ]
    
    return test_cases

def main():
    # 初始化测试器
    tester = YaolaoTester(MODEL_NAME, LORA_WEIGHTS_PATH)
    
    test_cases = load_test_cases()
    
    print("开始批量测试...")
    results = tester.batch_test(test_cases)
    
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"\n测试完成！结果已保存到 test_results.json")
if __name__ == "__main__":
    main()