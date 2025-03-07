import os
import re
import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
# 设置字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False


class CallGraphAnalyzer:
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.db_path = os.path.join(output_path, "call_graph.db")

        # 初始化数据库
        self._initialize_database()

    def _initialize_database(self):
        """
        初始化数据库以存储节点和边。SQL 脚本来自外部文件。
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 读取 SQL 脚本
        sql_file = os.path.join(self.output_path, "initialize_database.sql")
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()

        # 执行 SQL 脚本
        cursor.executescript(sql_script)

        conn.commit()
        conn.close()

    def analyze_code(self, directory: str):
        """
        遍历目录分析所有源代码文件。
        """
        language_patterns = {
            '.py': self._analyze_python,
            '.java': self._analyze_java,
            '.cpp': self._analyze_cpp,
            '.cs': self._analyze_csharp,
            '.js': self._analyze_javascript,
            '.ts': self._analyze_javascript,
            '.go': self._analyze_go,
            '.rb': self._analyze_ruby
    }

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    ext = os.path.splitext(file)[1]
                    if ext in language_patterns:
                        language_patterns[ext](file_path)
                except Exception as e:
                    print(f"无法分析文件 {file_path}: {e}")
                    


    def _analyze_python(self, file_path: str):
        """
        分析 Python 文件的函数调用关系。
        """
        self._generic_analyze(
            file_path,
            def_pattern=r'^\s*def\s+(\w+)\s*\(.*\):',
            call_pattern=r'(\w+)\s*\(',
            language='Python'
        )

    def _analyze_java(self, file_path: str):
        """
        分析 Java 文件的函数调用关系。
        """
        self._generic_analyze(
            file_path,
            def_pattern=r'^\s*public|private|protected\s+\w+\s+(\w+)\s*\(.*\)',
            call_pattern=r'(\w+)\s*\(',
            language='Java'
        )

    def _analyze_cpp(self, file_path: str):
        """
        分析 C++ 文件的函数调用关系。
        """
        self._generic_analyze(
            file_path,
            def_pattern=r'^\s*\w+\s+(\w+)\s*\(.*\)\s*\{',
            call_pattern=r'(\w+)\s*\(',
            language='C++'
        )

    def _analyze_csharp(self, file_path: str):
        """
        分析 C# 文件的函数调用关系。
        """
        self._generic_analyze(
            file_path,
            def_pattern=r'^\s*(public|private|protected|internal)\s+\w+\s+(\w+)\s*\(.*\)',
            call_pattern=r'(\w+)\s*\(',
            language='C#'
        )

    def _analyze_javascript(self, file_path: str):
        """
        分析 JavaScript/TypeScript 文件的函数调用关系。
        """
        self._generic_analyze(
            file_path,
            def_pattern=r'^\s*function\s+(\w+)\s*\(.*\)',
            call_pattern=r'(\w+)\s*\(',
            language='JavaScript/TypeScript'
        )

    def _analyze_go(self, file_path: str):
        """
        分析 Go 文件的函数调用关系。
        """
        self._generic_analyze(
            file_path,
            def_pattern=r'^\s*func\s+(\w+)\s*\(.*\)',
            call_pattern=r'(\w+)\s*\(',
            language='Go'
        )

    def _analyze_ruby(self, file_path: str):
        """
        分析 Ruby 文件的函数调用关系。
        """
        self._generic_analyze(
            file_path,
            def_pattern=r'^\s*def\s+(\w+)',
            call_pattern=r'(\w+)\s*\(',
            language='Ruby'
        )

    def _generic_analyze(self, file_path: str, def_pattern: str, call_pattern: str, language: str):
        """
        通用的函数定义和调用关系分析。
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_function = None
        functions = {}

        for line in lines:
            line = line.strip()

            # 匹配函数定义
            def_match = re.match(def_pattern, line)
            if def_match:
                current_function = def_match.group(1)
                if current_function not in functions:
                    functions[current_function] = []

            # 匹配函数调用
            if current_function:
                call_matches = re.findall(call_pattern, line)
                for call in call_matches:
                    functions[current_function].append(call)

        # 存储节点和边
        self._store_graph(functions, language)

    def _store_graph(self, functions: dict, language: str):
        """
        存储调用关系到数据库。
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        node_ids = {}
        for function, calls in functions.items():
            cursor.execute("INSERT INTO nodes (name, type, language, tag) VALUES (?, ?, ?, ?)",
                           (function, 'function', language, ''))
            node_ids[function] = cursor.lastrowid

        for function, calls in functions.items():
            source_id = node_ids[function]
            for call in calls:
                target_id = node_ids.get(call)
                if target_id:
                    cursor.execute("INSERT INTO edges (source_id, target_id, relationship) VALUES (?, ?, ?)",
                                   (source_id, target_id, 'calls'))

        conn.commit()
        conn.close()

    def extract_call_graph(self, directory: str) -> dict:
        """
        提取指定目录及其子目录中的函数定义和调用关系。
        """
        functions = {}

        for root, _, files in os.walk(directory):  # 遍历目录及其子目录
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1]  # 获取文件扩展名

                # 根据支持的语言扩展名筛选文件
                if ext in ['.py', '.java', '.cpp', '.cs', '.js', '.ts', '.go', '.rb']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    current_function = None

                    for line in lines:
                        line = line.strip()

                        # 匹配函数定义（通用模式）
                        def_match = re.match(
                            r'^\s*def\s+(\w+)\s*\(.*\)|'
                            r'^\s*(public|private|protected|internal)\s+\w+\s+(\w+)\s*\(.*\)',
                            line
                    )
                        if def_match:
                            current_function = def_match.group(1) or def_match.group(3)
                            if current_function not in functions:
                                functions[current_function] = []

                        # 匹配函数调用（通用模式）
                        if current_function:
                            call_matches = re.findall(r'(\w+)\s*\(', line)
                            for call in call_matches:
                                functions[current_function].append(call)

        return functions

    def save_call_graph(self, call_graph: dict, project_name: str):
        """
        将函数调用关系存储到数据库中。
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 插入项目名作为标签
        project_tag = f"Project: {project_name}"

        node_ids = {}
        for function, calls in call_graph.items():
            # 插入函数节点
            cursor.execute(
                "INSERT INTO nodes (name, type, language, tag) VALUES (?, ?, ?, ?)",
                (function, "function", "unknown", project_tag),
            )
            node_ids[function] = cursor.lastrowid

        for function, calls in call_graph.items():
            source_id = node_ids[function]
            for call in calls:
                target_id = node_ids.get(call)
                if target_id:
                    # 插入调用关系边
                    cursor.execute(
                        "INSERT INTO edges (source_id, target_id, relationship) VALUES (?, ?, ?)",
                        (source_id, target_id, "calls"),
                    )

        conn.commit()
        conn.close()
        
        # 输出保存成功的消息
        print(f"项目 '{project_name}' 的函数调用关系已成功保存到数据库。")

    def visualize_graph(self, project_name: str):
        """
        使用 NetworkX 和 Matplotlib 可视化特定项目的调用图，并将图保存到文件。
        """
        # 清理之前的图表
        plt.clf()  # 清除当前绘图区域
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        G = nx.DiGraph()

        # 查询特定项目的节点和边
        cursor.execute("SELECT id, name FROM nodes WHERE tag LIKE ?", (f"%{project_name}%",))
        nodes = cursor.fetchall()

        for node_id, name in nodes:
            G.add_node(node_id, label=name)

        cursor.execute("""
            SELECT source_id, target_id 
            FROM edges 
            JOIN nodes AS src ON edges.source_id = src.id
            WHERE src.tag LIKE ?
        """, (f"%{project_name}%",))
        edges = cursor.fetchall()

        for source_id, target_id in edges:
            G.add_edge(source_id, target_id)

        conn.close()

        # 绘制图形
        pos = nx.spring_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            labels=nx.get_node_attributes(G, 'label'),
            node_color="skyblue",
            edge_color="gray",
            node_size=1500,
            font_size=10,
        )
        plt.title(f"项目 '{project_name}' 的函数调用图")

        # 保存图像到文件
        output_dir = os.path.join(self.output_path, project_name)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{project_name}_call_graph.png")
        plt.savefig(output_file, format='png', dpi=300)
        print(f"调用图已保存到: {output_file}")

        # plt.show()

