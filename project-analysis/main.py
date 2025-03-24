# from config import BASE_DATA_PATH, OUTPUT_PATH
# from modules.file_analyzer import FileAnalyzer
# from modules.class_analyzer import ClassAnalyzer
# from modules.method_analyzer import MethodAnalyzer
# from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
# from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
# import os
# import mysql.connector
# from flask import Flask, render_template_string
# import json

# # MySQL 配置
# mysql_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "123456789",
#     "database": "method_analysis"
# }

# def ensure_database_exists(mysql_config):
#     """
#     如果指定的数据库不存在，则创建数据库（字符集为 utf8mb4)。
#     """
#     config = mysql_config.copy()
#     db_name = config.pop("database")
#     conn = mysql.connector.connect(**config)
#     cursor = conn.cursor()
#     cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
#     conn.commit()
#     cursor.close()
#     conn.close()

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

#         # 3. 方法统计（增加保存到 MySQL 的步骤）
#         method_structure = self.method_analyzer.count_methods(project_path)
#         self.method_analyzer.save_statistics(method_structure, project_name)
#         ensure_database_exists(mysql_config)
#         self.method_analyzer.save_to_mysql(method_structure, project_name, mysql_config)

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
#             self.analyze_project(project_path)

# # Flask 可视化界面（展示方法调用图）
# app = Flask(__name__)

# template = """
# <!DOCTYPE html>
# <html>
# <head>
#   <meta charset="utf-8">
#   <title>Method Call Graph</title>
#   <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
#   <style type="text/css">
#     #mynetwork {
#       width: 100%;
#       height: 800px;
#       border: 1px solid lightgray;
#     }
#   </style>
# </head>
# <body>
#   <h1>Method Call Graph</h1>
#   <div id="mynetwork"></div>
#   <script type="text/javascript">
#     var nodes = new vis.DataSet({{ nodes|safe }});
#     var edges = new vis.DataSet({{ edges|safe }});
#     var container = document.getElementById('mynetwork');
#     var data = {
#       nodes: nodes,
#       edges: edges
#     };
#     var options = {
#       layout: { hierarchical: false },
#       edges: { arrows: { to: true } },
#       physics: { enabled: true }
#     };
#     var network = new vis.Network(container, data, options);
#   </script>
# </body> 
# </html>
# """

# @app.route('/graph')
# def graph():
#     """
#     查询 MySQL 数据库中所有方法统计数据，构建节点与边，并渲染交互式图形界面。
#     """
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     cursor.execute("SELECT defined_method, called_methods FROM method_statistics")
#     rows = cursor.fetchall()
#     cursor.close()
#     conn.close()

#     nodes_set = set()
#     edges = []
#     for defined_method, called_methods_json in rows:
#         nodes_set.add(defined_method)
#         try:
#             called_methods = json.loads(called_methods_json)
#         except Exception:
#             called_methods = []
#         for cm in called_methods:
#             nodes_set.add(cm)
#             edges.append({"from": defined_method, "to": cm})
#     nodes = [{"id": node, "label": node} for node in nodes_set]
#     return render_template_string(template, nodes=json.dumps(nodes), edges=json.dumps(edges))

# if __name__ == "__main__":
#     # 运行项目分析任务
#     analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
#     analysis.run()

#     # 分析完成后启动 Flask 可视化服务
#     print("启动 Flask 可视化服务，访问地址: http://0.0.0.0:5000/graph")
#     app.run(host="0.0.0.0", port=5000)

# from config import BASE_DATA_PATH, OUTPUT_PATH
# from modules.file_analyzer import FileAnalyzer
# from modules.class_analyzer import ClassAnalyzer
# from modules.method_analyzer import MethodAnalyzer
# from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
# from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
# import os
# import mysql.connector
# from flask import Flask, render_template_string, request
# import json
# import re

# # MySQL 配置
# mysql_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "123456789",
#     "database": "method_analysis"
# }

# def ensure_database_exists(mysql_config):
#     """
#     如果指定的数据库不存在，则创建数据库（字符集为 utf8mb4)。
#     """
#     config = mysql_config.copy()
#     db_name = config.pop("database")
#     conn = mysql.connector.connect(**config)
#     cursor = conn.cursor()
#     cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
#     conn.commit()
#     cursor.close()
#     conn.close()

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

#         # 3. 方法统计（增加保存到 MySQL 的步骤）
#         method_structure = self.method_analyzer.count_methods(project_path)
#         self.method_analyzer.save_statistics(method_structure, project_name)
#         ensure_database_exists(mysql_config)
#         self.method_analyzer.save_to_mysql(method_structure, project_name, mysql_config)

#         # 4. 注释、代码和其他行统计
#         line_counts = self.comment_code_analyzer.analyze_lines(project_path)
#         self.comment_code_analyzer.save_statistics(line_counts, project_name)
#         self.comment_code_analyzer.save_comment_statistics(line_counts, project_name)

#         # # 5. 函数调用关系分析
#         # call_graph = self.call_graph_analyzer.extract_call_graph(project_path)
#         # self.call_graph_analyzer.save_call_graph(call_graph, project_name)
#         # self.call_graph_analyzer.visualize_graph(project_name)  # 显示调用图

#     def run(self):
#         """
#         运行所有项目的分析任务。
#         """
#         projects = self.scan_projects()  # 获取所有子目录作为项目路径
#         for project_path in projects:
#             self.analyze_project(project_path)

# # Flask 可视化界面（展示方法调用图）
# app = Flask(__name__)

# template = """
# <!DOCTYPE html>
# <html>
# <head>
#   <meta charset="utf-8">
#   <title>Method Call Graph</title>
#   <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
#   <style type="text/css">
#     #mynetwork {
#       width: 100%;
#       height: 1000px;
#       border: 1px solid lightgray;
#     }
#   </style>
# </head>
# <body>
#   <h1>Method Call Graph</h1>
#   <form method="get" action="/graph">
#     <label for="project">选择项目:</label>
#     <select name="project" id="project" onchange="this.form.submit()">
#       {% for project in projects %}
#       <option value="{{ project }}" {% if project == selected_project %}selected{% endif %}>{{ project }}</option>
#       {% endfor %}
#     </select>
#   </form>
#   <div id="mynetwork"></div>
#   <script type="text/javascript">
#     var nodes = new vis.DataSet({{ nodes|safe }});
#     var edges = new vis.DataSet({{ edges|safe }});
#     var container = document.getElementById('mynetwork');
#     var data = {
#       nodes: nodes,
#       edges: edges
#     };
#     var options = {
#       layout: { hierarchical: false },
#       edges: { arrows: { to: true } },
#       physics: { enabled: true }
#     };
#     var network = new vis.Network(container, data, options);
#   </script>
# </body> 
# </html>
# """

# @app.route('/graph', methods=["GET"])
# def graph():
#     """
#     查询 MySQL 数据库中指定项目的方法统计数据，构建节点与边，并渲染交互式图形界面。
#     同时提供下拉框供用户选择不同项目。
#     """
#     selected_project = request.args.get("project", None)

#     # 查询所有项目对应的表（表名格式为 method_statistics_{project}）
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_name LIKE 'method_statistics\\_%'", (mysql_config["database"],))
#     project_tables = cursor.fetchall()
#     projects = [table[0].replace("method_statistics_", "") for table in project_tables]
#     projects.sort()

