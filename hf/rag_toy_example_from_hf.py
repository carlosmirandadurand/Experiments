# Retrieval-Augmented Generation - Hugging Face Examples
# References:
#    https://huggingface.co/docs/transformers/main/model_doc/rag
#    https://huggingface.co/facebook/rag-sequence-nq


## FIRST DRAFT COMMIT - Pending testing....

#%%

from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration, RagTokenForGeneration


#%%########################################################################################################
# Model facebook/rag-token-nq
###########################################################################################################

tokenizer2 = RagTokenizer.from_pretrained("facebook/rag-token-nq")
retriever2 = RagRetriever.from_pretrained("facebook/rag-token-nq", index_name="exact", use_dummy_dataset=True)
model2 = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever2)


#%%
input_dict = tokenizer2.prepare_seq2seq_batch("who holds the record in 100m freestyle", return_tensors="pt") 


#%%
generated = model2.generate(input_ids=input_dict["input_ids"]) 


#%%
response = tokenizer2.batch_decode(generated, skip_special_tokens=True)
print(response[0])  # should give michael phelps => sounds reasonable



#%%########################################################################################################
# Model facebook/rag-sequence-nq
###########################################################################################################

 #%%
tokenizer = RagTokenizer.from_pretrained("facebook/rag-sequence-nq") 
retriever = RagRetriever.from_pretrained("facebook/rag-sequence-nq", index_name="exact", use_dummy_dataset=True) 
model = RagSequenceForGeneration.from_pretrained("facebook/rag-sequence-nq", retriever=retriever) 


#%%
input_dict = tokenizer.prepare_seq2seq_batch("how many countries are in europe", return_tensors="pt") 
print(input_dict)


#%%
generated = model.generate(input_ids=input_dict["input_ids"]) 


#%%
response = tokenizer.batch_decode(generated, skip_special_tokens=True)
print(response[0])  # should give 54 => google says either 44 or 51



#%% END
