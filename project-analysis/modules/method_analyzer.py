import os
import re
import json
import chardet  
from collections import defaultdict
from typing import Dict, List, Optional

# class MethodAnalyzer:
#     def __init__(self, output_path: str):
#         self.output_path = output_path

#     def detect_encoding(self, file_path: str) -> str:
#         """
#         检测文件的编码格式，避免因编码问题导致无法读取文件。
#         """
#         try:
#             with open(file_path, 'rb') as f:
#                 raw_data = f.read()
#                 result = chardet.detect(raw_data)
#                 return result['encoding']
#         except Exception as e:
#             print(f"无法检测文件 {file_path} 的编码: {e}")
#             return 'utf-8'  # 默认返回 utf-8 编码


#     def count_methods(self, directory: str) -> int:
#         method_count = 0
        
#         # 按语言分派不同的检测模式
#         patterns = {
#             'java': re.compile(r'^\s*((public|private|protected|static|final|abstract|synchronized|native|transient)\s+)+\s*[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{?'),
#             'py': re.compile(r'^\s*def\s+\w+\s*\(.*\)\s*:'),
#             'cpp': re.compile(r'^\s*((virtual|inline|static)\s+)+\s*[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{?'),
#             'cs': re.compile(r'^\s*((public|private|protected|internal|static|virtual|override)\s+)+\s*[\w<>\[\]]+\s+\w+\s*\([^)]*\)\s*\{?'),
#             'js': re.compile(r'^\s*(function\s+\w+\s*\(.*\)|const\s+\w+\s*=\s*\(.*\)\s*=>|async\s+function\s*\w+)'),
#             'ts': re.compile(r'^\s*(function\s+\w+\s*\(.*\)|const\s+\w+\s*=\s*\(.*\)\s*=>|async\s+function\s*\w+|private\s+\w+\s*\(.*\))'),
#             'go': re.compile(r'^\s*func\s+(\(\s*\w+\s+\*?\w+\s*\)\s*)?\w+\s*\(.*\)'),
#             'rb': re.compile(r'^\s*def\s+(self\.)?\w+\s*(\(.*\))?'),
#             'php': re.compile(r'^\s*(public|private|protected|static|function)\s+function\s+\w+\s*\(.*\)')
#         }

#         for root, _, files in os.walk(directory):
#             for file in files:
#                 ext = os.path.splitext(file)[1][1:]
#                 if ext not in patterns:
#                     continue
                
#                 file_path = os.path.join(root, file)
#                 try:
#                     encoding = self.detect_encoding(file_path)
#                     with open(file_path, 'r', encoding=encoding) as f:
#                         for line in f:
#                             line = line.strip()
#                             # 跳过空行和注释
#                             if not line or line.startswith(('//', '/*', '*', '#', '--')):
#                                 continue
#                             if patterns[ext].search(line):
#                                 method_count += 1
#                 except Exception as e:
#                     print(f"无法读取文件 {file_path}: {e}")

#         return method_count
    
#     def save_statistics(self, method_count: int, project_name: str):
#         """
#         保存方法统计结果到 JSON 文件。
#         """
#         # 为每个项目创建一个独立的文件夹，并在其中创建 method_statistics 子文件夹
#         project_dir = os.path.join(self.output_path, project_name)
#         method_statistics_dir = os.path.join(project_dir, "method_statistics")
        
#         # 创建 method_statistics 子文件夹（如果不存在）
#         os.makedirs(method_statistics_dir, exist_ok=True)

#         # 定义输出文件路径
#         method_stats_output = os.path.join(method_statistics_dir, "method_statistics.json")

#         method_stats = {
#             "project_name": project_name,
#             "method_count": method_count
#         }

