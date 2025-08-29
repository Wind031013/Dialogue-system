import os

def remove_empty_lines(input_file, output_file):
    #print("当前工作目录:", os.getcwd())
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        non_empty_lines = [line for line in lines if line.strip()]

        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(non_empty_lines)
        print(f"处理完成！已保存到: {output_file}")
        print(f"原始行数: {len(lines)}, 处理后行数: {len(non_empty_lines)}")

    except FileNotFoundError:
        print(f"错误：找不到文件 '{input_file}'")
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}")

if __name__ == "__main__":
    for i in range(1,10):
        input_path = os.getcwd() + r"\数据处理\data\train_" + str(i) + ".txt"
        output_path = os.getcwd() + r"\数据处理\NonEmptyData\train_" + str(i) + ".txt"
        remove_empty_lines(input_path, output_path)