#     # 如果未选择项目，默认选择第一个项目
#     if not selected_project and projects:
#         selected_project = projects[0]

#     nodes_set = set()
#     edges = []
#     if selected_project:
#         # 构造表名，注意防止 SQL 注入
#         table_name = f"method_statistics_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
#         query = f"SELECT defined_method, called_methods FROM {table_name}"
#         try:
#             cursor.execute(query)
#             rows = cursor.fetchall()
#             for defined_method, called_methods_json in rows:
#                 nodes_set.add(defined_method)
#                 try:
#                     called_methods = json.loads(called_methods_json)
#                 except Exception:
#                     called_methods = []
#                 for cm in called_methods:
#                     nodes_set.add(cm)
#                     edges.append({"from": defined_method, "to": cm})
#         except Exception as e:
#             print(f"Error querying table {table_name}: {e}")
#     cursor.close()
#     conn.close()
#     nodes = [{"id": node, "label": node} for node in nodes_set]
#     return render_template_string(template, nodes=json.dumps(nodes), edges=json.dumps(edges), projects=projects, selected_project=selected_project)

# if __name__ == "__main__":
#     # 运行项目分析任务
#     analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
#     analysis.run()

#     # 分析完成后启动 Flask 可视化服务
#     print("启动 Flask 可视化服务，访问地址: http://0.0.0.0:5000/graph")
#     app.run(host="0.0.0.0", port=5000)


# main_app.py
# from config import BASE_DATA_PATH, OUTPUT_PATH
# from modules.file_analyzer import FileAnalyzer
# from modules.class_analyzer import ClassAnalyzer
# from modules.method_analyzer import MethodAnalyzer
# from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
# from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
# import os
# import mysql.connector
# from flask import Flask, render_template_string, request, jsonify
# import json
# import re

# # MySQL 配置
# mysql_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "123456789",
#     "database": "method_analysis"
# }

# def ensure_database_exists(mysql_config):
#     """
#     如果指定的数据库不存在，则创建数据库（字符集为 utf8mb4)。
#     """
#     config = mysql_config.copy()
#     db_name = config.pop("database")
#     conn = mysql.connector.connect(**config)
#     cursor = conn.cursor()
#     cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
#     conn.commit()
#     cursor.close()
#     conn.close()

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
#         )
#         self.call_graph_analyzer = CallGraphAnalyzer(output_path)

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
#         project_name = os.path.basename(project_path)
#         print(f"开始分析项目: {project_name}")

#         # 1. 文件类型统计
#         file_stats = self.file_analyzer.count_file_types(project_path)
#         self.file_analyzer.save_statistics(file_stats, project_name)
#         self.file_analyzer.visualize_statistics(file_stats, project_name)

#         # 2. 类统计
#         class_count = self.class_analyzer.count_classes(project_path)
#         self.class_analyzer.save_statistics(class_count, project_name)

#         # 3. 方法统计（保存到 MySQL，并生成 JSON 文件记录热门方法）
#         method_structure = self.method_analyzer.count_methods(project_path)
#         self.method_analyzer.save_to_mysql(method_structure, project_name, mysql_config)
#         self.method_analyzer.save_statistics(method_structure, project_name)

#         # 4. 注释、代码行统计
#         line_counts = self.comment_code_analyzer.analyze_lines(project_path)
#         self.comment_code_analyzer.save_statistics(line_counts, project_name)
#         self.comment_code_analyzer.save_comment_statistics(line_counts, project_name)

#     def run(self):
#         """
#         运行所有项目的分析任务。
#         """
#         projects = self.scan_projects()
#         for project_path in projects:
#             self.analyze_project(project_path)

# # Flask 可视化界面（展示方法调用图、热门方法查询与查看源码功能）
# app = Flask(__name__)

# template = """
# <!DOCTYPE html>
# <html lang="zh-CN">
# <head>
#   <meta charset="utf-8">
#   <title>源代码方法调用图与热门方法查询</title>
#   <!-- 引入 Bootstrap（简约风格） -->
#   <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
#   <style>
#     body { background-color: #fff; color: #333; }
#     .btn { border-radius: 0; }
#     #mynetwork { width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 4px; }
#     #loadMore { margin-top: 10px; }
#     .top-methods { margin-top: 20px; }
#     .top-node { background-color: #ff6666 !important; border: 2px solid #ff0000 !important; font-weight: bold; }
#     .collapse-content { background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 5px; }
#   </style>
#   <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
#   <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
#   <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
#   <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
# </head>
# <body>
#   <div class="container mt-4">
#     <h1 class="mb-4">源代码方法调用图与热门方法查询</h1>
#     <div class="form-group">
#       <label for="projectSelect">选择项目:</label>
#       <select class="form-control" id="projectSelect" onchange="onProjectChange()">
#         {% for project in projects %}
#         <option value="{{ project }}" {% if project == selected_project %}selected{% endif %}>{{ project }}</option>
#         {% endfor %}
#       </select>
#     </div>
#     <div class="row">
#       <!-- 方法调用图区域 -->
#       <div class="col-md-8">
#         <h3>方法调用图</h3>
#         <div id="mynetwork"></div>
#         <button class="btn btn-primary" id="loadMore">加载更多</button>
#       </div>
#       <!-- 热门方法查询区域 -->
#       <div class="col-md-4">
#         <h3>前十热门方法</h3>
#         <ul class="list-group top-methods" id="topMethodsList"></ul>
#       </div>
#     </div>
#   </div>
#   <script type="text/javascript">
#     var nodes = new vis.DataSet([]);
#     var edges = new vis.DataSet([]);
#     var container = document.getElementById('mynetwork');
#     var data = { nodes: nodes, edges: edges };
#     var options = { layout: { hierarchical: false }, edges: { arrows: { to: true } }, physics: { enabled: true } };
#     var network = new vis.Network(container, data, options);

#     var currentPage = 0, pageSize = 100;
#     var selectedProject = "{{ selected_project }}";
#     var allLoaded = false;
#     // 全局存储热门方法名称列表
#     var topMethodNames = [];

#     function loadGraphData(page) {
#       if (allLoaded) {
#         alert("已经完全加载某项目的源代码方法调用图");
#         return;
#       }
#       var xhr = new XMLHttpRequest();
#       xhr.open("GET", "/graph_data?project=" + encodeURIComponent(selectedProject) + "&page=" + page, true);
#       xhr.onreadystatechange = function() {
#         if (xhr.readyState === 4 && xhr.status === 200) {
#           var resp = JSON.parse(xhr.responseText);
#           resp.nodes.forEach(function(node) {
#             if (!nodes.get(node.id)) {
#               if (topMethodNames.indexOf(node.id) !== -1) {
#                 node.color = { background: '#ff6666', border: '#ff0000' };
#               }
#               nodes.add(node);
#             }
#           });
#           resp.edges.forEach(function(edge) { edges.add(edge); });
#           if (!resp.has_more) {
#             allLoaded = true;
#             document.getElementById("loadMore").innerText = "加载更多";
#           }
#         }
#       };
#       xhr.send();
#     }

#     function applyTopMethodColors() {
#       nodes.forEach(function(node) {
#         if (topMethodNames.indexOf(node.id) !== -1) {
#           nodes.update({ id: node.id, color: { background: '#ff6666', border: '#ff0000' } });
#         }
#       });
#     }

