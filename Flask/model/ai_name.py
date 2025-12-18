# ai 로드 파일
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "WhitePeak/bert-base-cased-Korean-sentiment"

tokenizer_2C = AutoTokenizer.from_pretrained(model_name) # Max_length : 512 tokens
model_2C = AutoModelForSequenceClassification.from_pretrained(model_name)
model_2C.eval()

checkpoint_dir_6 = "yShelby/KoELECTRA_fine_tunning_mood"

tokenizer_6 = AutoTokenizer.from_pretrained(checkpoint_dir_6) # Max_length : 512 tokens
model_6 = AutoModelForSequenceClassification.from_pretrained(checkpoint_dir_6)
model_6.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_6.to(device)
model_2C.to(device)