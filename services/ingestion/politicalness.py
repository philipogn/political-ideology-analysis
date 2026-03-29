from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

politicalness_pipe = pipeline(
    "zero-shot-classification", model="mlburnham/Political_DEBATE_base_v1.0", device = device
)

premise = """
Labour's workers' rights concessions to save businesses billions, assessment shows	
The government will phase in the reforms over several years, with many measures subject to consultation.	
Archie Mitchell Business reporter A series of concessions on Labour's flagship workers' rights reforms will save businesses billions 
of pounds, a government impact assessment shows. An initial analy… [+3408 chars]
"""
# premise = """Nvidia's (NVDA) China business continues to face geopolitical hurdles, which could pose longer-term competitive risks for the AI chipmaker.
# Ongoing US-China tensions have upended Nvidias sales in wh… [+4297 chars]"""

tokenizer = AutoTokenizer.from_pretrained("mlburnham/Political_DEBATE_large_v1.0")
model = AutoModelForSequenceClassification.from_pretrained("mlburnham/Political_DEBATE_large_v1.0")

def about_politics(text):
    labels = ["is", "is not"]
    hypothesis = "This text is {} about politics."
    politicalness = politicalness_pipe(
        text, 
        labels, 
        hypothesis = hypothesis, 
        multi_label = False
    )
    # returns bool depending on predicted label
    prediction = {"is": True, "is not": False}[politicalness["labels"][0]]
    return prediction

print(about_politics(premise))