#     function loadTopMethods() {
#       var xhr = new XMLHttpRequest();
#       xhr.open("GET", "/top_methods?project=" + encodeURIComponent(selectedProject), true);
#       xhr.onreadystatechange = function() {
#         if (xhr.readyState === 4 && xhr.status === 200) {
#           var topMethods = JSON.parse(xhr.responseText);
#           topMethodNames = [];
#           var list = document.getElementById("topMethodsList");
#           list.innerHTML = "";
#           topMethods.forEach(function(item, index) {
#             topMethodNames.push(item.method);
#             var collapseCallersId = "collapseCallers" + index;
#             var collapseSourceId = "collapseSource" + index;
#             var li = document.createElement("li");
#             li.className = "list-group-item";
#             li.innerHTML = "<strong>" + item.method + "</strong> (" + item.count + " 次调用) " +
#               "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseCallersId + "' role='button' aria-expanded='false' aria-controls='" + collapseCallersId + "'>查看调用者</a> " +
#               "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseSourceId + "' role='button' aria-expanded='false' aria-controls='" + collapseSourceId + "'>查看源码</a>" +
#               "<div class='collapse' id='" + collapseCallersId + "'><div class='collapse-content'>调用者: " + (item.callers.join(", ") || "无") + "</div></div>" +
#               "<div class='collapse' id='" + collapseSourceId + "'><div class='collapse-content' id='source_" + index + "'>加载中...</div></div>";
#             list.appendChild(li);
#             loadMethodSource(item.method, collapseSourceId, index);
#           });
#           applyTopMethodColors();
#         }
#       };
#       xhr.send();
#     }

#     function loadMethodSource(method, collapseId, index) {
#       var xhr = new XMLHttpRequest();
#       xhr.open("GET", "/method_source?project=" + encodeURIComponent(selectedProject) + "&method=" + encodeURIComponent(method), true);
#       xhr.onreadystatechange = function() {
#         if (xhr.readyState === 4 && xhr.status === 200) {
#           var resp = JSON.parse(xhr.responseText);
#           document.getElementById("source_" + index).innerText = resp.source || "未找到源码";
#         }
#       };
#       xhr.send();
#     }

#     function onProjectChange() {
#       selectedProject = document.getElementById("projectSelect").value;
#       currentPage = 0; allLoaded = false; topMethodNames = [];
#       nodes.clear(); edges.clear();
#       loadGraphData(currentPage); loadTopMethods();
#     }

#     loadGraphData(currentPage);
#     loadTopMethods();

#     document.getElementById("loadMore").addEventListener("click", function() {
#       if (allLoaded) { alert("已经完全加载某项目的源代码方法调用图"); }
#       else { currentPage++; loadGraphData(currentPage); }
#     });
#   </script>
# </body>
# </html>
# """

# @app.route('/graph', methods=["GET"])
# def graph():
#     selected_project = request.args.get("project", None)
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_name LIKE 'method_statistics\\_%'", (mysql_config["database"],))
#     project_tables = cursor.fetchall()
#     projects = [table[0].replace("method_statistics_", "") for table in project_tables]
#     projects.sort()
#     if not selected_project and projects:
#         selected_project = projects[0]
#     cursor.close()
#     conn.close()
#     return render_template_string(template, projects=projects, selected_project=selected_project)

# @app.route('/graph_data', methods=["GET"])
# def graph_data():
#     selected_project = request.args.get("project", None)
#     page = int(request.args.get("page", 0))
#     page_size = 100
#     nodes_set = set()
#     edges = []
#     if selected_project:
#         table_name = f"method_statistics_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
#     else:
#         return jsonify({"nodes": [], "edges": [], "has_more": False})
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     count_query = f"SELECT COUNT(*) FROM {table_name}"
#     cursor.execute(count_query)
#     total_rows = cursor.fetchone()[0]
#     offset = page * page_size
#     query = f"SELECT defined_method, called_methods FROM {table_name} LIMIT %s OFFSET %s"
#     cursor.execute(query, (page_size, offset))
#     rows = cursor.fetchall()
#     for defined_method, called_methods_json in rows:
#         nodes_set.add(defined_method)
#         try:
#             called_methods = json.loads(called_methods_json)
#         except Exception:
#             called_methods = []
#         for cm in called_methods:
#             nodes_set.add(cm)
#             edges.append({"from": defined_method, "to": cm})
#     cursor.close()
#     conn.close()
#     nodes = [{"id": node, "label": node} for node in nodes_set]
#     has_more = offset + page_size < total_rows
#     return jsonify({"nodes": nodes, "edges": edges, "has_more": has_more})

# @app.route('/top_methods', methods=["GET"])
# def top_methods():
#     """
#     查询指定项目中被调用次数最多的前十个方法，
#     并返回每个方法的调用次数、调用者列表及在 JSON 文件中记录的源码信息。
#     这里不使用 JSON 文件中的 top_methods 字段，而是从 method_structure 重新计算。
#     """
#     selected_project = request.args.get("project", None)
#     if not selected_project:
#         return jsonify([])
#     import os
#     json_file = os.path.join(OUTPUT_PATH, selected_project, "method_statistics", "method_statistics.json")
#     if not os.path.exists(json_file):
#         return jsonify([])
#     try:
#         with open(json_file, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         all_methods = []
#         if "method_structure" in data:
#             for cls, cls_info in data["method_structure"].items():
#                 for method, details in cls_info.get("methods", {}).items():
#                     call_count = len(details.get("called_methods", []))
#                     all_methods.append({
#                         "method": method,
#                         "count": call_count,
#                         "source_code": details.get("source_code", ""),
#                         "callers": details.get("called_methods", [])
#                     })
#         top_methods = sorted(all_methods, key=lambda x: x["count"], reverse=True)[:10]
#         return jsonify(top_methods)
#     except Exception as e:
#         print("读取 JSON 文件失败:", e)
#         return jsonify([])

# @app.route('/method_source', methods=["GET"])
# def method_source():
#     selected_project = request.args.get("project", None)
#     method = request.args.get("method", None)
#     if not selected_project or not method:
#         return jsonify({"source": ""})
#     import os
#     json_file = os.path.join(OUTPUT_PATH, selected_project, "method_statistics", "method_statistics.json")
#     if not os.path.exists(json_file):
#         return jsonify({"source": ""})
#     try:
#         with open(json_file, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         # 从 method_structure 中查找该方法的源码（若存在）
#         if "method_structure" in data:
#             for cls, cls_info in data["method_structure"].items():
#                 for m, details in cls_info.get("methods", {}).items():
#                     if m == method:
#                         return jsonify({"source": details.get("source_code", "")})
#         return jsonify({"source": ""})
#     except Exception as e:
#         print("读取 JSON 文件失败:", e)
#         return jsonify({"source": ""})

# if __name__ == "__main__":
#     # 运行项目分析任务
#     analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
#     analysis.run()

#     print("启动 Flask 可视化服务，访问地址: http://0.0.0.0:5000/graph")
#     app.run(host="0.0.0.0", port=5000)

# from config import BASE_DATA_PATH, OUTPUT_PATH
# from modules.file_analyzer import FileAnalyzer
# from modules.class_analyzer import ClassAnalyzer
# from modules.method_analyzer import MethodAnalyzer
# from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
# from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
# import os
# import mysql.connector
# from flask import Flask, render_template_string, request, jsonify
# import json
# import re

