from config import BASE_DATA_PATH, OUTPUT_PATH
from modules.file_analyzer import FileAnalyzer
from modules.class_analyzer import ClassAnalyzer
from modules.method_analyzer import MethodAnalyzer
from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
import os

class ProjectAnalysis:
    """
    项目分析主控制器，用于管理和执行项目的分析任务。
    """
    def __init__(self, base_path: str, output_path: str):
        self.base_path = base_path  # 项目根目录路径
        self.output_path = output_path  # 输出分析结果的存储路径

        # 初始化各个分析模块
        self.file_analyzer = FileAnalyzer(output_path)
        self.class_analyzer = ClassAnalyzer(output_path)
        self.method_analyzer = MethodAnalyzer(output_path)
        self.comment_code_analyzer = CommentCodeAnalyzer(
            output_path, model_path='saved_codebert_model', tokenizer_path='saved_codebert_model'
        )  # 初始化注释分析器，传递本地路径
        self.call_graph_analyzer = CallGraphAnalyzer(output_path)  # 初始化函数调用关系分析器

    def scan_projects(self):
        """
        扫描根目录下的所有子目录并返回路径列表。
        """
        return [
            os.path.join(self.base_path, project)
            for project in os.listdir(self.base_path)
            if os.path.isdir(os.path.join(self.base_path, project))
        ]

    def analyze_project(self, project_path: str):
        """
        执行单个项目的分析任务。
        """
        project_name = os.path.basename(project_path)  # 获取项目名称
        print(f"开始分析项目: {project_name}")

        # 1. 文件类型统计
        file_stats = self.file_analyzer.count_file_types(project_path)
        self.file_analyzer.save_statistics(file_stats, project_name)
        self.file_analyzer.visualize_statistics(file_stats, project_name)

        # 2. 类统计
        class_count = self.class_analyzer.count_classes(project_path)
        self.class_analyzer.save_statistics(class_count, project_name)

        # 3. 方法统计
        method_structure = self.method_analyzer.count_methods(project_path)  # 修改为 method_structure
        self.method_analyzer.save_statistics(method_structure, project_name)  # 传递正确参数

        # 4. 注释、代码和其他行统计
        line_counts = self.comment_code_analyzer.analyze_lines(project_path)
        self.comment_code_analyzer.save_statistics(line_counts, project_name)
        self.comment_code_analyzer.save_comment_statistics(line_counts, project_name)

        # 5. 函数调用关系分析
        call_graph = self.call_graph_analyzer.extract_call_graph(project_path)
        self.call_graph_analyzer.save_call_graph(call_graph, project_name)
        self.call_graph_analyzer.visualize_graph(project_name)  # 显示调用图
    
   

    def run(self):
        """
        运行所有项目的分析任务。
        """
        projects = self.scan_projects()  # 获取所有子目录作为项目路径
        for project_path in projects:
            self.analyze_project(project_path)  # 分析每个项目

if __name__ == "__main__":
    # 创建并运行项目分析器
    analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
    analysis.run()
