import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
from dataclasses import dataclass
from torch.nn.functional import softmax
from torch import argmax

''' ===== DATACLASS ===== '''
@dataclass
class CompassValue:
    econ_left: float
    econ_right: float
    social_auth: float
    social_lib: float

# model to determine politicalness (https://huggingface.co/mlburnham/Political_DEBATE_large_v1.0)
politicalness_pipe = pipeline(
    "zero-shot-classification", 
    model="models/Political_DEBATE_large_v1.0", 
    local_files_only=True
)

# fine tuned model for political leaning (https://huggingface.co/matous-volf/political-leaning-deberta-large)
stance_tokenizer = AutoTokenizer.from_pretrained("matous-volf/political-leaning-deberta-large")
stance_model = AutoModelForSequenceClassification.from_pretrained("matous-volf/political-leaning-deberta-large")
stance_model.eval()

# content to infer
# premise = '''
# Even as Big Tech CEOs curry favor with President Trump, 
# Silicon Valley employees are calling on their bosses to use their influence to help stop his immigration policies
# '''

premise = '''
The 63-year-old has agreed a three-year deal and will begin work when the squad return for pre-season training on 13 July.
Real Madrid have paid Benfica £13m (15m euros) in compensation to bring the Portuguese head coach back to the Bernabeu - some 13 years after his first stint at the club came to an end.
Florentino Perez had vowed to reappoint Mourinho as head coach if re-elected as club president earlier this month.'''

# premise = '''Israel carries out air strikes on Lebanon, state media says, as Iran claims deal with US near'''

def about_politics(input_text):
    '''
    Classify whether text is political or not, for stance inference
    '''
    politicalness = politicalness_pipe(
        input_text,
        ["is", "is not"],
        hypothesis_template="This text {} about politics.",
        multi_label=False,
    )
    max_idx = politicalness["scores"].index(max(politicalness["scores"]))
    predicted_class_politicalness = {"is": True,"is not": False}[politicalness["labels"][max_idx]]
    return predicted_class_politicalness


def axis_score(input_text):
    '''
    Scoring the premise against left and right 
    '''
    inputs = stance_tokenizer(
        input_text, 
        return_tensors='pt', 
        truncation=True,
        padding=True
    )
    
    with torch.no_grad():
        output = stance_model(**inputs)
        logits = output.logits

    political_lean = argmax(logits, dim=1).item()
    probs = softmax(logits, dim=1)
    score = probs[0, political_lean].item()
    compass = "Left" if political_lean == 0 else "Center" if political_lean == 1 else "Right"
    return {"Economic scale": compass, "Confidence score": score}

def politicalness_inference(input_text):
    if about_politics(input_text) == True:
        return axis_score(input_text)
    else:
        return ("The article is non political")


if __name__ == "__main__":
    print(politicalness_inference(premise))