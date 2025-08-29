import re
import os

def readData(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

import re

def extract_TangSan_dialogues(lines):
    # 改进的正则表达式模式，匹配多种说话方式
    patterns = [
        r'唐三.*?["“](.*?)["”]',
    ]
    all_dialogues = []
    for line in lines:
        for pattern in patterns:
            dialogues = re.findall(pattern, line)
            if dialogues:
                all_dialogues.extend(dialogues)
                print(dialogues)
    return all_dialogues

if __name__ == "__main__":
    file_path = os.getcwd() + r"\数据处理\NonEmptyData\train_1.txt"
    lines = readData(file_path)
    dialogues = extract_TangSan_dialogues(lines)
    #print(lines[8])
    print(dialogues)