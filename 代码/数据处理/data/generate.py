import os

def createTxt(fileName):
    if not os.path.exists(fileName):
        with open(fileName, 'a', encoding='utf-8') as f:
            print(fileName +"文件已创建")
    else:
        print(fileName + "文件已存在")

if __name__ == "__main__":
    for i in range(1, 10):
        createTxt(os.getcwd() + r"\数据处理\data\train_" + str(i) + ".txt")