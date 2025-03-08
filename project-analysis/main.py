from config import BASE_DATA_PATH, OUTPUT_PATH
from modules.file_analyzer import FileAnalyzer
from modules.class_analyzer import ClassAnalyzer
from modules.method_analyzer import MethodAnalyzer
from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
import os
import mysql.connector
from flask import Flask, render_template_string
import json

# class ProjectAnalysis:
#     """
#     项目分析主控制器，用于管理和执行项目的分析任务。
#     """
#     def __init__(self, base_path: str, output_path: str):
#         self.base_path = base_path  # 项目根目录路径
#         self.output_path = output_path  # 输出分析结果的存储路径

#         # 初始化各个分析模块
#         self.file_analyzer = FileAnalyzer(output_path)
#         self.class_analyzer = ClassAnalyzer(output_path)
#         self.method_analyzer = MethodAnalyzer(output_path)
#         self.comment_code_analyzer = CommentCodeAnalyzer(
#             output_path, model_path='saved_codebert_model', tokenizer_path='saved_codebert_model'
#         )  # 初始化注释分析器，传递本地路径
#         self.call_graph_analyzer = CallGraphAnalyzer(output_path)  # 初始化函数调用关系分析器

#     def scan_projects(self):
#         """
#         扫描根目录下的所有子目录并返回路径列表。
#         """
#         return [
#             os.path.join(self.base_path, project)
#             for project in os.listdir(self.base_path)
#             if os.path.isdir(os.path.join(self.base_path, project))
#         ]

#     def analyze_project(self, project_path: str):
#         """
#         执行单个项目的分析任务。
#         """
#         project_name = os.path.basename(project_path)  # 获取项目名称
#         print(f"开始分析项目: {project_name}")

#         # 1. 文件类型统计
#         file_stats = self.file_analyzer.count_file_types(project_path)
#         self.file_analyzer.save_statistics(file_stats, project_name)
#         self.file_analyzer.visualize_statistics(file_stats, project_name)

#         # 2. 类统计
#         class_count = self.class_analyzer.count_classes(project_path)
#         self.class_analyzer.save_statistics(class_count, project_name)

#         # 3. 方法统计
#         method_structure = self.method_analyzer.count_methods(project_path)  # 修改为 method_structure
#         self.method_analyzer.save_statistics(method_structure, project_name)  # 传递正确参数

#         # 4. 注释、代码和其他行统计
#         line_counts = self.comment_code_analyzer.analyze_lines(project_path)
#         self.comment_code_analyzer.save_statistics(line_counts, project_name)
#         self.comment_code_analyzer.save_comment_statistics(line_counts, project_name)

#         # 5. 函数调用关系分析
#         call_graph = self.call_graph_analyzer.extract_call_graph(project_path)
#         self.call_graph_analyzer.save_call_graph(call_graph, project_name)
#         self.call_graph_analyzer.visualize_graph(project_name)  # 显示调用图
    
   

#     def run(self):
#         """
#         运行所有项目的分析任务。
#         """
#         projects = self.scan_projects()  # 获取所有子目录作为项目路径
#         for project_path in projects:
#             self.analyze_project(project_path)  # 分析每个项目

# if __name__ == "__main__":
#     # 创建并运行项目分析器
#     analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
#     analysis.run()



# MySQL 配置
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456789",
    "database": "method_analysis"
}

def ensure_database_exists(mysql_config):
    """
    如果指定的数据库不存在，则创建数据库（字符集为 utf8mb4)。
    """
    config = mysql_config.copy()
    db_name = config.pop("database")
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()
    cursor.close()
    conn.close()

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

        # 3. 方法统计（增加保存到 MySQL 的步骤）
        method_structure = self.method_analyzer.count_methods(project_path)
        self.method_analyzer.save_statistics(method_structure, project_name)
        ensure_database_exists(mysql_config)
        self.method_analyzer.save_to_mysql(method_structure, project_name, mysql_config)

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
            self.analyze_project(project_path)

# Flask 可视化界面（展示方法调用图）
app = Flask(__name__)

template = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Method Call Graph</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style type="text/css">
    #mynetwork {
      width: 100%;
      height: 800px;
      border: 1px solid lightgray;
    }
  </style>
</head>
<body>
  <h1>Method Call Graph</h1>
  <div id="mynetwork"></div>
  <script type="text/javascript">
    var nodes = new vis.DataSet({{ nodes|safe }});
    var edges = new vis.DataSet({{ edges|safe }});
    var container = document.getElementById('mynetwork');
    var data = {
      nodes: nodes,
      edges: edges
    };
    var options = {
      layout: { hierarchical: false },
      edges: { arrows: { to: true } },
      physics: { enabled: true }
    };
    var network = new vis.Network(container, data, options);
  </script>
</body> 
</html>
"""

@app.route('/graph')
def graph():
    """
    查询 MySQL 数据库中所有方法统计数据，构建节点与边，并渲染交互式图形界面。
    """
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("SELECT defined_method, called_methods FROM method_statistics")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    nodes_set = set()
    edges = []
    for defined_method, called_methods_json in rows:
        nodes_set.add(defined_method)
        try:
            called_methods = json.loads(called_methods_json)
        except Exception:
            called_methods = []
        for cm in called_methods:
            nodes_set.add(cm)
            edges.append({"from": defined_method, "to": cm})
    nodes = [{"id": node, "label": node} for node in nodes_set]
    return render_template_string(template, nodes=json.dumps(nodes), edges=json.dumps(edges))

if __name__ == "__main__":
    # 运行项目分析任务
    analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
    analysis.run()

    # 分析完成后启动 Flask 可视化服务
    print("启动 Flask 可视化服务，访问地址: http://0.0.0.0:5000/graph")
    app.run(host="0.0.0.0", port=5000)

