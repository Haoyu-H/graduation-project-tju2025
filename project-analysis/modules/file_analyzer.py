import os
import json
from collections import defaultdict

class FileAnalyzer:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def count_file_types(self, directory: str) -> dict:
        """
        递归统计指定目录及其子目录下不同类型文件的数量。
        """
        file_type_count = defaultdict(int)

        # 遍历目录及子目录
        for root, _, files in os.walk(directory):
            for file in files:
                file_extension = os.path.splitext(file)[-1].lower()
                if file_extension:
                    file_type_count[file_extension] += 1

        return dict(file_type_count)

    def save_statistics(self, statistics: dict, project_name: str):
        """
        将统计数据保存为 JSON 文件。
        """
        # 为每个项目创建一个独立的文件夹，并在其中创建 file_statistics 子文件夹
        project_dir = os.path.join(self.output_path, project_name)
        file_statistics_dir = os.path.join(project_dir, "file_statistics")
        
        # 创建 file_statistics 子文件夹（如果不存在）
        os.makedirs(file_statistics_dir, exist_ok=True)

        # 定义输出文件路径
        output_file = os.path.join(file_statistics_dir, "file_statistics.json")

        try:
            # 将统计数据保存为 JSON 文件
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(statistics, f, indent=4)
            print(f"文件类型统计结果已保存到: {output_file}")
        except IOError as e:
            print(f"保存文件类型统计结果时发生错误: {e}")

    def visualize_statistics(self, file_statistics: dict, project_name: str):
        """
        使用柱状图可视化文件类型统计结果。
        """
        import matplotlib.pyplot as plt

        if not file_statistics:
            print("没有统计数据可供可视化。")
            return

        labels = list(file_statistics.keys())
        sizes = list(file_statistics.values())

        plt.figure(figsize=(10, 6))
        plt.bar(labels, sizes, color="skyblue")
        plt.xlabel("File Types")
        plt.ylabel("Counts")
        plt.title(f"Filetype Statistics - {project_name}")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # 定义图表输出路径
        file_stats_image_path = os.path.join(self.output_path, project_name, "file_statistics", "file_statistics.png")
        plt.savefig(file_stats_image_path)
        print(f"图表已保存到: {file_stats_image_path}")
        # plt.show()  # 可以选择是否在保存后显示图表