#         # 将统计数据保存到文件
#         try:
#             with open(method_stats_output, "w", encoding="utf-8") as f:
#                 json.dump(method_stats, f, indent=4)
#             print(f"方法统计结果已保存到: {method_stats_output}")
#         except IOError as e:
#             print(f"保存方法统计结果时发生错误: {e}")
            
            
# class MethodAnalyzer:
#     def __init__(self, output_path: str):
#         self.output_path = output_path
#         # 定义各语言的关键字集合（简化的常见关键字）
#         self.keywords = {
#             'java': {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'try', 'catch', 'finally', 'return', 'new', 'throw', 'break', 'continue', 'class', 'interface', 'enum', 'void', 'int', 'String'},
#             'py': {'if', 'else', 'elif', 'for', 'while', 'def', 'class', 'return', 'try', 'except', 'finally', 'with', 'raise', 'import', 'from', 'as', 'pass', 'break', 'continue', 'and', 'or', 'not', 'is', 'in', 'lambda'},
#             'cpp': {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'try', 'catch', 'throw', 'return', 'new', 'delete', 'break', 'continue', 'class', 'struct', 'void', 'int', 'bool'},
#             'cs': {'if', 'else', 'for', 'foreach', 'while', 'do', 'switch', 'case', 'try', 'catch', 'finally', 'return', 'new', 'throw', 'break', 'continue', 'class', 'interface', 'enum', 'void', 'int', 'string'},
#             'js': {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'try', 'catch', 'finally', 'return', 'new', 'throw', 'break', 'continue', 'function', 'class', 'this', 'async', 'await'},
#             'ts': {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'try', 'catch', 'finally', 'return', 'new', 'throw', 'break', 'continue', 'function', 'class', 'this', 'async', 'await'},
#             'go': {'if', 'else', 'for', 'switch', 'case', 'func', 'return', 'new', 'make', 'break', 'continue', 'package', 'import', 'struct', 'interface'},
#             'rb': {'if', 'else', 'elsif', 'for', 'while', 'do', 'case', 'when', 'begin', 'rescue', 'ensure', 'return', 'new', 'raise', 'break', 'continue', 'def', 'class', 'module'},
#             'php': {'if', 'else', 'for', 'foreach', 'while', 'do', 'switch', 'case', 'try', 'catch', 'finally', 'return', 'new', 'throw', 'break', 'continue', 'function', 'class', 'interface'}
#         }
#         # 定义各语言的方法调用正则式
#         self.call_patterns = {
#             'java': [
#                 re.compile(r'\b(?!new\b|if\b|for\b|while\b|return\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\bnew\s+([a-zA-Z_]\w*)\s*\(')
#             ],
#             'py': [
#                 re.compile(r'\b(?!if\b|else\b|elif\b|for\b|while\b|return\b|def\b|class\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*)\s*\(')
#             ],
#             'cpp': [
#                 re.compile(r'\b(?!new\b|if\b|for\b|while\b|return\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\bnew\s+([a-zA-Z_]\w*)\s*\(')
#             ],
#             'cs': [
#                 re.compile(r'\b(?!new\b|if\b|for\b|foreach\b|while\b|return\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\bnew\s+([a-zA-Z_]\w*)\s*\(')
#             ],
#             'js': [
#                 re.compile(r'\b(?!new\b|if\b|for\b|while\b|return\b|function\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\bnew\s+([a-zA-Z_]\w*)\s*\(')
#             ],
#             'ts': [
#                 re.compile(r'\b(?!new\b|if\b|for\b|while\b|return\b|function\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\bnew\s+([a-zA-Z_]\w*)\s*\(')
#             ],
#             'go': [
#                 re.compile(r'\b(?!new\b|make\b|if\b|for\b|range\b|return\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*)\s*\(')
#             ],
#             'rb': [
#                 re.compile(r'\b(?!if\b|elsif\b|unless\b|for\b|while\b|return\b|def\b|class\b)([a-zA-Z_]\w*[?!]?)\s*\('),
#                 re.compile(r'\.([a-zA-Z_]\w*[?!]?)\s*\(')
#             ],
#             'php': [
#                 re.compile(r'\b(?!new\b|if\b|foreach\b|for\b|while\b|return\b|function\b)([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'->([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'::([a-zA-Z_]\w*)\s*\('),
#                 re.compile(r'\bnew\s+([a-zA-Z_]\w*)\s*\(')
#             ]
#         }
#         # 各语言的方法定义正则式（带方法名捕获）
#         self.method_patterns = {
#             'java': re.compile(r'^\s*((?:public|private|protected|static|final|abstract|synchronized|native|transient)\s+)*[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{?'),
#             'py': re.compile(r'^\s*def\s+(\w+)\s*\(.*\)\s*:'),
#             'cpp': re.compile(r'^\s*((?:virtual|inline|static)\s+)*[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{?'),
#             'cs': re.compile(r'^\s*((?:public|private|protected|internal|static|virtual|override)\s+)+[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*\{?'),
#             'js': re.compile(r'^\s*(?:function\s+(\w+)\s*\(.*\)|const\s+(\w+)\s*=\s*\(.*\)\s*=>|async\s+function\s*(\w+))'),
#             'ts': re.compile(r'^\s*(?:function\s+(\w+)\s*\(.*\)|const\s+(\w+)\s*=\s*\(.*\)\s*=>|async\s+function\s*(\w+)|private\s+\w+\s+(\w+)\s*\(.*\))'),
#             'go': re.compile(r'^\s*func\s+(?:\(\s*\w+\s+\*?\w+\s*\)\s*)?(\w+)\s*\(.*\)'),
#             'rb': re.compile(r'^\s*def\s+(?:self\.)?(\w+)\s*(?:\(.*\))?'),
#             'php': re.compile(r'^\s*(?:public|private|protected|static|function)\s+function\s+(\w+)\s*\(.*\)')
#         }

#     def detect_encoding(self, file_path: str) -> str:
#         try:
#             with open(file_path, 'rb') as f:
#                 raw_data = f.read()
#                 result = chardet.detect(raw_data)
#                 return result['encoding']
#         except Exception as e:
#             print(f"无法检测文件 {file_path} 的编码: {e}")
#             return 'utf-8'

#     def count_methods(self, directory: str) -> tuple[int, dict]:
#         method_count = 0
#         all_method_calls = defaultdict(list)

