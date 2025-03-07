import os
import shutil

def clear_output_folder(output_path: str):
    """
    清除 output 文件夹中的所有内容。
    """
    # 检查 output 文件夹是否存在
    if os.path.exists(output_path):
        try:
            # 使用 shutil.rmtree 删除 output 文件夹及其所有内容
            shutil.rmtree(output_path)
            print(f"已成功清除 {output_path} 文件夹中的所有内容。")
        except Exception as e:
            print(f"清除文件夹时发生错误: {e}")
    else:
        print(f"{output_path} 文件夹不存在，无法清除。")

if __name__ == "__main__":
    # 指定 output 文件夹路径
    output_path = "./output" 

    # 调用函数清除 output 文件夹
    clear_output_folder(output_path)