# # MySQL 配置
# mysql_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "123456789",
#     "database": "method_analysis"
# }

# def ensure_database_exists(mysql_config):
#     """
#     如果指定的数据库不存在，则创建数据库（字符集为 utf8mb4)。
#     """
#     config = mysql_config.copy()
#     db_name = config.pop("database")
#     conn = mysql.connector.connect(**config)
#     cursor = conn.cursor()
#     cursor.execute(
#         f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()

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
#         )
#         self.call_graph_analyzer = CallGraphAnalyzer(output_path)

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
#         project_name = os.path.basename(project_path)
#         print(f"开始分析项目: {project_name}")

#         # 1. 文件类型统计
#         file_stats = self.file_analyzer.count_file_types(project_path)
#         self.file_analyzer.save_statistics(file_stats, project_name)
#         self.file_analyzer.visualize_statistics(file_stats, project_name)

#         # 2. 类统计
#         class_count = self.class_analyzer.count_classes(project_path)
#         self.class_analyzer.save_statistics(class_count, project_name)

#         # 3. 方法统计（保存到 MySQL，并生成 JSON 文件记录前十热门方法）
#         method_structure = self.method_analyzer.count_methods(project_path)
#         self.method_analyzer.save_to_mysql(method_structure, project_name, mysql_config)
#         self.method_analyzer.save_statistics(method_structure, project_name)

#         # 4. 注释、代码行统计
#         line_counts = self.comment_code_analyzer.analyze_lines(project_path)
#         self.comment_code_analyzer.save_statistics(line_counts, project_name)
#         self.comment_code_analyzer.save_comment_statistics(line_counts, project_name)

#     def run(self):
#         """
#         运行所有项目的分析任务。
#         """
#         projects = self.scan_projects()
#         for project_path in projects:
#             self.analyze_project(project_path)

# # Flask 可视化界面（展示方法调用图、热门方法查询与查看源码功能）
# app = Flask(__name__)

# template = """
# <!DOCTYPE html>
# <html lang="zh-CN">
# <head>
#   <meta charset="utf-8">
#   <title>源代码方法调用图与热门方法查询</title>
#   <!-- 引入 Bootstrap（简约风格） -->
#   <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
#   <style>
#     body { background-color: #fff; color: #333; }
#     .btn { border-radius: 0; }
#     #mynetwork { width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 4px; }
#     #loadMore { margin-top: 10px; }
#     .top-methods { margin-top: 20px; }
#     .top-node { background-color: #ff6666 !important; border: 2px solid #ff0000 !important; font-weight: bold; }
#     .collapse-content { background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 5px; }
#   </style>
#   <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
#   <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
#   <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
#   <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
# </head>
# <body>
#   <div class="container mt-4">
#     <h1 class="mb-4">源代码方法调用图与热门方法查询</h1>
#     <div class="form-group">
#       <label for="projectSelect">选择项目:</label>
#       <select class="form-control" id="projectSelect" onchange="onProjectChange()">
#         {% for project in projects %}
#         <option value="{{ project }}" {% if project == selected_project %}selected{% endif %}>{{ project }}</option>
#         {% endfor %}
#       </select>
#     </div>
#     <div class="row">
#       <!-- 方法调用图区域 -->
#       <div class="col-md-8">
#         <h3>方法调用图</h3>
#         <div id="mynetwork"></div>
#         <button class="btn btn-primary" id="loadMore">加载更多</button>
#       </div>
#       <!-- 热门方法查询区域 -->
#       <div class="col-md-4">
#         <h3>前十热门方法</h3>
#         <ul class="list-group top-methods" id="topMethodsList"></ul>
#       </div>
#     </div>
#   </div>
#   <script type="text/javascript">
#     var nodes = new vis.DataSet([]);
#     var edges = new vis.DataSet([]);
#     var container = document.getElementById('mynetwork');
#     var data = { nodes: nodes, edges: edges };
#     var options = { layout: { hierarchical: false }, edges: { arrows: { to: true } }, physics: { enabled: true } };
#     var network = new vis.Network(container, data, options);

#     var currentPage = 0, pageSize = 100;
#     var selectedProject = "{{ selected_project }}";
#     var allLoaded = false;
#     // 全局存储热门方法名称列表
#     var topMethodNames = [];

#     function loadGraphData(page) {
#       if (allLoaded) {
#         alert("已经完全加载某项目的源代码方法调用图");
#         return;
#       }
#       var xhr = new XMLHttpRequest();
#       xhr.open("GET", "/graph_data?project=" + encodeURIComponent(selectedProject) + "&page=" + page, true);
#       xhr.onreadystatechange = function() {
#         if (xhr.readyState === 4 && xhr.status === 200) {
#           var resp = JSON.parse(xhr.responseText);
#           resp.nodes.forEach(function(node) {
#             if (!nodes.get(node.id)) {
#               if (topMethodNames.indexOf(node.id) !== -1) {
#                 node.color = { background: '#ff6666', border: '#ff0000' };
#               }
#               nodes.add(node);
#             }
#           });
#           resp.edges.forEach(function(edge) { edges.add(edge); });
#           if (!resp.has_more) {
#             allLoaded = true;
#             document.getElementById("loadMore").innerText = "加载更多";
#           }
#         }
#       };
#       xhr.send();
#     }

#     function applyTopMethodColors() {
#       nodes.forEach(function(node) {
#         if (topMethodNames.indexOf(node.id) !== -1) {
#           nodes.update({ id: node.id, color: { background: '#ff6666', border: '#ff0000' } });
#         }
#       });
#     }

#     function loadTopMethods() {
#       var xhr = new XMLHttpRequest();
#       xhr.open("GET", "/top_methods?project=" + encodeURIComponent(selectedProject), true);
#       xhr.onreadystatechange = function() {
#         if (xhr.readyState === 4 && xhr.status === 200) {
#           var topMethods = JSON.parse(xhr.responseText);
#           topMethodNames = [];
#           var list = document.getElementById("topMethodsList");
#           list.innerHTML = "";
#           topMethods.forEach(function(item, index) {
#             topMethodNames.push(item.method);
#             var collapseCallersId = "collapseCallers" + index;
#             var collapseSourceId = "collapseSource" + index;
#             var li = document.createElement("li");
#             li.className = "list-group-item";
#             li.innerHTML = "<strong>" + item.method + "</strong> (" + item.count + " 次调用) " +
#               "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseCallersId + "' role='button' aria-expanded='false' aria-controls='" + collapseCallersId + "'>查看调用者</a> " +
#               "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseSourceId + "' role='button' aria-expanded='false' aria-controls='" + collapseSourceId + "'>查看源码</a>" +
#               "<div class='collapse' id='" + collapseCallersId + "'><div class='collapse-content'>调用者: " + (item.callers.join(", ") || "无") + "</div></div>" +
#               "<div class='collapse' id='" + collapseSourceId + "'><div class='collapse-content' id='source_" + index + "'>加载中...</div></div>";
#             list.appendChild(li);
#             loadMethodSource(item.method, collapseSourceId, index);
#           });
#           applyTopMethodColors();
#         }
#       };
#       xhr.send();
#     }