#         for root, _, files in os.walk(directory):
#             for file in files:
#                 ext = os.path.splitext(file)[1][1:]
#                 if ext not in self.method_patterns:
#                     continue
#                 file_path = os.path.join(root, file)
#                 current_method = None
#                 method_calls = defaultdict(list)
#                 try:
#                     encoding = self.detect_encoding(file_path)
#                     with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
#                         for line in f:
#                             stripped_line = line.strip()
#                             # 跳过空行和注释
#                             if not stripped_line or stripped_line.startswith(('//', '/*', '*', '#', '--', '"""', "'''")):
#                                 continue
#                             # 检测方法定义
#                             match = self.method_patterns[ext].match(line)
#                             if match:
#                                 # 提取方法名（根据不同的正则组）
#                                 groups = match.groups()
#                                 method_name = next((g for g in groups if g is not None), None)
#                                 if method_name:
#                                     current_method = method_name
#                                     method_count += 1
#                             else:
#                                 if current_method:
#                                     # 处理方法调用
#                                     keywords = self.keywords.get(ext, set())
#                                     for regex in self.call_patterns.get(ext, []):
#                                         matches = regex.findall(line)
#                                         for match_group in matches:
#                                             # 处理可能的多个捕获组
#                                             if isinstance(match_group, tuple):
#                                                 for m in match_group:
#                                                     if m and m not in keywords:
#                                                         method_calls[current_method].append(m)
#                                             else:
#                                                 if match_group and match_group not in keywords:
#                                                     method_calls[current_method].append(m)
#                     # 合并当前文件的调用数据
#                     for method, calls in method_calls.items():
#                         all_method_calls[method].extend(calls)
#                 except Exception as e:
#                     print(f"无法读取文件 {file_path}: {e}")
#         return method_count, dict(all_method_calls)

#     def save_statistics(self, method_count: int, method_calls: dict, project_name: str):
#         project_dir = os.path.join(self.output_path, project_name)
#         method_statistics_dir = os.path.join(project_dir, "method_statistics")
#         os.makedirs(method_statistics_dir, exist_ok=True)
#         method_stats_output = os.path.join(method_statistics_dir, "method_statistics.json")

#         method_stats = {
#             "project_name": project_name,
#             "method_count": method_count,
#             "method_calls": method_calls
#         }

#         try:
#             with open(method_stats_output, "w", encoding="utf-8") as f:
#                 json.dump(method_stats, f, indent=4, ensure_ascii=False)
#             print(f"方法统计结果已保存到: {method_stats_output}")
#         except IOError as e:
#             print(f"保存方法统计结果时发生错误: {e}")           
            
            
            
# class MethodAnalyzer:
#     def __init__(self, output_path: str):
#         self.output_path = output_path

#     def detect_encoding(self, file_path: str) -> str:
#         try:
#             with open(file_path, 'rb') as f:
#                 raw_data = f.read()
#                 result = chardet.detect(raw_data)
#                 return result['encoding']
#         except Exception as e:
#             print(f"无法检测文件 {file_path} 的编码: {e}")
#             return 'utf-8'

#     def count_methods(self, directory: str):
#         method_structure = {}
#         patterns = {
#             'java': {
#                 'class_def': re.compile(r'\bclass\s+(\w+)'),
#                 'method_def': re.compile(r'\b(public|private|protected|static|final|abstract|synchronized|native)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\.(\w+)\s*\(([^)]*)\)')  # 确保匹配 "对象.方法名(参数)"
#             }
#         }

#         for root, _, files in os.walk(directory):
#             for file in files:
#                 ext = os.path.splitext(file)[1][1:]
#                 if ext not in patterns:
#                     continue
                
#                 file_path = os.path.join(root, file)
#                 try:
#                     encoding = self.detect_encoding(file_path)
#                     with open(file_path, 'r', encoding=encoding) as f:
#                         lines = f.readlines()

#                     class_name = None
#                     current_method = None
                    
#                     for line in lines:
#                         line = line.strip()
#                         if not line or line.startswith(('//', '/*', '*', '#', '--')):
#                             continue

#                         # 1. 识别类定义
#                         if match := patterns[ext]['class_def'].search(line):
#                             class_name = match.group(1)
#                             if class_name not in method_structure:
#                                 method_structure[class_name] = {}

#                         # 2. 识别方法定义
#                         if match := patterns[ext]['method_def'].search(line):
#                             method_name = match.group(2)
#                             params = match.group(3)
#                             current_method = f"{class_name}.{method_name}({params})"
#                             if class_name and current_method:
#                                 method_structure[class_name][current_method] = []

#                         # 3. 识别方法调用
#                         elif current_method and (call_match := patterns[ext]['method_call'].search(line)):
#                             caller_object = call_match.group(1)  # 调用者（对象/类名）
#                             method_name = call_match.group(2)  # 方法名
#                             params = call_match.group(3)  # 参数

#                             called_method = f"{caller_object}.{method_name}({params})"

#                             # 过滤掉不属于类的方法调用（比如 `if`, `while`, `return` ）
#                             if caller_object not in {"if", "while", "return", "for", "switch"}:
#                                 method_structure[class_name][current_method].append(called_method)

#                 except Exception as e:
#                     print(f"无法读取文件 {file_path}: {e}")

#         return method_structure
    
#     def save_statistics(self, method_structure: dict, project_name: str):
#         project_dir = os.path.join(self.output_path, project_name)
#         method_statistics_dir = os.path.join(project_dir, "method_statistics")
#         os.makedirs(method_statistics_dir, exist_ok=True)
        
#         method_stats_output = os.path.join(method_statistics_dir, "method_statistics.json")
        
#         try:
#             with open(method_stats_output, "w", encoding="utf-8") as f:
#                 json.dump(method_structure, f, indent=4)
#             print(f"方法统计结果已保存到: {method_stats_output}")
#         except IOError as e:
#             print(f"保存方法统计结果时发生错误: {e}")



