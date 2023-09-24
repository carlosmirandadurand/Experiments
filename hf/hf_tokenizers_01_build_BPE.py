# Using Hugging Face Tokeniners to build a subword tokenizer
# 
# Sources: 
#      https://huggingface.co/docs/tokenizers/quicktour
#      https://huggingface.co/docs/transformers/tokenizer_summary
#
# Additional Dependencies: Prior downloads:
#       curl -O https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-103-raw-v1.zip
#       unzip wikitext-103-raw-v1.zip
#
# KEY TOKENIZER TYPES:
# BPE:            Byte-Pair Encoding. Subword tokenization algorithm. 
#                 Split training data into words (pre-tokenizer), create base vocabulary consisting of all symbols, learn merge rules til max vocabulary size is reached.
# Byte-level BPE: Subword tokenization algorithm. Use bytes rather than unicode characters as base vocabulary.  
#                 Example: GPT-2.
# WordPiece:      Subword tokenization algorithm. Very similar to BPE, but uses maximum likelihood to merge tokens.
#                 Used for BERT, DistilBERT, and Electra.
# Unigram:        Subword tokenization algorithm. Initializes base vocabulary to a large number of symbols (i.e. all pretokenized words and most common substrings) 
#                 and progressively trims down each symbol to obtain a smaller vocabulary.  
#                 Not used directly for any of the models in the transformers, but it’s used in conjunction with SentencePiece.
# SentencePiece:  General subword tokenizer that treats inputs as raw stream including the space (not all languages use spaces to separate words) then uses BPE or Unigram.  
#                 All transformers models in the library that use SentencePiece use it in combination with unigram. Examples: ALBERT, XLNet, Marian, and T5. 
#


#%% 
import os

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.processors import TemplateProcessing


#%% 
# Set Global Parameters

input_folder  = './downloads/wikitext-103-raw-v1/wikitext-103-raw'
output_folder = './downloads'

print(os.getcwd())



#%%
# Build a subword BPE tokenizer from scratch

tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = Whitespace()

trainer = BpeTrainer(special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"])

files = [f"{input_folder}/wiki.{split}.raw" for split in ["test", "train", "valid"]]
tokenizer.train(files, trainer)

tokenizer.save(f"{output_folder}/tokenizer-wiki.json")


#%% 
# Set the post-processing to give us the traditional BERT inputs

print(tokenizer.token_to_id("[SEP]"))

tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]")),
    ],
)

tokenizer.save(f"{output_folder}/tokenizer-wiki-final.json")


#%% 
# Use your tokenizer

tokenizer1 = Tokenizer.from_file(f"{output_folder}/tokenizer-wiki.json")
tokenizer2 = Tokenizer.from_file(f"{output_folder}/tokenizer-wiki-final.json")

sentence = "Hello, y'all! How are you 😁 ?"

output1 = tokenizer1.encode(sentence)
output2 = tokenizer2.encode(sentence)


#%%
# See tokenizer output without post-processing

print(output1.tokens)
print(output1.ids)


#%%
# See final tokenizer output 

print('tokens              :', output2.tokens)
print('ids                 :', output2.ids)
print('type_ids            :', output2.type_ids)
print('attention_mask      :', output2.attention_mask)
print('special_tokens_mask :', output2.special_tokens_mask)
print('overflowing         :', output2.overflowing)


#%%
# See the offsets and tokens they split

for i in output2.offsets:
    print(f'offset: {i} --> { sentence[i[0]:i[1]] }')



#%% END




