# Using Hugging Face Tokenizers to build a BERT tokenizer from scratch
# 
# Sources: 
#   https://huggingface.co/docs/tokenizers/pipeline
#   https://huggingface.co/docs/tokenizers/components
#   https://huggingface.co/docs/transformers/tokenizer_summary


#%% 
import os

from tokenizers import Tokenizer
from tokenizers import normalizers
from tokenizers import decoders
from tokenizers.models import WordPiece
from tokenizers.normalizers import NFD, Lowercase, StripAccents
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing
from tokenizers.trainers import WordPieceTrainer



#%% 
# Set Global Parameters

input_folder  = './downloads/wikitext-103-raw-v1/wikitext-103-raw'
output_folder = './downloads'
print(os.getcwd())



#%% 
# Test a normalizer

from tokenizers import normalizers
from tokenizers.normalizers import NFD, StripAccents
normalizer = normalizers.Sequence([NFD(), StripAccents()])
normalizer.normalize_str("Héllò hôw are ü?")

#%%
# Define the BERT tokenizer

bert_tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
bert_tokenizer.normalizer = normalizers.Sequence([NFD(), Lowercase(), StripAccents()])
bert_tokenizer.pre_tokenizer = Whitespace()
bert_tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", 1),
        ("[SEP]", 2),
    ],
)

#%%
# Train the BERT tokenizer

trainer = WordPieceTrainer(vocab_size=30522, special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"])

files = [f"{input_folder}/wiki.{split}.raw" for split in ["test", "train", "valid"]]

bert_tokenizer.train(files, trainer)
bert_tokenizer.save(f"{output_folder}/bert-wiki.json")


#%% 
# Test the tokenizer

input_sentence = "Welcome to the 🤗 Tokenizers library."
output = bert_tokenizer.encode(input_sentence)
print(output.ids)
print(output.tokens)

reconstructed_input = bert_tokenizer.decode(output.ids)
print(reconstructed_input)

#%% 
# Set the right decoder --> test the tokenizer again

bert_tokenizer.decoder = decoders.WordPiece()
reconstructed_input = bert_tokenizer.decode(output.ids)
print(reconstructed_input)


#%% END



