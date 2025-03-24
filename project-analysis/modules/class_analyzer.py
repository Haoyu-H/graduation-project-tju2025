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
        # 支持更全面的类定义匹配，包括 public、private、protected 等修饰符
        class_pattern = re.compile(
            r'^\s*(?:public\s+|private\s+|protected\s+)?class\s+\w+|^\s*(?:const|let|var)\s+\w+\s*=\s*class\s+\w+'
        )

        # 遍历目录及子目录
        for root, _, files in os.walk(directory):
            for file in files:
                # 只处理指定扩展名的源代码文件
                if file.endswith(('.java', '.py', '.cpp', '.cs', '.js', '.ts', '.go', '.rb', '.php')):
                    file_path = os.path.join(root, file)
                    try:
                        # 自动检测文件编码
                        with open(file_path, 'rb') as f:
                            raw_data = f.read()
                            result = chardet.detect(raw_data)
                            encoding = result['encoding'] if result['encoding'] else 'utf-8'
                        # 使用检测到的编码打开文件，添加 errors='replace' 防止解码错误
                        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
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
        project_dir = os.path.join(self.output_path, project_name)
        class_statistics_dir = os.path.join(project_dir, "class_statistics")
        os.makedirs(class_statistics_dir, exist_ok=True)
        class_stats_output = os.path.join(class_statistics_dir, "class_statistics.json")
        class_stats = {
            "project_name": project_name,
            "class_count": class_count
        }
        try:
            with open(class_stats_output, "w", encoding="utf-8") as f:
                json.dump(class_stats, f, indent=4)
            print(f"类统计结果已保存到: {class_stats_output}")
        except IOError as e:
            print(f"保存类统计结果时发生错误: {e}")