#     function loadMethodSource(method, collapseId, index) {
#       var xhr = new XMLHttpRequest();
#       xhr.open("GET", "/method_source?project=" + encodeURIComponent(selectedProject) + "&method=" + encodeURIComponent(method), true);
#       xhr.onreadystatechange = function() {
#         if (xhr.readyState === 4 && xhr.status === 200) {
#           var resp = JSON.parse(xhr.responseText);
#           document.getElementById("source_" + index).innerText = resp.source || "未找到源码";
#         }
#       };
#       xhr.send();
#     }

#     function onProjectChange() {
#       selectedProject = document.getElementById("projectSelect").value;
#       currentPage = 0; allLoaded = false; topMethodNames = [];
#       nodes.clear(); edges.clear();
#       loadGraphData(currentPage); loadTopMethods();
#     }

#     loadGraphData(currentPage);
#     loadTopMethods();

#     document.getElementById("loadMore").addEventListener("click", function() {
#       if (allLoaded) { alert("已经完全加载某项目的源代码方法调用图"); }
#       else { currentPage++; loadGraphData(currentPage); }
#     });
#   </script>
# </body>
# </html>
# """

# @app.route('/graph', methods=["GET"])
# def graph():
#     selected_project = request.args.get("project", None)
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_name LIKE 'method_statistics\\_%'", (mysql_config["database"],))
#     project_tables = cursor.fetchall()
#     projects = [table[0].replace("method_statistics_", "") for table in project_tables]
#     projects.sort()
#     if not selected_project and projects:
#         selected_project = projects[0]
#     cursor.close()
#     conn.close()
#     return render_template_string(template, projects=projects, selected_project=selected_project)

# @app.route('/graph_data', methods=["GET"])
# def graph_data():
#     selected_project = request.args.get("project", None)
#     page = int(request.args.get("page", 0))
#     page_size = 100
#     nodes_set = set()
#     edges = []
#     if selected_project:
#         table_name = f"method_statistics_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
#     else:
#         return jsonify({"nodes": [], "edges": [], "has_more": False})
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     count_query = f"SELECT COUNT(*) FROM {table_name}"
#     cursor.execute(count_query)
#     total_rows = cursor.fetchone()[0]
#     offset = page * page_size
#     query = f"SELECT defined_method, called_methods FROM {table_name} LIMIT %s OFFSET %s"
#     cursor.execute(query, (page_size, offset))
#     rows = cursor.fetchall()
#     for defined_method, called_methods_json in rows:
#         nodes_set.add(defined_method)
#         try:
#             called_methods = json.loads(called_methods_json)
#         except Exception:
#             called_methods = []
#         for cm in called_methods:
#             nodes_set.add(cm)
#             edges.append({"from": defined_method, "to": cm})
#     cursor.close()
#     conn.close()
#     nodes = [{"id": node, "label": node} for node in nodes_set]
#     has_more = offset + page_size < total_rows
#     return jsonify({"nodes": nodes, "edges": edges, "has_more": has_more})

# @app.route('/top_methods', methods=["GET"])
# def top_methods():
#     """
#     直接从 method_statistics.json 文件中读取前十热门方法（包含方法名、源码及调用者列表）返回给前端。
#     """
#     selected_project = request.args.get("project", None)
#     if not selected_project:
#         return jsonify([])
#     import os
#     json_file = os.path.join(OUTPUT_PATH, selected_project, "method_statistics", "method_statistics.json")
#     if not os.path.exists(json_file):
#         return jsonify([])
#     try:
#         with open(json_file, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         return jsonify(data.get("top_methods", []))
#     except Exception as e:
#         print("读取 JSON 文件失败:", e)
#         return jsonify([])

# @app.route('/method_source', methods=["GET"])
# def method_source():
#     """
#     根据传入的热门方法名称，从 method_statistics.json 中查找对应方法的源码返回。
#     """
#     selected_project = request.args.get("project", None)
#     method = request.args.get("method", None)
#     if not selected_project or not method:
#         return jsonify({"source": ""})
#     import os
#     json_file = os.path.join(OUTPUT_PATH, selected_project, "method_statistics", "method_statistics.json")
#     if not os.path.exists(json_file):
#         return jsonify({"source": ""})
#     try:
#         with open(json_file, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         top_methods = data.get("top_methods", [])
#         for item in top_methods:
#             if item.get("method") == method:
#                 return jsonify({"source": item.get("source_code", "")})
#         return jsonify({"source": ""})
#     except Exception as e:
#         print("读取 JSON 文件失败:", e)
#         return jsonify({"source": ""})

# if __name__ == "__main__":
#     # 运行项目分析任务
#     analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
#     analysis.run()

#     print("启动 Flask 可视化服务，访问地址: http://0.0.0.0:5000/graph")
#     app.run(host="0.0.0.0", port=5000)

# from config import BASE_DATA_PATH, OUTPUT_PATH
# from modules.file_analyzer import FileAnalyzer
# from modules.class_analyzer import ClassAnalyzer
# from modules.method_analyzer import MethodAnalyzer
# from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
# from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
# import os
# import mysql.connector
# from flask import Flask, render_template_string, request, jsonify
# import json
# import re

# # MySQL 配置
# mysql_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "123456789",
#     "database": "method_analysis"
# }

# def ensure_database_exists(mysql_config):
#     """
#     如果指定的数据库不存在，则创建数据库（字符集为 utf8mb4)。
#     """
#     config = mysql_config.copy()
#     db_name = config.pop("database")
#     conn = mysql.connector.connect(**config)
#     cursor = conn.cursor()
#     cursor.execute(
#         f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()

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
#         )
#         self.call_graph_analyzer = CallGraphAnalyzer(output_path)

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
#         project_name = os.path.basename(project_path)
#         print(f"开始分析项目: {project_name}")

#         # 1. 文件类型统计
#         file_stats = self.file_analyzer.count_file_types(project_path)
#         self.file_analyzer.save_statistics(file_stats, project_name)
#         self.file_analyzer.visualize_statistics(file_stats, project_name)

#         # 2. 类统计
#         class_count = self.class_analyzer.count_classes(project_path)
#         self.class_analyzer.save_statistics(class_count, project_name)

#         # 3. 方法统计（保存到 MySQL，并生成 JSON 文件记录前十热门方法，同时保存到单独数据库表）
#         method_structure = self.method_analyzer.count_methods(project_path)
#         self.method_analyzer.save_to_mysql(method_structure, project_name, mysql_config)
#         top_methods = self.method_analyzer.save_statistics(method_structure, project_name)
#         self.method_analyzer.save_top_methods_to_mysql(top_methods, project_name, mysql_config)

#         # 4. 注释、代码行统计
#         line_counts = self.comment_code_analyzer.analyze_lines(project_path)
#         self.comment_code_analyzer.save_statistics(line_counts, project_name)
#         self.comment_code_analyzer.save_comment_statistics(line_counts, project_name)

#     def run(self):
#         """
#         运行所有项目的分析任务。
#         """
#         projects = self.scan_projects()
#         for project_path in projects:
#             self.analyze_project(project_path)

# # Flask 可视化界面（展示方法调用图、热门方法查询与查看源码功能）
# app = Flask(__name__)

