from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "microsoft/codebert-base"
local_dir = "./saved_codebert_model"

model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

model.save_pretrained(local_dir)
tokenizer.save_pretrained(local_dir)
