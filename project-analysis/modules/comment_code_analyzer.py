import os
import re
import json
import chardet
import matplotlib.pyplot as plt
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch


class CommentCodeAnalyzer:
    def __init__(self, output_path: str, model_path: str, tokenizer_path: str):
        self.output_path = output_path
        self.model_path = model_path  # 本地模型路径
        self.tokenizer_path = tokenizer_path  # 本地tokenizer路径
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # 加载本地保存的模型和 tokenizer
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(self.tokenizer_path)

    def detect_encoding(self, file_path: str) -> str:
        """
        检测文件的编码格式。
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding']
        except Exception as e:
            print(f"无法检测文件 {file_path} 的编码: {e}")
            return 'utf-8'

    def classify_comments_batch(self, comments: list) -> list:
        """
        批量分类注释为代码注释或说明注释，结合模型预测与规则调整。
        """
        if not comments:
            return []

        # 使用模型预测初步分类
        inputs = self.tokenizer(comments, return_tensors="pt", padding=True, truncation=True)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=1).cpu().tolist()

        # 模型预测结果
        results = ["code_comment" if pred == 0 else "explanation_comment" for pred in predictions]

        # 进一步规则调整
        for i, comment in enumerate(comments):
            stripped_comment = comment.strip()

            # 如果注释行包含典型的代码结构或特征，调整为 `code_comment`
            if re.search(r'\b(if|else|int|return|for|while|class|def|void|import|public|private|try|catch|finally)\b', stripped_comment, re.IGNORECASE) or \
                re.search(r'[=;{}()\[\]]', stripped_comment):
                results[i] = "code_comment"

            # 如果注释行主要是解释性语言（包括中文），调整为 `explanation_comment`
            elif re.search(r'[^\x00-\x7F]+', stripped_comment):  # 检测中文字符
                results[i] = "explanation_comment"

        # 如果是以 "#" 或 "//" 开头，且不包含代码结构，可能是解释性注释
            elif stripped_comment.startswith(("#", "//")) and not re.search(r'[=;{}()\[\]]', stripped_comment):
                results[i] = "explanation_comment"

        # 多行注释（如 /* ... */）的处理：根据内容决定
            elif stripped_comment.startswith("/*") and stripped_comment.endswith("*/"):
            # 如果内容包含代码特征
                if re.search(r'[=;{}()\[\]]', stripped_comment) or \
                    re.search(r'\b(if|else|int|return|class|def|void)\b', stripped_comment, re.IGNORECASE):
                    results[i] = "code_comment"
                else:
                    results[i] = "explanation_comment"

        return results


    def process_comments_batch(self, comments_batch: list, line_counts: dict):
        """
        处理注释批次，更新代码注释和说明注释的计数。
        """
        if comments_batch:
            results = self.classify_comments_batch(comments_batch)
            for result in results:
                if result == "code_comment":
                    line_counts["code_comment_lines"] += 1
                elif result == "explanation_comment":
                    line_counts["explanation_comment_lines"] += 1
            line_counts["comment_lines"] += len(results)  # 确保注释总行数等于已分类的行数
            comments_batch.clear()


    def analyze_lines(self, directory: str) -> dict:
        """
        统计目录及子目录中文件的代码行数、注释行数和其他行数，同时区分代码注释和说明注释。
        """
        line_counts = {
            "code_lines": 0,
            "comment_lines": 0,
            "other_lines": 0,
            "code_comment_lines": 0,
            "explanation_comment_lines": 0,
        }

        comments_batch = []
        source_file_extensions = ('.java', '.py', '.cpp', '.cs', '.js', '.ts', '.go', '.rb', '.php', '.html')
        valid_code_pattern = re.compile(r'[a-zA-Z0-9_]+|[=;{}()\[\]]')

        for root, _, files in os.walk(directory):
            for file in files:
                file_extension = os.path.splitext(file)[1]
                if file_extension in source_file_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        encoding = self.detect_encoding(file_path)
                        with open(file_path, 'r', encoding=encoding) as f:
                            in_multi_line_comment = False
                            for line in f:
                                stripped_line = line.strip()

                                # HTML 多行注释
                                if file_extension == '.html' and re.search(r'<!--', stripped_line):
                                    in_multi_line_comment = not re.search(r'-->', stripped_line)
                                    line_counts["comment_lines"] += 1
                                    comments_batch.append(stripped_line)

                                # 多行注释处理
                                elif in_multi_line_comment or re.search(r'/\*', stripped_line):
                                    in_multi_line_comment = not re.search(r'\*/', stripped_line)
                                    line_counts["comment_lines"] += 1
                                    comments_batch.append(stripped_line)

                                # 单行注释
                                elif re.search(r'^\s*//|^\s*#', stripped_line):
                                    line_counts["comment_lines"] += 1
                                    comments_batch.append(stripped_line)

                                # 代码行检测
                                elif valid_code_pattern.search(stripped_line):
                                    line_counts["code_lines"] += 1

                                # 其他行
                                else:
                                    line_counts["other_lines"] += 1

                                # 每 32 行批量推理一次
                                if len(comments_batch) >= 32:
                                    self.process_comments_batch(comments_batch, line_counts)

                            # 处理剩余注释
                            self.process_comments_batch(comments_batch, line_counts)

                    except Exception as e:
                        print(f"无法读取文件 {file_path}: {e}")

        # 确保注释分类总和不超过注释总数
        line_counts["comment_lines"] = line_counts["code_comment_lines"] + line_counts["explanation_comment_lines"]

        return line_counts


    def save_statistics(self, line_counts: dict, project_name: str):
        """
        保存注释、代码和其他行统计结果到 JSON 文件，并生成饼状图。
        """
        output_dir = os.path.join(self.output_path, project_name, 'line_statistics', 'codeline_statistics')
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "line_statistics.json")
        try:
            # 保存统计结果到 JSON 文件
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(line_counts, f, indent=4)
            print(f"行数统计结果已保存到: {output_file}")

            # 生成饼状图
            labels = ['Code Lines', 'Comment Lines', 'Other Lines']
            sizes = [line_counts["code_lines"], line_counts["comment_lines"], line_counts["other_lines"]]
            colors = ['#ff9999', '#66b3ff', '#99ff99']  # 自定义颜色
            plt.figure(figsize=(7, 7))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            plt.title(f"Line Statistics for {project_name}")
            plt.axis("equal")  # Equal aspect ratio ensures that pie chart is circular.
            
            # 保存饼状图
            plt.savefig(os.path.join(output_dir, "line_statistics_pie_chart.png"))

        except IOError as e:
            print(f"保存行数统计结果时发生错误: {e}")

    def save_comment_statistics(self, line_counts: dict, project_name: str):
        """
        保存代码注释与说明注释统计结果到 JSON 文件，并绘制饼状图
        """
        output_dir = os.path.join(self.output_path, project_name, 'line_statistics', 'commentline_statistics')
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "comment_statistics.json")
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(line_counts, f, indent=4)
            print(f"注释统计结果已保存到: {output_file}")

            # 饼状图
            labels = ["Code Comments", "Explanation Comments"]
            sizes = [line_counts["code_comment_lines"], line_counts["explanation_comment_lines"]]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.title(f"Comment Type Statistics")
            plt.axis("equal")  
            plt.savefig(os.path.join(output_dir, "comment_statistics_pie_chart.png"))
        except IOError as e:
            print(f"保存注释统计结果时发生错误: {e}")
