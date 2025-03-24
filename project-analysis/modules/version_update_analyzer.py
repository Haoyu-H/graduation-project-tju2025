import os
import re
import json
import chardet
import mysql.connector
import subprocess

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

class VersionUpdateAnalyzer:
    """
    版本更新分析器：
      - 遍历 Git 仓库所有提交，统计每次提交的总代码行数以及变更行数
      - 对于首次提交，变更行数等于总代码行数；
        对于后续提交，通过 git diff --numstat 计算前一个提交与当前提交之间新增与删除的行数之和。
      - 定义“稳定版本”为：项目总代码行数首次达到最终版本（最后一次提交）的 ?
        此时的总代码行数作为稳定版本基准，后续提交中累计变更的代码行数达到该基准一半所用的时间（单位：天）
      - 该时间值存储在稳定版本对应记录的 half_total_time 字段中，其它提交记录该字段为空。
    分析结果将保存到 MySQL 数据库中，每个项目生成独立的表，表名格式为：
      version_updates_{项目名}
    """
    def __init__(self, repo_path: str, mysql_config: dict):
        self.repo_path = repo_path
        self.mysql_config = mysql_config

    def detect_encoding(self, file_path: str) -> str:
        """
        检测文件编码，若检测失败则返回默认编码 utf-8。
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result.get('encoding')
                return encoding if encoding else 'utf-8'
        except Exception as e:
            print(f"无法检测文件 {file_path} 的编码: {e}")
            return 'utf-8'

    def count_lines(self) -> int:
        """
        遍历仓库目录（排除 .git 目录），统计所有文件的代码行数。
        对每个文件先检测编码后再按行统计。
        """
        total_lines = 0
        for root, dirs, files in os.walk(self.repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    encoding = self.detect_encoding(file_path)
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                        lines = f.readlines()
                        total_lines += len(lines)
                except Exception as e:
                    print(f"无法读取文件 {file_path}: {e}")
                    continue
        return total_lines

    def run_git_command(self, args: list) -> str:
        """
        在仓库目录下执行 Git 命令，并返回标准输出结果。
        为避免 Windows 默认编码问题，此处指定编码为 utf-8，遇到解码错误则采用替换模式。
        """
        result = subprocess.run(
            ['git'] + args,
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode != 0:
            raise Exception(f"Git 命令失败: {result.stderr}")
        return (result.stdout or "").strip()

    def get_commit_list(self) -> list:
        """
        获取所有提交记录，每条记录为 (commit_hash, commit_time)，按提交时间正序排列。
        """
        log_output = self.run_git_command(['log', '--reverse', '--pretty=format:%H|%ct'])
        commits = []
        for line in log_output.splitlines():
            parts = line.strip().split('|')
            if len(parts) != 2:
                continue
            commit_hash, commit_time_str = parts
            try:
                commit_time = int(commit_time_str)
            except:
                commit_time = 0
            commits.append((commit_hash, commit_time))
        return commits

    def analyze(self) -> list:
        """
        分析 Git 提交历史，统计每次提交的总代码行数和变更行数，
        并计算：从项目达到“稳定版本”开始，后续累计变更的代码行数达到稳定版本总代码行数一半所用的时间（天）。
        稳定版本定义为：首次提交的总代码行数达到最终版本总代码行数 90% 时的提交。
        返回一个列表，每个元素为字典，包含：
            commit_hash, commit_time, update_lines, total_lines, half_total_time
        其中只有稳定版本那一条记录的 half_total_time 有值，其它记录为 None。
        """
        commits = self.get_commit_list()
        if not commits:
            print("未找到提交记录。")
            return []
        # 保存当前分支，便于后续恢复
        try:
            original_branch = self.run_git_command(['rev-parse', '--abbrev-ref', 'HEAD'])
        except Exception as e:
            print(f"无法获取当前分支信息: {e}")
            original_branch = None

        commit_data = []
        # 计算每个提交的总代码行数和变更行数
        for idx, (commit_hash, commit_time) in enumerate(commits):
            print(f"正在处理提交: {commit_hash} ...")
            try:
                self.run_git_command(['reset', '--hard'])
                self.run_git_command(['clean', '-fd'])
            except Exception as e:
                print(f"清理工作区失败: {e}")
            self.run_git_command(['checkout', commit_hash])
            total_lines = self.count_lines()
            if idx == 0:
                update_lines = total_lines
            else:
                prev_commit = commits[idx - 1][0]
                try:
                    diff_output = self.run_git_command(['diff', '--numstat', prev_commit, commit_hash])
                    update_lines = 0
                    for line in diff_output.splitlines():
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                added = int(parts[0])
                            except:
                                added = 0
                            try:
                                deleted = int(parts[1])
                            except:
                                deleted = 0
                            update_lines += (added + deleted)
                except Exception as e:
                    print(f"计算 diff 失败: {e}")
                    update_lines = 0
            commit_data.append({
                'commit_hash': commit_hash,
                'commit_time': commit_time,
                'update_lines': update_lines,
                'total_lines': total_lines,
                'half_total_time': None  # 默认 None
            })

        # 定义稳定版本：稳定版本为项目总代码行数首次达到最终版本总代码行数 ?
        final_total = commit_data[-1]['total_lines']
        stable_threshold = final_total * 0.5 
        stable_index = None
        for i, data in enumerate(commit_data):
            if data['total_lines'] >= stable_threshold:
                stable_index = i
                break

        if stable_index is not None and stable_index < len(commit_data) - 1:
            stable_commit = commit_data[stable_index]
            stable_total = stable_commit['total_lines']
            target_change = stable_total / 2.0
            cumulative_change = 0
            stable_time = stable_commit['commit_time']
            half_time = None
            # 从稳定版本之后开始累计变更行数
            for data in commit_data[stable_index+1:]:
                cumulative_change += data['update_lines']
                if cumulative_change >= target_change:
                    half_time_seconds = data['commit_time'] - stable_time
                    half_time_days = half_time_seconds / (3600 * 24)
                    half_time = half_time_days
                    break
            # 将稳定版本记录的 half_total_time 赋值为计算得到的天数
            stable_commit['half_total_time'] = half_time

        # 恢复到原来的分支
        if original_branch:
            self.run_git_command(['checkout', original_branch])
        print("版本更新分析完成。")
        return commit_data

    def save_to_mysql(self, commit_data: list, project_name: str):
        """
        将版本更新分析结果保存到 MySQL 数据库中，每个项目生成独立的表：
            version_updates_{项目名}
        表结构包括：commit_hash, commit_time, update_lines, total_lines, half_total_time（单位：天）。
        为确保最新表结构，此处先 DROP TABLE 再创建。
        """
        ensure_database_exists(self.mysql_config)
        conn = mysql.connector.connect(**self.mysql_config)
        cursor = conn.cursor()
        safe_project_name = re.sub(r'[^a-zA-Z0-9_]', '', project_name)
        table_name = f"version_updates_{safe_project_name}"
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        create_table_sql = f"""
        CREATE TABLE {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            commit_hash VARCHAR(50),
            commit_time BIGINT,
            update_lines INT,
            total_lines INT,
            half_total_time DOUBLE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_table_sql)
        insert_sql = f"""
        INSERT INTO {table_name} (commit_hash, commit_time, update_lines, total_lines, half_total_time)
        VALUES (%s, %s, %s, %s, %s);
        """
        for data in commit_data:
            cursor.execute(insert_sql, (data['commit_hash'], data['commit_time'],
                                        data['update_lines'], data['total_lines'],
                                        data['half_total_time']))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"版本更新结果已保存到 MySQL 表 {table_name}。")
