import torch
from transformers import XLMRobertaTokenizer, AutoModel

MODEL_NAME = "uitnlp/visobert"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ÉP tokenizer SLOW
tokenizer = XLMRobertaTokenizer.from_pretrained(MODEL_NAME)

model = AutoModel.from_pretrained(MODEL_NAME)
model.to(device)
model.eval()