# template = """
# <!DOCTYPE html>
# <html lang="zh-CN">
# <head>
#   <meta charset="utf-8">
#   <title>源代码方法调用图与热门方法查询</title>
#   <!-- 引入 AdminLTE CSS 和 FontAwesome -->
#   <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/css/adminlte.min.css">
#   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
#   <style>
#     .container { width: 80%; margin: 0 auto; }
#     #mynetwork { width: 100%; height: 700px; border: 1px solid #ddd; }
#     .top-methods { margin-top: 20px; }
#     .collapse-content { background-color: #f4f6f9; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 5px; }
#   </style>
# </head>
# <body class="hold-transition sidebar-mini">
# <div class="wrapper">
#   <!-- Content Wrapper. Contains page content -->
#   <div class="content-wrapper" style="margin: 20px;">
#     <!-- Content Header (Page header) -->
#     <section class="content-header">
#       <div class="container-fluid">
#         <h1>源代码方法调用图与热门方法查询</h1>
#       </div>
#     </section>
#     <!-- Main content -->
#     <section class="content">
#       <div class="container-fluid">
#         <!-- Project Selection -->
#         <div class="form-group">
#           <label for="projectSelect">选择项目:</label>
#           <select class="form-control" id="projectSelect" onchange="onProjectChange()">
#             {% for project in projects %}
#             <option value="{{ project }}" {% if project == selected_project %}selected{% endif %}>{{ project }}</option>
#             {% endfor %}
#           </select>
#         </div>
#         <div class="row">
#           <!-- 方法调用图区域 -->
#           <div class="col-md-8">
#             <div class="card">
#               <div class="card-header">
#                 <h3 class="card-title">方法调用图</h3>
#               </div>
#               <div class="card-body">
#                 <div id="mynetwork"></div>
#               </div>
#               <div class="card-footer">
#                 <button class="btn btn-primary" id="loadMore">加载更多</button>
#               </div>
#             </div>
#           </div>
#           <!-- 热门方法查询区域 -->
#           <div class="col-md-4">
#             <div class="card">
#               <div class="card-header">
#                 <h3 class="card-title">前十热门方法</h3>
#               </div>
#               <div class="card-body">
#                 <ul class="list-group top-methods" id="topMethodsList"></ul>
#               </div>
#             </div>
#           </div>
#         </div>
#       </div>
#     </section>
#   </div>
# </div>
# <!-- Scripts -->
# <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
# <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
# <script src="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/js/adminlte.min.js"></script>
# <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
# <script type="text/javascript">
#   var nodes = new vis.DataSet([]);
#   var edges = new vis.DataSet([]);
#   var container = document.getElementById('mynetwork');
#   var data = { nodes: nodes, edges: edges };
#   var options = { layout: { hierarchical: false }, edges: { arrows: { to: true } }, physics: { enabled: true } };
#   var network = new vis.Network(container, data, options);

#   var currentPage = 0, pageSize = 100;
#   var selectedProject = "{{ selected_project }}";
#   var allLoaded = false;
#   var topMethodNames = [];

#   function loadGraphData(page) {
#     if (allLoaded) {
#       alert("已经完全加载某项目的源代码方法调用图");
#       return;
#     }
#     $.get("/graph_data", { project: selectedProject, page: page }, function(resp) {
#       console.log("graph_data:", resp);
#       resp.nodes.forEach(function(node) {
#         if (!nodes.get(node.id)) {
#           if (topMethodNames.indexOf(node.id) !== -1) {
#             node.color = { background: '#ff6666', border: '#ff0000' };
#           }
#           nodes.add(node);
#         }
#       });
#       resp.edges.forEach(function(edge) { edges.add(edge); });
#       if (!resp.has_more) {
#         allLoaded = true;
#         $("#loadMore").text("加载更多");
#       }
#     });
#   }

#   function applyTopMethodColors() {
#     nodes.forEach(function(node) {
#       if (topMethodNames.indexOf(node.id) !== -1) {
#         nodes.update({ id: node.id, color: { background: '#ff6666', border: '#ff0000' } });
#       }
#     });
#   }

#   function loadTopMethods() {
#     $.get("/top_methods", { project: selectedProject }, function(topMethods) {
#       console.log("top_methods:", topMethods);
#       topMethodNames = [];
#       var list = $("#topMethodsList");
#       list.empty();
#       topMethods.forEach(function(item, index) {
#         topMethodNames.push(item.method);
#         var collapseCallersId = "collapseCallers" + index;
#         var collapseSourceId = "collapseSource" + index;
#         var li = $("<li class='list-group-item'></li>");
#         li.html("<strong>" + item.method + "</strong> (" + item.count + " 次调用) " +
#           "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseCallersId + "' role='button' aria-expanded='false' aria-controls='" + collapseCallersId + "'>查看调用者</a> " +
#           "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseSourceId + "' role='button' aria-expanded='false' aria-controls='" + collapseSourceId + "'>查看源码</a>" +
#           "<div class='collapse' id='" + collapseCallersId + "'><div class='collapse-content'>调用者: " + (item.callers.join(", ") || "无") + "</div></div>" +
#           "<div class='collapse' id='" + collapseSourceId + "'><div class='collapse-content' id='source_" + index + "'>加载中...</div></div>"
#         );
#         list.append(li);
#         loadMethodSource(item.method, collapseSourceId, index);
#       });
#       applyTopMethodColors();
#     });
#   }

#   function loadMethodSource(method, collapseId, index) {
#     $.get("/method_source", { project: selectedProject, method: method }, function(resp) {
#       $("#source_" + index).text(resp.source || "未找到源码");
#     });
#   }

#   function onProjectChange() {
#     selectedProject = $("#projectSelect").val();
#     currentPage = 0; allLoaded = false; topMethodNames = [];
#     nodes.clear(); edges.clear();
#     loadGraphData(currentPage); loadTopMethods();
#   }

#   loadGraphData(currentPage);
#   loadTopMethods();

#   $("#loadMore").click(function() {
#     if (allLoaded) {
#       alert("已经完全加载某项目的源代码方法调用图");
#     } else {
#       currentPage++;
#       loadGraphData(currentPage);
#     }
#   });
# </script>
# </body>
# </html>
# """

# @app.route('/graph', methods=["GET"])
# def graph():
#     selected_project = request.args.get("project", None)
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_name LIKE 'method_statistics\\_%'", (mysql_config["database"],))
#     project_tables = cursor.fetchall()
#     projects = [table[0].replace("method_statistics_", "") for table in project_tables]
#     projects.sort()
#     if not selected_project and projects:
#         selected_project = projects[0]
#     cursor.close()
#     conn.close()
#     return render_template_string(template, projects=projects, selected_project=selected_project)

# @app.route('/graph_data', methods=["GET"])
# def graph_data():
#     selected_project = request.args.get("project", None)
#     page = int(request.args.get("page", 0))
#     page_size = 100
#     nodes_set = set()
#     edges = []
#     if selected_project:
#         table_name = f"method_statistics_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
#     else:
#         return jsonify({"nodes": [], "edges": [], "has_more": False})
#     conn = mysql.connector.connect(**mysql_config)
#     cursor = conn.cursor()
#     count_query = f"SELECT COUNT(*) FROM {table_name}"
#     cursor.execute(count_query)
#     total_rows = cursor.fetchone()[0]
#     offset = page * page_size
#     query = f"SELECT defined_method, called_methods FROM {table_name} LIMIT %s OFFSET %s"
#     cursor.execute(query, (page_size, offset))
#     rows = cursor.fetchall()
#     for defined_method, called_methods_json in rows:
#         nodes_set.add(defined_method)
#         try:
#             called_methods = json.loads(called_methods_json)
#         except Exception:
#             called_methods = []
#         for cm in called_methods:
#             nodes_set.add(cm)
#             edges.append({"from": defined_method, "to": cm})
#     cursor.close()
#     conn.close()
#     nodes = [{"id": node, "label": node} for node in nodes_set]
#     has_more = offset + page_size < total_rows
#     return jsonify({"nodes": nodes, "edges": edges, "has_more": has_more})

