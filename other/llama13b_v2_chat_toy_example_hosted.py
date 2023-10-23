# Toy Examples using the Llama 2 model (hosted by replicate)
# Sources: 
#    https://www.youtube.com/watch?v=dBoQLktIkOo&t=114s
#    https://github.com/dataprofessor/llama2
#    https://github.com/replicate/replicate-python


#%%
import replicate
import os
from dotenv import load_dotenv


#%% 
# export REPLICATE_API_TOKEN=<your token>

load_dotenv()
api_token = os.getenv('replicate_api_token__cmd') # replicate_api_token__default, replicate_api_token__cmd
os.environ["REPLICATE_API_TOKEN"] = api_token

print("Token length: ", len(os.getenv('REPLICATE_API_TOKEN')))


#%%
# Replicate demo example (Stable Difusion) 

r = replicate.run(
        "stability-ai/stable-diffusion:27b93a2413e7f36cd83da926f3656280b2931564ff050bf9575f1fdf9bcd7478",
        input={"prompt": "a 19th century portrait of a wombat gentleman"}
    )

r


#%% 
# LLM Prompts (Llama v2)

system_prompt = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."

user_prompt = "When was America discovered?"


#%% 
# Call LLM (Llama v2)


llm_input = {"prompt": f"{system_prompt} {user_prompt} Assistant: ",
             "temperature": 0.1, 
             "top_p": 0.9, 
             "max_length": 128, 
             "repetition_penalty": 1,
             }

llm_model = "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5"
llm_model = "a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea"

llm_output_gen = replicate.run(llm_model, input = llm_input) 

llm_output_gen


#%%
# See Llama v2 results

llm_full_response = ""
for item in llm_output_gen:
  llm_full_response += item

print(llm_full_response)


#%% END

