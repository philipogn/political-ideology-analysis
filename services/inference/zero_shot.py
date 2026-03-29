import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
from dataclasses import dataclass

# mnli model able to classify topic of article, not stance
model_name = 'facebook/bart-large-mnli'
tokenizer_name = ''

''' ===== DATACLASS ===== '''
@dataclass
class CompassValue:
    econ_left: float
    econ_right: float
    social_auth: float
    social_lib: float
    positive: float
    negative: float

''' ===== VARIABLES ===== '''

labels = ['left-wing', 'right-wing', 'authoritarian', 'libertarian']

# HYPOTHESIS
ECON_LEFT = "This text supports left-wing or progressive political views."
ECON_RIGHT = "This text supports right-wing or conservative political views."
SOCIAL_AUTH = "This text supports authoritarian policies like increased state control, surveillance, harsh policing or strict border enforcement."
SOCIAL_LIB = "This text supports libertarian ideas like individual freedom, limited government, free markets or civil liberties."

POSITIVE = "This text expresses positive sentiment or supports the stated position."
NEGATIVE = "This text expresses negative sentiment or opposes the stated position."

# content to infer
premise = """
Labour's workers' rights concessions to save businesses billions, assessment shows	
The government will phase in the reforms over several years, with many measures subject to consultation.	
Archie Mitchell Business reporter A series of concessions on Labour's flagship workers' rights reforms will save businesses billions 
of pounds, a government impact assessment shows. An initial analy… [+3408 chars]
"""
# premise = """Nvidia's (NVDA) China business continues to face geopolitical hurdles, which could pose longer-term competitive risks for the AI chipmaker.
# Ongoing US-China tensions have upended Nvidias sales in wh… [+4297 chars]"""

''' ===== PIPELINE ===== '''
# class InferPipeline:
#     def __init__(self, model_name):
#         self.model_name = model_name

#     def run_pipe(self):
#         classifier = pipeline("zero-shot-classification", model=self.model_name)
#         print(classifier(premise, [ECON_LEFT, ECON_RIGHT], multi_label=False))
#         return classifier

''' ===== MANUAL LOADING WITH TORCH ===== '''

model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model.eval()

def axis_score(premise, axis1, axis2):
    '''
    Scoring the premise against the two axes
    '''
    batched_inference = [(premise, axis1), (premise, axis2)]
    inputs = tokenizer(batched_inference, 
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

    axis1_score = float(label_probs[0])
    axis2_score = float(label_probs[1])
    return axis1_score, axis2_score


def inference(text):
    econ_left, econ_right = axis_score(text, ECON_LEFT, ECON_RIGHT)
    social_auth, social_lib = axis_score(text, SOCIAL_AUTH, SOCIAL_LIB)
    positive, negative = axis_score(text, POSITIVE, NEGATIVE)

    '''
    !!! CURRENT ISSUE !!!
    mnli model able to classify topic of article, not stance
    - one solution
        for e.g., article critiquing right-wing policies/views should be labelled as left-wing (in theory but correlation != rule)
        so maybe political axis (classify topic on political axis) and emotion of content (positive/negative/neutral)
        but again, it can correlate, but does not imply, e.g., critiquing right !-> left-leaning author/article...
    '''
    
    # need to implement confidence scoring

    return CompassValue(
        econ_left = econ_left,
        econ_right = econ_right,
        social_auth = social_auth,
        social_lib = social_lib,
        positive = positive, 
        negative = negative
    )


if __name__ == '__main__':
    ''' ===== PIPELINE ===== '''
    # model_name = 'facebook/bart-large-mnli'
    # pipe = InferPipeline(model_name)
    # result = pipe.run_pipe()
    # print(result)

    ''' ===== MANUAL LOADING WITH TORCH ===== '''
    print(inference(premise))