#%%##################################################################################
# OpenAI - Function calling from Chat completions API
# Original source code: https://platform.openai.com/docs/guides/gpt/function-calling
#####################################################################################

import os
import json
import types
import random
import openai

from dotenv import load_dotenv


#%%##################################################################################
# Define Callback Functions  (dummy examples hard-coded to simulate the real thing)
#####################################################################################

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if unit.lower()=="fahrenheit":
        t = random.randint(30, 90)
        if t >= 60:
            f = ["sunny", "windy"]
        else:
            f = ["rainy", "windy"]
    else: 
        t = random.randint(-1, 32)
        if t >= 15:
            f = ["sunny", "windy"]
        else:
            f = ["rainy", "windy"]
    weather_info = {
        "location": location,
        "temperature": t, 
        "unit": unit,
        "forecast": f,
    }
    print(f"[FUNCTION CALLED: get_current_weather({location},{unit}) -> {t} {f}]")
    return json.dumps(weather_info)


def send_email(subject, message, to, cc = []):
    """Send an email"""
    response = "Message sent"
    print(f"[FUNCTION CALLED: send_email(to='{to}', cc='{cc}', subject='{subject}', message='{message}') --> {response}]")
    return response


# DEFINE THE CALLBACK FUNCTION SPECS FOR CHAT GPT
available_functions_definitions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },

    {
        "name": "send_email",
        "description": "Send an email",
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "The subject of the email to be sent",
                },
                "message": {
                    "type": "string",
                    "description": "The body of the email to be sent eitehr in plain text or HTML format",
                },
                "to": {
                    "type": "string",
                    "description": "An email address or a comma-separated list of email addresses to whom the email should be sent",
                },
                "cc": {
                    "type": "string",
                    "description": "An email address or a comma-separated list of email addresses who should be copied in the email",
                },
            },
            "required": ["subject", "message", "to"],
        },
    },
]



# Create a dictionary mapping function names to the actual functions available 
available_functions = {name: func 
                       for name, func in globals().items() 
                          if isinstance(func, types.FunctionType) 
                            and name in [x['name'] for x in available_functions_definitions] }

print(available_functions)



#%%##################################################################################
# Conversation with ChatGPT  
#####################################################################################

def run_conversation_with_one_function_call (user_question = "What's the weather like in Boston?"):

    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": user_question}]

    response = openai.ChatCompletion.create(
        model         = "gpt-3.5-turbo-0613",
        messages      = messages,
        functions     = available_functions_definitions,
        function_call = "auto",  
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):

        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        function_name    = response_message["function_call"]["name"]
        function_args    = json.loads(response_message["function_call"]["arguments"])
        function_to_call = available_functions[function_name]
        function_response = function_to_call(**function_args)

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  
        second_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
        )  
        return second_response

    else:
        # Step 3 (if no function is called): return the first response
        return response_message


def run_conversation_with_function_calls (user_question = "What's the weather like in Boston?"):

    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": user_question}]

    response = openai.ChatCompletion.create(
        model         = "gpt-3.5-turbo-0613",
        messages      = messages,
        functions     = available_functions_definitions,
        function_call = "auto",  
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    while response_message.get("function_call"):

        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        function_name    = response_message["function_call"]["name"]
        function_args    = json.loads(response_message["function_call"]["arguments"])
        function_to_call = available_functions[function_name]
        function_response = function_to_call(**function_args)

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )
        response = openai.ChatCompletion.create(
            model         = "gpt-3.5-turbo-0613",
            messages      = messages,
            functions     = available_functions_definitions,
            function_call = "auto",  
        )
        response_message = response["choices"][0]["message"]

    # Final step, when the response if not a call-back function, return the answer to the user
    return response_message




#%%##################################################################################
# Execute
#####################################################################################

load_dotenv()
openai.organization = os.getenv('openai_organization_id')
openai.api_key      = os.getenv('openai_organization_key')


#%%
print(run_conversation_with_one_function_call("What's the weather like in Dallas Fort Worth?"))


#%%
print(run_conversation_with_function_calls("What's the weather like in Dallas Fort Worth?"))


#%%
print(run_conversation_with_function_calls("Please find out what's the weather like in Paris and send the information to my wife (rose.smith@gmail.com) and son (mike.smith@gmail.com) and copy me as well (charlie.smith@gmail.com)."))

#%%
print(run_conversation_with_function_calls("""Please find out what's the weather like in Little Rock, AR.  
                                           If it seems a good day for a picnic, then please send the information to my wife (rose.smith@gmail.com) and son (mike.smith@gmail.com) and copy me as well (charlie.smith@gmail.com). 
                                           If it seems not a good day for a picnic, then don't send the email and just let me know why.
                                           """))



#%% END



