import os
import re
import json
import chardet

class ClassAnalyzer:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def count_classes(self, directory: str) -> int:
        """
        统计目录及其子目录下所有源文件中的类定义数量。
        """
        class_count = 0
        # 更新正则表达式，支持更全面的类定义匹配，包括 public、private、protected 等修饰符
        class_pattern = re.compile(r'^\s*(?:public\s+|private\s+|protected\s+)?class\s+\w+|^\s*(?:const|let|var)\s+\w+\s*=\s*class\s+\w+')

        # 遍历目录及子目录
        for root, _, files in os.walk(directory):
            for file in files:
                # 只处理源代码文件（可以根据需求调整扩展名）
                if file.endswith(('.java', '.py', '.cpp', '.cs', '.js', '.ts', '.go', '.rb', '.php')):
                    file_path = os.path.join(root, file)
                    try:
                        # 自动检测文件编码
                        with open(file_path, 'rb') as f:  # 以二进制模式读取文件
                            raw_data = f.read()
                            result = chardet.detect(raw_data)  # 检测编码
                            encoding = result['encoding'] if result['encoding'] else 'utf-8'  # 默认使用 utf-8

                        # 使用检测到的编码打开文件
                        with open(file_path, 'r', encoding=encoding) as f:
                            for line in f:
                                if class_pattern.match(line):
                                    class_count += 1
                    except Exception as e:
                        print(f"无法读取文件 {file_path}: {e}")

        return class_count

    def save_statistics(self, class_count: int, project_name: str):
        """
        保存类统计结果到 JSON 文件。
        """
        # 为每个项目创建一个独立的文件夹，保存统计结果
        project_dir = os.path.join(self.output_path, project_name)
        class_statistics_dir = os.path.join(project_dir, "class_statistics")
        
        # 创建 class_statistics 子文件夹（如果不存在）
        os.makedirs(class_statistics_dir, exist_ok=True)

        # 定义输出文件路径
        class_stats_output = os.path.join(class_statistics_dir, "class_statistics.json")

        # 准备要保存的数据
        class_stats = {
            "project_name": project_name,
            "class_count": class_count
        }

        # 将统计数据保存到文件
        try:
            with open(class_stats_output, "w", encoding="utf-8") as f:
                json.dump(class_stats, f, indent=4)
            print(f"类统计结果已保存到: {class_stats_output}")
        except IOError as e:
            print(f"保存类统计结果时发生错误: {e}")
