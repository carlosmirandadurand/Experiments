#%%#########################################################################################
# 
# AWS Bedrock Test with LangChain
# Source: https://python.langchain.com/v0.1/docs/integrations/llms/bedrock/
#
# Also compare with OpenAI-langchain
# 
############################################################################################


import os
from dotenv import load_dotenv

from langchain_community.llms import Bedrock
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler



#%%
# Load parameters

load_dotenv()





#%%#########################################################################################
# AWS Bedrock - Langchain
############################################################################################

llm = Bedrock(
    credentials_profile_name = "default", 
    model_id = "mistral.mixtral-8x7b-instruct-v0:1"
)


#%%
# Using a conversation chain

conversation = ConversationChain(
    llm=llm, verbose=True, memory=ConversationBufferMemory()
)

conversation.predict(input="Hi there!")


#%% 
# Conversation Chain With Streaming

llm = Bedrock(
    credentials_profile_name="default",
    model_id="mistral.mixtral-8x7b-instruct-v0:1",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
)

conversation = ConversationChain(
    llm=llm, verbose=True, memory=ConversationBufferMemory()
)

conversation.predict(input="Hi there!")


#%% END
