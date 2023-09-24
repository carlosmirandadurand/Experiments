# Tests with Spacy
# Sources: 
#       https://spacy.io/
#       https://github.com/explosion/spacy-llm


# TODO: Spacy and ftfy 


import spacy


#%% Install depenencies and download a specific model (e.g., the English model) 

# pip install -U spacy
# python -m spacy download en_core_web_sm


#%%
# Load English tokenizer, tagger, parser and NER

nlp = spacy.load("en_core_web_sm")

# Process whole documents
text = ("When Sebastian Thrun started working on self-driving cars at "
        "Google in 2007, few people outside of the company took him "
        "seriously. “I can tell you very senior CEOs of major American "
        "car companies would shake my hand and turn away because I wasn’t "
        "worth talking to,” said Thrun, in an interview with Recode earlier "
        "this week.")
doc = nlp(text)

# Analyze syntax
print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks])
print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"])

# Find named entities, phrases and concepts
for entity in doc.ents:
    print(entity.text, entity.label_)


