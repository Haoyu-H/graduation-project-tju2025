from modules.comment_code_analyzer import CommentCodeAnalyzer

test_comments = [
    "// 我是邱程浩，这是我的测试文件",  # explanation_comment
    "/* results = analyzer.classify_comments_batch(test_comments); */",  # code_comment
    "# Explanation comment example",  # explanation_comment
    "// int a = 10; // 注释掉的代码",  # code_comment
    "/* return x + y; */"  # code_comment
]

analyzer = CommentCodeAnalyzer(
    output_path="output/",
    model_path="saved_codebert_model",
    tokenizer_path="saved_codebert_model"
)

results = analyzer.classify_comments_batch(test_comments)
print("分类结果:", results)