#       2025.3.6修改，todo：正确识别类名和方法名，完成关系型数据库的构建
#       数据库表：原方法  调用方法  代码片段  （三个字段）

# class MethodAnalyzer:
#     def __init__(self, output_path: str):
#         self.output_path = output_path

#     def detect_encoding(self, file_path: str) -> str:
#         try:
#             with open(file_path, 'rb') as f:
#                 raw_data = f.read()
#                 result = chardet.detect(raw_data)
#                 return result['encoding']
#         except Exception as e:
#             print(f"无法检测文件 {file_path} 的编码: {e}")
#             return 'utf-8'

#     def count_methods(self, directory: str):
#         method_structure = {}
#         patterns = {
#             'java': {
#                 'class_def': re.compile(r'\bclass\s+(\w+)'),
#                 'method_def': re.compile(r'\b(public|private|protected|static|final|abstract|synchronized|native)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
#             },
#             'py': {
#                 'class_def': re.compile(r'\bclass\s+(\w+)'),
#                 'method_def': re.compile(r'\bdef\s+(\w+)\s*\(([^)]*)\)\s*:'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'cpp': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'\b(?:virtual|static|inline)?\s*[\w<>:]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
#             },
#             'cs': {
#                 'class_def': re.compile(r'\bclass\s+(\w+)'),
#                 'method_def': re.compile(r'\b(public|private|protected|internal|static|virtual|override)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
#             },
#             'js': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'\b(?:function|async function)\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'go': {
#                 'class_def': re.compile(r'type\s+(\w+)\s+struct'),
#                 'method_def': re.compile(r'func\s+\(\w+\s+\*?(\w+)\)\s+(\w+)\s*\(([^)]*)\)'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'kt': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'fun\s+(\w+)\s*\(([^)]*)\)\s*:?\s*[\w<>\[\]]*\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'swift': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'func\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'rb': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'def\s+(\w+)\s*\(([^)]*)\)'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'php': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'function\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'rs': {
#                 'class_def': re.compile(r'struct\s+(\w+)'),
#                 'method_def': re.compile(r'fn\s+(\w+)\s*\(([^)]*)\)\s*->?\s*[\w<>\[\]]*\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'ts': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'\b(?:function|async function)\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             }
#         }

#         for root, _, files in os.walk(directory):
#             for file in files:
#                 ext = os.path.splitext(file)[1][1:]
#                 if ext not in patterns:
#                     continue

#                 file_path = os.path.join(root, file)
#                 try:
#                     encoding = self.detect_encoding(file_path)
#                     with open(file_path, 'r', encoding=encoding) as f:
#                         lines = f.readlines()

#                     class_name = None
#                     current_method = None
#                     method_count = 0
                    

#                     for line in lines:
#                         line = line.strip()
#                         if not line or line.startswith(('//', '/*', '*', '#', '--')):
#                             continue

#                         if match := patterns[ext]['class_def'].search(line):
#                             class_name = match.group(1)
#                             if class_name not in method_structure:
#                                 method_structure[class_name] = {'methods': {}, 'method_count': 0}

#                         if match := patterns[ext]['method_def'].search(line):
#                             # 根据语言类型处理不同的分组
#                             if ext in ['java', 'cs']:
#                                 method_name = match.group(2)
#                                 params = match.group(3)
#                             elif ext == 'go':
#                                 method_name = match.group(2)
#                                 params = match.group(3)
#                             else:
#                                 method_name = match.group(1)
#                                 params = match.group(2)
                            
#                             current_method = f"{class_name}.{method_name}({params})"
#                             if class_name and current_method:
#                                 method_structure[class_name]['methods'][current_method] = []
#                                 method_structure[class_name]['method_count'] += 1

#                         elif current_method and (call_match := patterns[ext]['method_call'].search(line)):
#                             # 处理方法调用，去除参数
#                             method_name = call_match.group(1)
#                             called_method = f"{method_name}()"
#                             if called_method not in method_structure[class_name]['methods'][current_method]:
#                                 method_structure[class_name]['methods'][current_method].append(called_method)

#                 except Exception as e:
#                     print(f"无法读取文件 {file_path}: {e}")

#         return method_structure

#     def save_statistics(self, method_structure: dict, project_name: str):
#         project_dir = os.path.join(self.output_path, project_name)
#         method_statistics_dir = os.path.join(project_dir, "method_statistics")
#         os.makedirs(method_statistics_dir, exist_ok=True)

#         method_stats_output = os.path.join(method_statistics_dir, "method_statistics.json")

#         try:
#             with open(method_stats_output, "w", encoding="utf-8") as f:
#                 json.dump(method_structure, f, indent=4, ensure_ascii=False)
#             print(f"方法统计结果已保存到: {method_stats_output}")
#         except IOError as e:
#             print(f"保存方法统计结果时发生错误: {e}")


# class MethodAnalyzer:
#     def __init__(self, output_path: str):
#         self.output_path = output_path

#     def detect_encoding(self, file_path: str) -> str:
#         try:
#             with open(file_path, 'rb') as f:
#                 raw_data = f.read()
#                 result = chardet.detect(raw_data)
#                 return result['encoding']
#         except Exception as e:
#             print(f"无法检测文件 {file_path} 的编码: {e}")
#             return 'utf-8'

