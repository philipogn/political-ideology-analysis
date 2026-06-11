import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
from dataclasses import dataclass
from torch.nn.functional import softmax
from torch import argmax

# model to determine politicalness
# https://huggingface.co/mlburnham/Political_DEBATE_large_v1.0
politicalness_pipe = pipeline(
    "zero-shot-classification", 
    model="models/Political_DEBATE_large_v1.0", 
    local_files_only=True
)

# fine tuned model for political leaning
# https://huggingface.co/matous-volf/political-leaning-deberta-large
model_name = 'matous-volf/political-leaning-deberta-large'
tokenizer_name = 'microsoft/deberta-v3-large'

''' ===== DATACLASS ===== '''
@dataclass
class CompassValue:
    econ_left: float
    econ_right: float
    social_auth: float
    social_lib: float

''' ===== VARIABLES ===== '''

labels = ['left-wing', 'right-wing', 'authoritarian', 'libertarian']

# HYPOTHESIS
ECON_LEFT = "This text supports left-wing or progressive political views."
ECON_RIGHT = "This text supports right-wing or conservative political views."
SOCIAL_AUTH = "This text supports authoritarian policies like increased state control, surveillance, harsh policing or strict border enforcement."
SOCIAL_LIB = "This text supports libertarian ideas like individual freedom, limited government, free markets or civil liberties."

# content to infer
# premise = """
# Labour's workers' rights concessions to save businesses billions, assessment shows	
# The government will phase in the reforms over several years, with many measures subject to consultation.	
# Archie Mitchell Business reporter A series of concessions on Labour's flagship workers' rights reforms will save businesses billions 
# of pounds, a government impact assessment shows. An initial analy… [+3408 chars]
# """

# premise = '''
# Even as Big Tech CEOs curry favor with President Trump, 
# Silicon Valley employees are calling on their bosses to use their influence to help stop his immigration policies
# '''

premise = '''
The 63-year-old has agreed a three-year deal and will begin work when the squad return for pre-season training on 13 July.
Real Madrid have paid Benfica £13m (15m euros) in compensation to bring the Portuguese head coach back to the Bernabeu - some 13 years after his first stint at the club came to an end.
Florentino Perez had vowed to reappoint Mourinho as head coach if re-elected as club president earlier this month.'''

''' ===== POLITICAL LEARNING ===== '''

model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
model.eval()

def politicalness(input_text):
    '''
    Classify whether text is political or not, for stance inference
    '''
    politicalness = politicalness_pipe(
        input_text,
        ["is not", "is"],
        hypothesis_template="This text {} about politics.",
        multi_label=False,
    )

    max_idx = politicalness['scores'].index(max(politicalness['scores']))
    predicted_class_politicalness = {
        "is not": "non-political",
        "is": "political"
    }[politicalness['labels'][max_idx]]
    return predicted_class_politicalness


def axis_score(input_text):
    '''
    Scoring the premise against left and right 
    '''
    inputs = tokenizer(
        input_text, 
        return_tensors='pt', 
        truncation=True,
        padding=True
    )
    
    with torch.no_grad():
        output = model(**inputs)
        logits = output.logits

    political_lean = argmax(logits, dim=1).item()
    probs = softmax(logits, dim=1)
    score = probs[0, political_lean].item()
    compass = 'Left' if political_lean == 0 else 'Center' if political_lean == 1 else 'Right'
    return {'Economic scale': compass, 'Confidence score': score}


if __name__ == '__main__':
    # print(inference(premise))
    print(politicalness(premise))
    # print(axis_score(premise))

    # test = {'score': [0.578943, 0.213]}

    # max_index = test['score'].index(max(test['score']))
    # print(max_index)