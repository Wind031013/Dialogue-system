import re
import os
import json
import jieba 
import jieba.posseg as pseg
from collections import Counter
from typing import List, Dict, Any, Tuple

class DialogueProcessor:
    def __init__(self, user_dict_path: str):
        """初始化处理器"""
        try:
            jieba.load_userdict(user_dict_path)
        except FileNotFoundError:
            print(f"用户词典文件未找到: {user_dict_path}")
        self.person_flags = {'nr', 'nrt', 'nz'}
        self.adjective_flags = {'a', 'ad', 'an'}
    
    def read_data(self, file_path: str) -> List[str]:
        """读取数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            print(f"文件未找到: {file_path}")
            return []
        except UnicodeDecodeError:
            print(f"文件编码错误: {file_path}")
            return []
    
    def get_file_count(self, directory_path: str) -> int:
        """获取目录中的文件数量"""
        try:
            return len([name for name in os.listdir(directory_path) 
                       if os.path.isfile(os.path.join(directory_path, name))])
        except FileNotFoundError:
            print(f"目录不存在: {directory_path}")
            return 0
        except PermissionError:
            print(f"没有权限访问目录: {directory_path}")
            return 0
    
    def find_name_adjective(self, text: str) -> Tuple[List[str], List[str]]:
        """从文本中提取人名和形容词"""
        # 移除引号内的内容，避免对话内容干扰词性分析
        text_without_quotes = re.sub(r'"[^"]*"', '', text)
        words = pseg.cut(text_without_quotes)
        
        persons = []
        adjectives = []
        
        for word, flag in words:
            if flag in self.person_flags:
                persons.append(word)
            elif flag in self.adjective_flags:
                adjectives.append(word)
        
        return persons, adjectives
    
    def extract_dialogues_with_context(self, lines: List[str]) -> List[Dict[str, Any]]:
        """提取对话及其上下文信息"""
        dialogues_data = []
        dialogue_pattern = r'([^"“”]*)(["“])([^"”]*)(["”])'
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # 查找所有对话
            matches = re.findall(dialogue_pattern, line)
            if not matches:
                continue
                
            for match in matches:
                prefix, quote_start, dialogue_content, quote_end = match
                # 提取说话者信息
                speaker_match = re.search(r'([\u4e00-\u9fa5]{2,4})[说问喊叫叹答回]', prefix)
                speaker = speaker_match.group(1) if speaker_match else "未知"
                
                # 提取情感词和人物
                persons, adjectives = self.find_name_adjective(prefix)
                
                dialogues_data.append({
                    'line_number': line_num,
                    'speaker': speaker,
                    'character': persons,
                    'emotion': adjectives,
                    'dialogue': dialogue_content,
                    'context': prefix.strip(),
                    'full_text': line
                })
        
        return dialogues_data
    
    def is_tang_san_dialogue(self, dialogue_data: Dict[str, Any]) -> bool:
        """判断是否为唐三的对话"""
        # 直接说话者是唐三
        if dialogue_data['speaker'] == '唐三':
            return True
        
        # 上下文中提到唐三且频率最高
        if '唐三' in dialogue_data['character']:
            char_counter = Counter(dialogue_data['character'])
            if char_counter.most_common(1)[0][0] == '唐三':
                return True
        
        return False
    
    def create_conversation_pairs(self, dialogues_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """创建对话对"""
        conversation_pairs = []
        tangsan_system = "你是唐三，前世为唐门外门弟子，因偷学内门绝技《玄天宝录》而自杀谢罪，穿越至斗罗大陆。你是万年不遇的双生武魂拥有者（昊天锤、蓝银皇），未来的海神与修罗神双神位继承者。你性格沉稳坚毅、睿智冷静、极其重情重义，尤其深爱小舞，愿为她付出一切。你秉持'人不犯我，我不犯人；人若犯我，步步逼人'的准则。你精通唐门绝学（玄玉手、紫极魔瞳、暗器百解等），擅长在战斗中使用智慧和技巧。"
        
        # 按行号排序
        dialogues_data.sort(key=lambda x: x['line_number'])
        
        # 创建对话对
        for i in range(1, len(dialogues_data)):
            current = dialogues_data[i]
            previous = dialogues_data[i - 1]
            
            # 确保当前对话是唐三的
            if self.is_tang_san_dialogue(current):
                # 检查对话对是否合理（避免跨章节的不相关对话）
                if abs(current['line_number'] - previous['line_number']) <= 5:  # 最多相隔5行
                    conversation_pair = {
                        "messages": [
                            {
                                "system": tangsan_system,
                                "input": previous['dialogue'],
                                "output": current['dialogue'],
                                "metadata": {
                                    "previous_speaker": previous['speaker'],
                                    "current_speaker": current['speaker'],
                                    "line_numbers": f"{previous['line_number']}-{current['line_number']}",
                                    "emotion": current['emotion']
                                }
                            }
                        ]
                    }
                    conversation_pairs.append(conversation_pair)
        
        return conversation_pairs
    
    def process_directory(self, input_dir: str, output_dir: str):
        """处理整个目录的文件"""
        all_conversations = []
        
        # 获取所有txt文件
        txt_files = [f for f in os.listdir(input_dir) 
                    if f.endswith('.txt') and os.path.isfile(os.path.join(input_dir, f))]
        
        print(f"找到 {len(txt_files)} 个文件需要处理")
        
        for file_name in txt_files:
            file_path = os.path.join(input_dir, file_name)
            print(f"处理文件: {file_name}")
            
            lines = self.read_data(file_path)
            if not lines:
                continue
                
            dialogues_data = self.extract_dialogues_with_context(lines)
            conversation_pairs = self.create_conversation_pairs(dialogues_data)
            
            all_conversations.extend(conversation_pairs)
            
            # 可选：为每个文件保存单独的结果
            if conversation_pairs:
                base_name = os.path.splitext(file_name)[0]
                output_file = os.path.join(output_dir, f"{base_name}_conversations.json")
                self.save_conversations(conversation_pairs, output_file)
        
        # 保存所有对话对
        if all_conversations:
            final_output = os.path.join(output_dir, "all_conversations.json")
            self.save_conversations(all_conversations, final_output)
            print(f"总共提取了 {len(all_conversations)} 个对话对")
        
        return all_conversations
    
    def save_conversations(self, conversations: List[Dict[str, Any]], output_path: str):
        """保存对话数据"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
        
        print(f"对话数据已保存到: {output_path}")

def main():
    # 初始化处理器
    processor = DialogueProcessor(r"E:\论文\代码\数据处理\my_dict.txt")
    
    # 设置路径
    train_data_path = r"E:\论文\代码\数据处理\NonEmptyData"
    output_path = r"E:\论文\代码\数据处理\output"
    
    # 处理所有文件
    all_conversations = processor.process_directory(train_data_path, output_path)
    
    # 打印示例
    if all_conversations:
        print("\n前3个对话对示例:")
        for i, conv in enumerate(all_conversations[:3]):
            print(f"对话对 {i + 1}:")
            msg = conv["messages"][0]
            print(f"  输入: {msg['input']}")
            print(f"  输出: {msg['output']}")
            print(f"  元数据: {msg['metadata']}")
            print()

if __name__ == "__main__":
    main()