#     def count_methods(self, directory: str):
#         method_structure = {}
#         # 用于记录变量名与类名的映射，如 {"orders": "Orders"}
#         instance_to_class = {}

#         # 定义各语言的正则表达式
#         patterns = {
#             'java': {
#                 'class_def': re.compile(r'\bclass\s+(\w+)'),
#                 'method_def': re.compile(r'\b(public|private|protected|static|final|abstract|synchronized|native)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
#             },
#             'py': {
#                 'class_def': re.compile(r'\bclass\s+(\w+)\s*[:\(]'),
#                 'method_def': re.compile(r'\bdef\s+(\w+)\s*\(([^)]*)\)\s*:'), 
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'cpp': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'\b(?:virtual|static|inline)?\s*[\w<>:]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
#             },
#             'cs': {
#                 'class_def': re.compile(r'\bclass\s+(\w+)'),
#                 'method_def': re.compile(r'\b(public|private|protected|internal|static|virtual|override)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
#             },
#             'js': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 # 支持 ES6 类中不带 function 关键字的方法定义，同时也支持传统写法
#                 'method_def': re.compile(r'^\s*(?:(?:function|async function|static)\s+)?(\w+)\s*\(([^)]*)\)\s*\{'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;?')
#             },
#             'go': {
#                 'class_def': re.compile(r'type\s+(\w+)\s+struct'),
#                 'method_def': re.compile(r'func\s+\(\w+\s+\*?(\w+)\)\s+(\w+)\s*\(([^)]*)\)'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'kt': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'fun\s+(\w+)\s*\(([^)]*)\)\s*:?\s*[\w<>\[\]]*\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'swift': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'func\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'rb': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'def\s+(\w+)\s*\(([^)]*)\)'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'php': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'function\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'rs': {
#                 'class_def': re.compile(r'struct\s+(\w+)'),
#                 'method_def': re.compile(r'fn\s+(\w+)\s*\(([^)]*)\)\s*->?\s*[\w<>\[\]]*\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             },
#             'ts': {
#                 'class_def': re.compile(r'class\s+(\w+)'),
#                 'method_def': re.compile(r'\b(?:function|async function)\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
#                 'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
#             }
#         }

#         # 定义各语言对象实例化的正则表达式
#         instantiation_patterns = {
#             'java': re.compile(r'\b(\w+)\s+(\w+)\s*=\s*new\s+(\w+)\s*\('),  # 例如: Orders orders = new Orders();
#             'py': re.compile(r'\b(\w+)\s*=\s*(\w+)\s*\('),                      # 例如: orders = Orders()
#             'js': re.compile(r'\b(?:let|var|const)\s+(\w+)\s*=\s*new\s+(\w+)\s*\(')  # 例如: let orders = new Orders();
#         }

#         # 通用的带对象调用的方法调用正则，适用于所有语言（结尾的分号为可选）
#         dot_call_pattern = re.compile(r'\b(\w+)\.(\w+)\s*\(([^)]*)\)\s*;?')

#         for root, _, files in os.walk(directory):
#             for file in files:
#                 ext = os.path.splitext(file)[1][1:]
#                 if ext not in patterns:
#                     continue

#                 file_path = os.path.join(root, file)
#                 try:
#                     encoding = self.detect_encoding(file_path)
#                     with open(file_path, 'r', encoding=encoding) as f:
#                         lines = f.readlines()

#                     class_name = None
#                     current_method = None

#                     for line in lines:
#                         line = line.strip()
#                         if not line or line.startswith(('//', '/*', '*', '#', '--')):
#                             continue

#                         # 根据文件类型使用对应的实例化正则检测对象实例化
#                         if ext in instantiation_patterns:
#                             if inst_match := instantiation_patterns[ext].search(line):
#                                 if ext == 'java':
#                                     # 例如: Orders orders = new Orders();
#                                     declared_type = inst_match.group(1)
#                                     var_name = inst_match.group(2)
#                                     instantiated_type = inst_match.group(3)
#                                     instance_to_class[var_name] = instantiated_type
#                                 elif ext == 'py':
#                                     # 例如: orders = Orders()
#                                     var_name = inst_match.group(1)
#                                     possible_class = inst_match.group(2)
#                                     if possible_class and possible_class[0].isupper():
#                                         instance_to_class[var_name] = possible_class
#                                 elif ext == 'js':
#                                     # 例如: let orders = new Orders();
#                                     var_name = inst_match.group(1)
#                                     class_name_inst = inst_match.group(2)
#                                     instance_to_class[var_name] = class_name_inst

#                         # 检测类定义
#                         if match := patterns[ext]['class_def'].search(line):
#                             class_name = match.group(1)
#                             if class_name not in method_structure:
#                                 method_structure[class_name] = {'methods': {}, 'method_count': 0}

#                         # 检测方法定义
#                         if match := patterns[ext]['method_def'].search(line):
#                             if ext in ['java', 'cs']:
#                                 method_name = match.group(2)
#                                 params = match.group(3)
#                             elif ext == 'go':
#                                 method_name = match.group(2)
#                                 params = match.group(3)
#                             else:
#                                 method_name = match.group(1)
#                                 params = match.group(2)
                            