# @app.route('/top_methods', methods=["GET"])
# def top_methods():
#     """
#     从数据库中读取指定项目的前十热门方法数据，并返回给前端。
#     表名为：top_methods_项目名（非法字符已过滤）
#     """
#     selected_project = request.args.get("project", None)
#     if not selected_project:
#         return jsonify([])
#     table_name = f"top_methods_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
#     try:
#         conn = mysql.connector.connect(**mysql_config)
#         cursor = conn.cursor()
#         query = f"SELECT method, count, source_code, callers FROM {table_name}"
#         cursor.execute(query)
#         rows = cursor.fetchall()
#         result = []
#         for row in rows:
#             method, count, source_code, callers_json = row
#             try:
#                 callers = json.loads(callers_json)
#             except Exception:
#                 callers = []
#             result.append({
#                 "method": method,
#                 "count": count,
#                 "source_code": source_code,
#                 "callers": callers
#             })
#         cursor.close()
#         conn.close()
#         print(f"DEBUG: /top_methods 从数据库读取数据：{result}")
#         return jsonify(result)
#     except Exception as e:
#         print("读取热门方法数据库失败:", e)
#         return jsonify([])

# @app.route('/method_source', methods=["GET"])
# def method_source():
#     """
#     根据传入的热门方法名称，从数据库中查找对应方法的源码返回。
#     """
#     selected_project = request.args.get("project", None)
#     method = request.args.get("method", None)
#     if not selected_project or not method:
#         return jsonify({"source": ""})
#     table_name = f"top_methods_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
#     try:
#         conn = mysql.connector.connect(**mysql_config)
#         cursor = conn.cursor()
#         query = f"SELECT source_code FROM {table_name} WHERE method = %s"
#         cursor.execute(query, (method,))
#         row = cursor.fetchone()
#         cursor.close()
#         conn.close()
#         if row:
#             return jsonify({"source": row[0]})
#         return jsonify({"source": ""})
#     except Exception as e:
#         print("读取方法源码数据库失败:", e)
#         return jsonify({"source": ""})

# if __name__ == "__main__":
#     # 运行项目分析任务
#     analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
#     analysis.run()

#     print("启动 Flask 可视化服务，访问地址: http://0.0.0.0:5000/graph")
#     app.run(host="0.0.0.0", port=5000)

from config import BASE_DATA_PATH, OUTPUT_PATH
from modules.file_analyzer import FileAnalyzer
from modules.class_analyzer import ClassAnalyzer
from modules.method_analyzer import MethodAnalyzer
from modules.comment_code_analyzer import CommentCodeAnalyzer  # 添加 CommentCodeAnalyzer 模块
from modules.call_graph_analyzer import CallGraphAnalyzer  # 添加 CallGraphAnalyzer 模块
from modules.version_update_analyzer import VersionUpdateAnalyzer  # 添加 VersionUpdateAnalyzer 模块
import os
import mysql.connector
from flask import Flask, render_template_string, request, jsonify
import json
import re

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
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
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
        )
        self.call_graph_analyzer = CallGraphAnalyzer(output_path)

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
        执行单个项目的分析任务，包括文件、类、方法、注释代码、以及版本更新分析（Git 提交历史）。
        """
        project_name = os.path.basename(project_path)
        print(f"开始分析项目: {project_name}")

        # 1. 文件类型统计
        file_stats = self.file_analyzer.count_file_types(project_path)
        self.file_analyzer.save_statistics(file_stats, project_name)
        self.file_analyzer.visualize_statistics(file_stats, project_name)

        # 2. 类统计
        class_count = self.class_analyzer.count_classes(project_path)
        self.class_analyzer.save_statistics(class_count, project_name)

        # 3. 方法统计（保存到 MySQL，并生成 JSON 文件记录前十热门方法，同时保存到单独数据库表）
        method_structure = self.method_analyzer.count_methods(project_path)
        self.method_analyzer.save_to_mysql(method_structure, project_name, mysql_config)
        top_methods = self.method_analyzer.save_statistics(method_structure, project_name)
        self.method_analyzer.save_top_methods_to_mysql(top_methods, project_name, mysql_config)

        # 4. 注释、代码行统计
        line_counts = self.comment_code_analyzer.analyze_lines(project_path)
        self.comment_code_analyzer.save_statistics(line_counts, project_name)
        self.comment_code_analyzer.save_comment_statistics(line_counts, project_name)

        # 5. 版本更新分析（针对 Git 项目）
        try:
            # 每个项目在 data 下，假设项目目录同时为 Git 仓库目录
            version_update_analyzer = VersionUpdateAnalyzer(project_path, mysql_config)
            commit_data = version_update_analyzer.analyze()
            if commit_data:
                version_update_analyzer.save_to_mysql(commit_data, project_name)
        except Exception as e:
            print(f"版本更新分析失败: {e}")

    def run(self):
        """
        运行所有项目的分析任务。
        """
        projects = self.scan_projects()
        for project_path in projects:
            self.analyze_project(project_path)

# Flask 可视化界面（展示方法调用图、热门方法查询与查看源码功能）
app = Flask(__name__)

template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>源代码方法调用图与热门方法查询</title>
  <!-- 引入 AdminLTE CSS 和 FontAwesome -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/css/adminlte.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    .container { width: 80%; margin: 0 auto; }
    #mynetwork { width: 100%; height: 700px; border: 1px solid #ddd; }
    .top-methods { margin-top: 20px; }
    .collapse-content { background-color: #f4f6f9; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-top: 5px; }
  </style>
</head>
<body class="hold-transition sidebar-mini">
<div class="wrapper">
  <!-- Content Wrapper. Contains page content -->
  <div class="content-wrapper" style="margin: 20px;">
    <!-- Content Header (Page header) -->
    <section class="content-header">
      <div class="container-fluid">
        <h1>源代码方法调用图与热门方法查询</h1>
      </div>
    </section>
    <!-- Main content -->
    <section class="content">
      <div class="container-fluid">
        <!-- Project Selection -->
        <div class="form-group">
          <label for="projectSelect">选择项目:</label>
          <select class="form-control" id="projectSelect" onchange="onProjectChange()">
            {% for project in projects %}
            <option value="{{ project }}" {% if project == selected_project %}selected{% endif %}>{{ project }}</option>
            {% endfor %}
          </select>
        </div>
        <div class="row">
          <!-- 方法调用图区域 -->
          <div class="col-md-8">
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">方法调用图</h3>
              </div>
              <div class="card-body">
                <div id="mynetwork"></div>
              </div>
              <div class="card-footer">
                <button class="btn btn-primary" id="loadMore">加载更多</button>
              </div>
            </div>
          </div>
          <!-- 热门方法查询区域 -->
          <div class="col-md-4">
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">前十热门方法</h3>
              </div>
              <div class="card-body">
                <ul class="list-group top-methods" id="topMethodsList"></ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</div>
<!-- Scripts -->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/js/adminlte.min.js"></script>
<script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<script type="text/javascript">
  var nodes = new vis.DataSet([]);
  var edges = new vis.DataSet([]);
  var container = document.getElementById('mynetwork');
  var data = { nodes: nodes, edges: edges };
  var options = { layout: { hierarchical: false }, edges: { arrows: { to: true } }, physics: { enabled: true } };
  var network = new vis.Network(container, data, options);

  var currentPage = 0, pageSize = 100;
  var selectedProject = "{{ selected_project }}";
  var allLoaded = false;
  var topMethodNames = [];

  function loadGraphData(page) {
    if (allLoaded) {
      alert("已经完全加载某项目的源代码方法调用图");
      return;
    }
    $.get("/graph_data", { project: selectedProject, page: page }, function(resp) {
      console.log("graph_data:", resp);
      resp.nodes.forEach(function(node) {
        if (!nodes.get(node.id)) {
          if (topMethodNames.indexOf(node.id) !== -1) {
            node.color = { background: '#ff6666', border: '#ff0000' };
          }
          nodes.add(node);
        }
      });
      resp.edges.forEach(function(edge) { edges.add(edge); });
      if (!resp.has_more) {
        allLoaded = true;
        $("#loadMore").text("加载更多");
      }
    });
  }

  function applyTopMethodColors() {
    nodes.forEach(function(node) {
      if (topMethodNames.indexOf(node.id) !== -1) {
        nodes.update({ id: node.id, color: { background: '#ff6666', border: '#ff0000' } });
      }
    });
  }

  function loadTopMethods() {
    $.get("/top_methods", { project: selectedProject }, function(topMethods) {
      console.log("top_methods:", topMethods);
      topMethodNames = [];
      var list = $("#topMethodsList");
      list.empty();
      topMethods.forEach(function(item, index) {
        topMethodNames.push(item.method);
        var collapseCallersId = "collapseCallers" + index;
        var collapseSourceId = "collapseSource" + index;
        var li = $("<li class='list-group-item'></li>");
        li.html("<strong>" + item.method + "</strong> (" + item.count + " 次调用) " +
          "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseCallersId + "' role='button' aria-expanded='false' aria-controls='" + collapseCallersId + "'>查看调用者</a> " +
          "<a class='btn btn-link' data-toggle='collapse' href='#" + collapseSourceId + "' role='button' aria-expanded='false' aria-controls='" + collapseSourceId + "'>查看源码</a>" +
          "<div class='collapse' id='" + collapseCallersId + "'><div class='collapse-content'>调用者: " + (item.callers.join(", ") || "无") + "</div></div>" +
          "<div class='collapse' id='" + collapseSourceId + "'><div class='collapse-content' id='source_" + index + "'>加载中...</div></div>"
        );
        list.append(li);
        loadMethodSource(item.method, collapseSourceId, index);
      });
      applyTopMethodColors();
    });
  }

  function loadMethodSource(method, collapseId, index) {
    $.get("/method_source", { project: selectedProject, method: method }, function(resp) {
      $("#source_" + index).text(resp.source || "未找到源码");
    });
  }

  function onProjectChange() {
    selectedProject = $("#projectSelect").val();
    currentPage = 0; allLoaded = false; topMethodNames = [];
    nodes.clear(); edges.clear();
    loadGraphData(currentPage); loadTopMethods();
  }

  loadGraphData(currentPage);
  loadTopMethods();

  $("#loadMore").click(function() {
    if (allLoaded) {
      alert("已经完全加载某项目的源代码方法调用图");
    } else {
      currentPage++;
      loadGraphData(currentPage);
    }
  });
</script>
</body>
</html>
"""

