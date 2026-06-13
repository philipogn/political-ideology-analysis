# political-ideology-analysis
A system to locate a news articles' political compass 

# Implications
Models such as MNLI classifiers are not able to classify political stance of a text. (will test with pos/neg connotation against fine-tund)
This requires a fine-tuned model to process and classify stance

First model to classify whether or not the text is on the topic of politics ('mlburnham/Political_DEBATE_large_v1.0')
Second model to classify the political stance of the text ('matous-volf/political-leaning-deberta-large')