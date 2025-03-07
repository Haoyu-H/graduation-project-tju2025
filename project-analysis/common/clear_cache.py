import os
import shutil

def remove_pycache(directory):
    """
    删除指定目录及子目录中的所有 __pycache__ 文件夹。
    """
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    print(f"已删除: {dir_path}")
                except Exception as e:
                    print(f"无法删除 {dir_path}: {e}")

if __name__ == "__main__":
    project_path = os.getcwd()  # 获取当前工作目录
    print(f"正在清理 {project_path} 中的 __pycache__ 文件夹...")
    remove_pycache(project_path)
