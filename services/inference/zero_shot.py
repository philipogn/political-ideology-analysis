from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

model_name = 'facebook/bart-large-mnli'
classifier = pipeline("zero-shot-classification", model=model_name)
# model = AutoModelForSequenceClassification.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)

labels = ['left-wing', 'right-wing', 'authoritarian', 'libertarian']

# attempt with pipeline
# content to infer
premise = """
A very simple explanation for why politics is broken. In today's America,
the less money a white voter has, the more likely they are to support Donald Trump.
Whites in the bottom 10 percent of America’s income distribution broke for the GOP nominee in 2024
by landslide margins. Those in the top 5 percent largely… A new study presents evidence that cable news
causes voters — and thus, politicians — to put a greater premium on social issues. 
"""

# content 'falls into a political compass
hypothesis = ''

result = classifier(premise, labels, multi_label=True)

print(result)