from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
model_name = 'facebook/bart-large-mnli'
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# content to infer
premise = ''
# content 'falls into a political compass'
hypothesis = ''


political_axis = ['left-wing', 'right-wing', 'authoritarian', 'libertarian']
