import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline

model_name = 'facebook/bart-large-mnli'

''' ===== VARIABLES ===== '''

labels = ['left-wing', 'right-wing', 'authoritarian', 'libertarian']

STANCE_LABELS = [
    "This supports left-wing or progressive political views.",
    "This supports right-wing or conservative political views.",
    "This supports authoritarian policies like increased state control, surveillance, harsh policing or strict border enforcement.",
    "This supports libertarian ideas like individual freedom, limited government, free markets or civil liberties."
]

ECON_LEFT = "This supports left-wing or progressive political views."
ECON_RIGHT = "This supports right-wing or conservative political views."
SOCIAL_AUTH = "This supports authoritarian policies like increased state control, surveillance, harsh policing or strict border enforcement."
SOCIAL_LIB = "This supports libertarian ideas like individual freedom, limited government, free markets or civil liberties."

# content to infer
premise = """
Labour's workers' rights concessions to save businesses billions, assessment shows	
The government will phase in the reforms over several years, with many measures subject to consultation.	
Archie Mitchell Business reporter A series of concessions on Labour's flagship workers' rights reforms will save businesses billions 
of pounds, a government impact assessment shows. An initial analy… [+3408 chars]
"""

# content 'falls into a political compass
hypothesis = 'This supports left-wing or progressive political views'


''' ===== PIPELINE ===== '''
# class InferPipeline:
#     def __init__(self, model_name):
#         self.model_name = model_name

#     def run_pipe(self):
#         classifier = pipeline("zero-shot-classification", model=self.model_name)
#         return classifier

''' ===== MANUAL LOADING WITH TORCH ===== '''

model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model.eval()

build_sequence = [(premise, ECON_LEFT), (premise, ECON_RIGHT), (premise, SOCIAL_AUTH), (premise, SOCIAL_LIB)]
batched_sequence = [(premise, hyp) for hyp in STANCE_LABELS]

# padding for batches
inputs = tokenizer(batched_sequence, 
                   return_tensors='pt', 
                   truncation=True,
                   padding=True
                   )

with torch.no_grad():
    output = model(**inputs)
    logits = output.logits

entailment_logits = logits[:,[0,2]]
probs = torch.softmax(entailment_logits, dim=1)
label_probs = probs[:,1]
print(label_probs)

results = sorted(
        [{"label": l, "score": float(p)} for l, p in zip(labels, label_probs)],
        key=lambda x: x["score"],
        reverse=True
    )

print(results)

# if __name__ == '__main__':
#     model_name = 'facebook/bart-large-mnli'

#     ''' ===== PIPELINE ===== '''
#     # pipe = InferPipeline(model_name)
#     # result = pipe.classifier(premise, labels, multi_label=True)
#     # print(result)

#     ''' ===== MANUAL LOADING WITH TORCH ===== '''