#                             current_method = f"{class_name}.{method_name}({params})"
#                             if class_name and current_method:
#                                 method_structure[class_name]['methods'][current_method] = []
#                                 method_structure[class_name]['method_count'] += 1

#                         # 检测方法调用
#                         elif current_method:
#                             # 优先处理带对象调用的方法，如 orders.setOrderTime(...)
#                             if dot_match := dot_call_pattern.search(line):
#                                 caller = dot_match.group(1)
#                                 method_name = dot_match.group(2)
#                                 # 如果行中含有 new，则排除构造函数调用
#                                 if 'new' in line:
#                                     continue
#                                 if caller in instance_to_class:
#                                     caller_class = instance_to_class[caller]
#                                 else:
#                                     # 若 caller 首字母大写，则可能直接为类名，否则归于当前类
#                                     caller_class = caller if caller[0].isupper() else class_name
#                                 called_method = f"{caller_class}.{method_name}()"
#                                 if called_method not in method_structure[class_name]['methods'][current_method]:
#                                     method_structure[class_name]['methods'][current_method].append(called_method)
#                             # 处理不带点调用的情况，默认归为当前类的方法调用
#                             elif call_match := patterns[ext]['method_call'].search(line):
#                                 if 'new' in line:
#                                     continue
#                                 method_name = call_match.group(1)
#                                 called_method = f"{class_name}.{method_name}()"
#                                 if called_method not in method_structure[class_name]['methods'][current_method]:
#                                     method_structure[class_name]['methods'][current_method].append(called_method)

#                 except Exception as e:
#                     print(f"无法读取文件 {file_path}: {e}")

#         return method_structure

#     def save_statistics(self, method_structure: dict, project_name: str):
#         project_dir = os.path.join(self.output_path, project_name)
#         method_statistics_dir = os.path.join(project_dir, "method_statistics")
#         os.makedirs(method_statistics_dir, exist_ok=True)

#         method_stats_output = os.path.join(method_statistics_dir, "method_statistics.json")

#         try:
#             with open(method_stats_output, "w", encoding="utf-8") as f:
#                 json.dump(method_structure, f, indent=4, ensure_ascii=False)
#             print(f"方法统计结果已保存到: {method_stats_output}")
#         except IOError as e:
#             print(f"保存方法统计结果时发生错误: {e}")

import os
import re
import json
import chardet
import argparse
import mysql.connector
from flask import Flask, render_template_string, request

# ================= MySQL 配置及数据库准备 =================
# 请根据实际情况修改下面的 MySQL 连接参数
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

