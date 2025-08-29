import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria, StoppingCriteriaList
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class SimpleChatbot:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        初始化对话机器人
        :param model_name: 预训练模型名称
        """
        print("正在加载模型，请稍候...")
        
        # 加载tokenizer和模型
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # 设置pad_token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("模型加载完成！")
        print("=" * 50)
    
    def generate_response(self, user_input: str, chat_history: List[Dict[str, str]], 
                         max_length: int = 1000, temperature: float = 0.7) -> str:
        """
        生成回复
        :param user_input: 用户输入
        :param chat_history: 对话历史
        :param max_length: 生成的最大长度
        :param temperature: 温度参数，控制生成随机性
        :return: 模型生成的回复
        """
        # 将对话历史格式化为模型输入
        input_text = self._format_conversation(user_input, chat_history)
        
        # 编码输入文本
        inputs = self.tokenizer.encode(input_text, return_tensors="pt")
        
        # 生成回复
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )
        
        # 解码生成的文本
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 提取新生成的回复（去掉输入部分）
        new_response = response[len(input_text):].strip()
        
        return new_response
    
    def _format_conversation(self, user_input: str, chat_history: List[Dict[str, str]]) -> str:
        """
        格式化对话历史为模型输入
        :param user_input: 当前用户输入
        :param chat_history: 对话历史
        :return: 格式化后的文本
        """
        # 开始构建对话文本
        conversation_text = ""
        
        # 添加历史对话
        for turn in chat_history:
            conversation_text += f"用户: {turn['user']}\n机器人: {turn['bot']}\n"
        
        # 添加当前用户输入
        conversation_text += f"用户: {user_input}\n机器人:"
        
        return conversation_text

class StopOnTokens(StoppingCriteria):
    """自定义停止条件"""
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = [self.tokenizer.eos_token_id, self.tokenizer.pad_token_id]
        return any(stop_id in input_ids for stop_id in stop_ids)

def run_chat_demo():
    """运行聊天演示"""
    # 初始化聊天机器人
    chatbot = SimpleChatbot("microsoft/DialoGPT-medium")
    
    # 存储对话历史
    chat_history = []
    
    print("对话系统Demo已启动！")
    print("输入 '退出' 来结束对话")
    print("输入 '清除' 来清除对话历史")
    print("=" * 50)
    
    while True:
        # 获取用户输入
        user_input = input("你: ").strip()
        
        # 检查退出条件
        if user_input.lower() in ['退出', 'exit', 'quit']:
            print("再见！")
            break
        
        # 检查清除历史条件
        if user_input.lower() in ['清除', 'clear', '重置']:
            chat_history = []
            print("对话历史已清除")
            continue
        
        if not user_input:
            continue
        
        try:
            # 生成回复
            response = chatbot.generate_response(user_input, chat_history)
            
            # 显示回复
            print(f"机器人: {response}")
            print("-" * 30)
            
            # 保存到对话历史
            chat_history.append({
                "user": user_input,
                "bot": response
            })
            
            # 限制历史记录长度，避免内存问题
            if len(chat_history) > 10:
                chat_history = chat_history[-5:]
                
        except Exception as e:
            print(f"生成回复时出错: {e}")
            continue

if __name__ == "__main__":
    # 运行聊天演示
    run_chat_demo()