@app.route('/graph', methods=["GET"])
def graph():
    selected_project = request.args.get("project", None)
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_name LIKE 'method_statistics\\_%'", (mysql_config["database"],))
    project_tables = cursor.fetchall()
    projects = [table[0].replace("method_statistics_", "") for table in project_tables]
    projects.sort()
    if not selected_project and projects:
        selected_project = projects[0]
    cursor.close()
    conn.close()
    return render_template_string(template, projects=projects, selected_project=selected_project)

@app.route('/graph_data', methods=["GET"])
def graph_data():
    selected_project = request.args.get("project", None)
    page = int(request.args.get("page", 0))
    page_size = 100
    nodes_set = set()
    edges = []
    if selected_project:
        table_name = f"method_statistics_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
    else:
        return jsonify({"nodes": [], "edges": [], "has_more": False})
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    count_query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(count_query)
    total_rows = cursor.fetchone()[0]
    offset = page * page_size
    query = f"SELECT defined_method, called_methods FROM {table_name} LIMIT %s OFFSET %s"
    cursor.execute(query, (page_size, offset))
    rows = cursor.fetchall()
    for defined_method, called_methods_json in rows:
        nodes_set.add(defined_method)
        try:
            called_methods = json.loads(called_methods_json)
        except Exception:
            called_methods = []
        for cm in called_methods:
            nodes_set.add(cm)
            edges.append({"from": defined_method, "to": cm})
    cursor.close()
    conn.close()
    nodes = [{"id": node, "label": node} for node in nodes_set]
    has_more = offset + page_size < total_rows
    return jsonify({"nodes": nodes, "edges": edges, "has_more": has_more})

@app.route('/top_methods', methods=["GET"])
def top_methods():
    """
    从数据库中读取指定项目的前十热门方法数据，并返回给前端。
    表名为：top_methods_项目名（非法字符已过滤）
    """
    selected_project = request.args.get("project", None)
    if not selected_project:
        return jsonify([])
    table_name = f"top_methods_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        query = f"SELECT method, count, source_code, callers FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            method, count, source_code, callers_json = row
            try:
                callers = json.loads(callers_json)
            except Exception:
                callers = []
            result.append({
                "method": method,
                "count": count,
                "source_code": source_code,
                "callers": callers
            })
        cursor.close()
        conn.close()
        print(f"DEBUG: /top_methods 从数据库读取数据：{result}")
        return jsonify(result)
    except Exception as e:
        print("读取热门方法数据库失败:", e)
        return jsonify([])

@app.route('/method_source', methods=["GET"])
def method_source():
    """
    根据传入的热门方法名称，从数据库中查找对应方法的源码返回。
    """
    selected_project = request.args.get("project", None)
    method = request.args.get("method", None)
    if not selected_project or not method:
        return jsonify({"source": ""})
    table_name = f"top_methods_{re.sub(r'[^a-zA-Z0-9_]', '', selected_project)}"
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        query = f"SELECT source_code FROM {table_name} WHERE method = %s"
        cursor.execute(query, (method,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return jsonify({"source": row[0]})
        return jsonify({"source": ""})
    except Exception as e:
        print("读取方法源码数据库失败:", e)
        return jsonify({"source": ""})

if __name__ == "__main__":
    # 运行项目分析任务，遍历 BASE_DATA_PATH 下所有项目
    analysis = ProjectAnalysis(BASE_DATA_PATH, OUTPUT_PATH)
    analysis.run()

    print("启动 Flask 可视化服务，访问地址: http://0.0.0.0:5000/graph")
    app.run(host="0.0.0.0", port=5000)