# ================= 方法调用分析类 =================
class MethodAnalyzer:
    def __init__(self, output_path: str):
        self.output_path = output_path

    def detect_encoding(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            print(f"无法检测文件 {file_path} 的编码: {e}")
            return 'utf-8'

    def count_methods(self, directory: str):
        """
        遍历目录下的源代码文件，根据语言类型使用相应正则表达式，提取：
         - 类定义（用于确定当前所属类）
         - 方法定义（格式如 ClassName.methodName(params))
         - 方法调用（支持对象调用及默认调用）
        返回结果结构示例：
        {
          "OrderServiceImpl": {
              "methods": {
                  "OrderServiceImpl.submitOrder(OrdersSubmitDTO ordersSubmitDTO)": [
                      "OrderServiceImpl.getById()",
                      "OrderServiceImpl.getCityName()",
                      ...
                  ]
              },
              "method_count": 1
          },
          ...
        }
        """
        method_structure = {}
        # 记录变量名与类名的映射，如 {"orders": "Orders"}
        instance_to_class = {}

        # 定义各语言的正则表达式
        patterns = {
            'java': {
                'class_def': re.compile(r'\bclass\s+(\w+)'),
                'method_def': re.compile(r'\b(public|private|protected|static|final|abstract|synchronized|native)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
            },
            'py': {
                'class_def': re.compile(r'\bclass\s+(\w+)\s*[:\(]'),
                'method_def': re.compile(r'\bdef\s+(\w+)\s*\(([^)]*)\)\s*:'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            },
            'cpp': {
                'class_def': re.compile(r'class\s+(\w+)'),
                'method_def': re.compile(r'\b(?:virtual|static|inline)?\s*[\w<>:]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
            },
            'cs': {
                'class_def': re.compile(r'\bclass\s+(\w+)'),
                'method_def': re.compile(r'\b(public|private|protected|internal|static|virtual|override)\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;')
            },
            'js': {
                'class_def': re.compile(r'class\s+(\w+)'),
                # 同时支持 ES6 类中不带 function 关键字的方法定义以及传统写法
                'method_def': re.compile(r'^\s*(?:(?:function|async function|static)\s+)?(\w+)\s*\(([^)]*)\)\s*\{'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*;?')
            },
            'go': {
                'class_def': re.compile(r'type\s+(\w+)\s+struct'),
                'method_def': re.compile(r'func\s+\(\w+\s+\*?(\w+)\)\s+(\w+)\s*\(([^)]*)\)'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            },
            'kt': {
                'class_def': re.compile(r'class\s+(\w+)'),
                'method_def': re.compile(r'fun\s+(\w+)\s*\(([^)]*)\)\s*:?\s*[\w<>\[\]]*\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            },
            'swift': {
                'class_def': re.compile(r'class\s+(\w+)'),
                'method_def': re.compile(r'func\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            },
            'rb': {
                'class_def': re.compile(r'class\s+(\w+)'),
                'method_def': re.compile(r'def\s+(\w+)\s*\(([^)]*)\)'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            },
            'php': {
                'class_def': re.compile(r'class\s+(\w+)'),
                'method_def': re.compile(r'function\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            },
            'rs': {
                'class_def': re.compile(r'struct\s+(\w+)'),
                'method_def': re.compile(r'fn\s+(\w+)\s*\(([^)]*)\)\s*->?\s*[\w<>\[\]]*\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            },
            'ts': {
                'class_def': re.compile(r'class\s+(\w+)'),
                'method_def': re.compile(r'\b(?:function|async function)\s+(\w+)\s*\(([^)]*)\)\s*\{?'),
                'method_call': re.compile(r'\b(\w+)\s*\(([^)]*)\)\s*')
            }
        }

        # 定义各语言对象实例化的正则表达式
        instantiation_patterns = {
            'java': re.compile(r'\b(\w+)\s+(\w+)\s*=\s*new\s+(\w+)\s*\('),  # 例如: Orders orders = new Orders();
            'py': re.compile(r'\b(\w+)\s*=\s*(\w+)\s*\('),                      # 例如: orders = Orders()
            'js': re.compile(r'\b(?:let|var|const)\s+(\w+)\s*=\s*new\s+(\w+)\s*\(')  # 例如: let orders = new Orders();
        }

        # 通用的对象调用正则（结尾分号为可选）
        dot_call_pattern = re.compile(r'\b(\w+)\.(\w+)\s*\(([^)]*)\)\s*;?')

        for root, _, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1][1:]
                if ext not in patterns:
                    continue

                file_path = os.path.join(root, file)
                try:
                    encoding = self.detect_encoding(file_path)
                    with open(file_path, 'r', encoding=encoding) as f:
                        lines = f.readlines()

                    class_name = None
                    current_method = None

                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith(('//', '/*', '*', '#', '--')):
                            continue

                        # 检测对象实例化（用于方法调用中确定调用者所属类）
                        if ext in instantiation_patterns:
                            if inst_match := instantiation_patterns[ext].search(line):
                                if ext == 'java':
                                    declared_type = inst_match.group(1)
                                    var_name = inst_match.group(2)
                                    instantiated_type = inst_match.group(3)
                                    instance_to_class[var_name] = instantiated_type
                                elif ext == 'py':
                                    var_name = inst_match.group(1)
                                    possible_class = inst_match.group(2)
                                    if possible_class and possible_class[0].isupper():
                                        instance_to_class[var_name] = possible_class
                                elif ext == 'js':
                                    var_name = inst_match.group(1)
                                    class_name_inst = inst_match.group(2)
                                    instance_to_class[var_name] = class_name_inst

                        # 检测类定义
                        if match := patterns[ext]['class_def'].search(line):
                            class_name = match.group(1)
                            if class_name not in method_structure:
                                method_structure[class_name] = {'methods': {}, 'method_count': 0}

                        # 检测方法定义
                        if match := patterns[ext]['method_def'].search(line):
                            if ext in ['java', 'cs']:
                                method_name = match.group(2)
                                params = match.group(3)
                            elif ext == 'go':
                                method_name = match.group(2)
                                params = match.group(3)
                            else:
                                method_name = match.group(1)
                                params = match.group(2)
                            
                            current_method = f"{class_name}.{method_name}({params})"
                            if class_name and current_method:
                                method_structure[class_name]['methods'][current_method] = []
                                method_structure[class_name]['method_count'] += 1

                        # 检测方法调用
                        elif current_method:
                            # 处理对象调用，如 orders.setOrderTime(...)
                            if dot_match := dot_call_pattern.search(line):
                                caller = dot_match.group(1)
                                method_name = dot_match.group(2)
                                if 'new' in line:
                                    continue
                                if caller in instance_to_class:
                                    caller_class = instance_to_class[caller]
                                else:
                                    # 如果调用者首字母大写，则认为它为类名，否则归属当前类
                                    caller_class = caller if caller[0].isupper() else class_name
                                called_method = f"{caller_class}.{method_name}()"
                                if called_method not in method_structure[class_name]['methods'][current_method]:
                                    method_structure[class_name]['methods'][current_method].append(called_method)
                            # 处理默认调用（归属当前类）
                            elif call_match := patterns[ext]['method_call'].search(line):
                                if 'new' in line:
                                    continue
                                method_name = call_match.group(1)
                                called_method = f"{class_name}.{method_name}()"
                                if called_method not in method_structure[class_name]['methods'][current_method]:
                                    method_structure[class_name]['methods'][current_method].append(called_method)

                except Exception as e:
                    print(f"无法读取文件 {file_path}: {e}")

        return method_structure

    # def save_to_mysql(self, method_structure: dict, project_name: str, mysql_config: dict):
    #     """
    #     将方法定义与调用方法集合保存到 MySQL 数据库中。
    #     数据表为 method_statistics,字段包括:
    #       - defined_method TEXT NOT NULL
    #       - called_methods TEXT  （保存 JSON 字符串）
    #     """
    #     # 如果数据库不存在，则先创建
    #     ensure_database_exists(mysql_config)
    #     conn = mysql.connector.connect(**mysql_config)
    #     cursor = conn.cursor()

    #     create_table_sql = '''
    #     CREATE TABLE IF NOT EXISTS method_statistics (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         defined_method TEXT NOT NULL,
    #         called_methods TEXT
    #     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    #     '''
    #     cursor.execute(create_table_sql)

    #     # 遍历 method_structure，将数据写入表中
    #     for class_name, class_info in method_structure.items():
    #         for defined_method, called_methods in class_info['methods'].items():
    #             called_methods_json = json.dumps(called_methods, ensure_ascii=False)
    #             insert_sql = '''
    #             INSERT INTO method_statistics (defined_method, called_methods)
    #             VALUES (%s, %s);
    #             '''
    #             cursor.execute(insert_sql, (defined_method, called_methods_json))

    #     conn.commit()
    #     cursor.close()
    #     conn.close()
    #     print("方法统计结果已保存到 MySQL 数据库。")
    
    # 将不同项目的源代码存入不同的 MySQL 表
    def save_to_mysql(self, method_structure: dict, project_name: str, mysql_config: dict):
        """
        将方法定义与调用方法集合保存到 MySQL 数据库中。
        每个项目使用独立的数据表: method_statistics_projectName
        """
        ensure_database_exists(mysql_config)
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # 规范化表名，防止 SQL 注入（去除特殊字符）
        table_name = f"method_statistics_{re.sub(r'[^a-zA-Z0-9_]', '', project_name)}"

        create_table_sql = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            defined_method TEXT NOT NULL,
            called_methods TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        '''
        cursor.execute(create_table_sql)

        # 遍历 method_structure，将数据写入项目的专属表中
        for class_name, class_info in method_structure.items():
            for defined_method, called_methods in class_info['methods'].items():
                called_methods_json = json.dumps(called_methods, ensure_ascii=False)
                insert_sql = f'''
                INSERT INTO {table_name} (defined_method, called_methods)
                VALUES (%s, %s);
                '''
                cursor.execute(insert_sql, (defined_method, called_methods_json))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"方法统计结果已保存到 MySQL 数据库表 {table_name}。")

        
        
    def save_statistics(self, method_structure: dict, project_name: str):
        project_dir = os.path.join(self.output_path, project_name)
        method_statistics_dir = os.path.join(project_dir, "method_statistics")
        os.makedirs(method_statistics_dir, exist_ok=True)

        method_stats_output = os.path.join(method_statistics_dir, "method_statistics.json")

        try:
            with open(method_stats_output, "w", encoding="utf-8") as f:
                json.dump(method_structure, f, indent=4, ensure_ascii=False)
            print(f"方法统计结果已保存到: {method_stats_output}")
        except IOError as e:
            print(f"保存方法统计结果时发生错误: {e}")

# ================= Flask 可视化界面 =================
app = Flask(__name__)

# HTML 模板，使用 vis-network 绘制有向图
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

# @app.route('/graph')
# def graph():
#     """
#     查询 MySQL 数据库中所有方法统计数据，构建节点（所有出现的 method 字符串）与边（从 defined_method 到每个 called_method),
#     并渲染交互式图形界面。
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
@app.route('/graph', methods=['GET'])
def graph():
    """
    根据项目名称查询 MySQL 数据库，渲染对应的调用图。
    """
    project_name = request.args.get('project', '')

    if not project_name:
        return "请提供 project 参数，例如 /graph?project=your_project_name", 400

    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    # 规范化表名
    table_name = f"method_statistics_{re.sub(r'[^a-zA-Z0-9_]', '', project_name)}"

    try:
        cursor.execute(f"SELECT defined_method, called_methods FROM {table_name}")
        rows = cursor.fetchall()
    except mysql.connector.Error:
        cursor.close()
        conn.close()
        return f"项目 {project_name} 不存在或没有数据", 404

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
    return render_template_string(template, nodes=json.dumps(nodes), edges=json.dumps(edges), project_name=project_name)


# ================= 主程序入口 =================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="方法调用统计与交互式图形展示")
    subparsers = parser.add_subparsers(dest='command', help='子命令: analyze 分析代码并写入 MySQL，runserver 启动 Flask 可视化服务')

    # 分析代码并写入 MySQL
    analyze_parser = subparsers.add_parser('analyze', help='分析代码并保存到 MySQL 数据库')
    analyze_parser.add_argument('--src', type=str, required=True, help='待分析的源代码目录')
    analyze_parser.add_argument('--project', type=str, required=True, help='项目名称')
    analyze_parser.add_argument('--output', type=str, default='./output', help='输出目录')

    # 启动 Flask 服务
    runserver_parser = subparsers.add_parser('runserver', help='启动 Flask 服务展示方法调用图')
    runserver_parser.add_argument('--host', type=str, default='0.0.0.0', help='Flask 服务器绑定的主机')
    runserver_parser.add_argument('--port', type=int, default=5000, help='Flask 服务器端口')

    args = parser.parse_args()

    if args.command == 'analyze':
        analyzer = MethodAnalyzer(output_path=args.output)
        method_structure = analyzer.count_methods(args.src)
        analyzer.save_to_mysql(method_structure, args.project, mysql_config)
    elif args.command == 'runserver':
        app.run(host=args.host, port=args.port)
    else:
        parser.print_help()
