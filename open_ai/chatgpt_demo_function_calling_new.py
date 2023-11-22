#%%##################################################################################
# OpenAI - Function calling from Chat completions API
# Original source code from: 
#       https://platform.openai.com/docs/guides/gpt/function-calling (old)
#       https://platform.openai.com/docs/guides/function-calling
#       https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models 
#####################################################################################

import os
import json
import time
import types
import random
import openai

from dotenv import load_dotenv

import sqlite3


#%%##################################################################################
# ChatGPT Helper Functions  
#####################################################################################

def chatgpt_basic_call (prompt, 
                        prior_messages = None,
                        system_message = None, 
                        model = 'gpt-3.5-turbo', 
                        temperature = 0.01,
                        pause = 0.01,
                        ):
    # Pre-execution
    if model is None:
        return prompt # For testing 
    
    if pause:
        time.sleep(pause)  # Wait to avoid exceeding limits

    if prior_messages:
        messages = prior_messages + [
            {"role": "user", "content": prompt}
        ]
    elif system_message:
        messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
    else:
        messages = [
                {"role": "user", "content": prompt},
            ]
    
    # Execute
    try:
        response = openai.ChatCompletion.create(
            model = model,
            messages = messages,
            temperature = temperature,
            n = 1,
        )
        
        response_message = response.choices[0].message
        response_content = response_message['content']
        response_attributes = { 
            'id':                response['id'],
            'response_ms':       response.response_ms,
            'model':             response['model'],
            'prompt_tokens':     response['usage']['prompt_tokens'],
            'completion_tokens': response['usage']['completion_tokens'],
            'total_tokens':      response['usage']['total_tokens'],
            }        
        messages.append(dict(response_message))

    except Exception as err:

        response_content = f"Unexpected Error: {err=}"
        response_attributes = {}
        messages = prior_messages

    return (response_content, messages, response_attributes)



def chatgpt_run_conversation_with_function_calls (prompt, 
                                                  prior_messages = None,
                                                  system_message = None,
                                                  functions_definitions = {},
                                                  model = 'gpt-3.5-turbo',
                                                  tool_choice = "auto",
                                                  temperature = 0.01,
                                                  pause = 0.01,
                                                  f_out = None,
                                                  ):
    # Pre-execution
    if model is None:
        return prompt # For testing 
 
    if pause:
        time.sleep(pause)  # Wait to avoid exceeding limits

    if prior_messages:
        messages = prior_messages + [
            {"role": "user", "content": prompt}
        ]
    elif system_message:
        messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ]
    else:
        messages = [
                {"role": "user", "content": prompt},
            ]
        
    response_attributes = []
        
    # Map function names to the actual functions available and to tools
    available_functions = {name: func 
                        for name, func in globals().items() 
                            if isinstance(func, types.FunctionType) 
                                and name in [f['name'] for f in functions_definitions] }

    # List of "tools" (only functions for now)
    tool_definitions = []
    for f in functions_definitions:
        tool_definitions.append({"type": "function", "function": f})
    
    # Execute
    try:

        while True:

            # Send the conversation and available functions to ChatGPT
            if f_out: f_out.write(f"CHATGPT {model} CALL:\n{messages}\n")
            if tool_definitions:
                response = openai.ChatCompletion.create(
                    model         = model,
                    messages      = messages,
                    tools         = tool_definitions,
                    tool_choice   = tool_choice,
                    temperature   = temperature,
                )
            else:
                response = openai.ChatCompletion.create(
                    model         = model,
                    messages      = messages,
                    temperature   = temperature,
                )
            if f_out: f_out.write(f"CHATGPT RESPONSE:\n{response}\n")

            response_message = response.choices[0].message
            response_content = response_message['content']
            messages.append(dict(response_message))
            response_attributes.append({ 
                'id':                response['id'],
                'response_ms':       response.response_ms,
                'model':             response['model'],
                'prompt_tokens':     response['usage']['prompt_tokens'],
                'completion_tokens': response['usage']['completion_tokens'],
                'total_tokens':      response['usage']['total_tokens'],
                })    

            # Check if the response contains a function call
            if 'tool_calls' not in response_message:
                break  # Exit the loop here

            # Execute all the tools called by ChatGPT
            for tool in response_message['tool_calls']:

                if tool['type']  == 'function':
                    # Call the function
                    # TODO: the JSON response may not always be valid; be sure to handle errors
                    # TODO: Check when no longer in beta: client.beta.threads.runs.submit_tool_outputs
                    function_name    = tool["function"]["name"]
                    function_args    = tool["function"]["arguments"]
                    function_args    = json.loads(function_args)
                    function_to_call = available_functions[function_name]
                    function_response = function_to_call(**function_args)

                    # Send the info on the function call and function response to GPT
                    messages.append({"role"         : "tool", 
                                     "tool_call_id" : tool['id'], 
                                     "name"         : function_name, 
                                     "content"      : function_response,
                                     })

    except Exception as err:

        response_content = f"Unexpected Error: {err=}"
        response_attributes = {}
        messages = prior_messages

    # When the response if not a call-back function, return the final answers to the user
    return (response_content, messages, response_attributes)



#%%##################################################################################
# Mock Callback Functions  (dummy examples hard-coded to simulate the real thing)
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


#%%##################################################################################
# Real Callback Functions  (execute real queries)
#####################################################################################


def ask_database(query):
    """Function to query SQLite database with a provided SQL query."""
    try:
        results = str(conn.execute(query).fetchall())
    except Exception as e:
        results = f"query failed with error: {e}"
    print(f"[FUNCTION CALLED: ask_database({query}) -> {results}]")
    return results


# Helper functions
def get_table_names(conn):
    """Return a list of table names."""
    table_names = []
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names


def get_column_names(conn, table_name):
    """Return a list of column names."""
    column_names = []
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    for col in columns:
        column_names.append(col[1])
    return column_names


def get_database_info(conn):
    """Return a list of dicts containing the table name and columns for each table in the database."""
    table_dicts = []
    for table_name in get_table_names(conn):
        columns_names = get_column_names(conn, table_name)
        table_dicts.append({"table_name": table_name, "column_names": columns_names})
    return table_dicts


#%%##################################################################################
# Execute
#####################################################################################

load_dotenv()
openai.organization = os.getenv('openai_organization_id')
openai.api_key      = os.getenv('openai_organization_key')

conn = sqlite3.connect("../data/Chinook.db")

print("Connections were sucessful!")



#%%##################################################################################
# Execute basic ChatGPT calls
#####################################################################################

q1 = chatgpt_basic_call("Who discovered penicilin?")
q1

#%%
q2 = chatgpt_basic_call("When?")
q2

#%%
q1_response_content, q1_messages, q1_response_attributes = q1
q2 = chatgpt_basic_call("When?", q1_messages)
q2





#%%##################################################################################
# Execute ChatGPT calls that require functions
#####################################################################################

# # Load metadata for function description below
# database_schema_dict = get_database_info(conn)
# database_schema_string = "\n".join(
#     [
#         f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
#         for table in database_schema_dict
#     ]
# )

# Define all the functions
functions_definitions = [
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

    {
        "name": "ask_database",
        "description": "Use this function to answer user questions about music. Input should be a fully formed SQL query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": f"""
                            SQL query extracting info to answer the user's question.
                            SQL should be written using this database schema:
                            Table: albums
                            Columns: AlbumId, Title, ArtistId
                            Table: artists
                            Columns: ArtistId, Name
                            Table: customers
                            Columns: CustomerId, FirstName, LastName, Company, Address, City, State, Country, PostalCode, Phone, Fax, Email, SupportRepId
                            Table: employees
                            Columns: EmployeeId, LastName, FirstName, Title, ReportsTo, BirthDate, HireDate, Address, City, State, Country, PostalCode, Phone, Fax, Email
                            Table: genres
                            Columns: GenreId, Name
                            Table: invoices
                            Columns: InvoiceId, CustomerId, InvoiceDate, BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode, Total
                            Table: invoice_items
                            Columns: InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity
                            Table: media_types
                            Columns: MediaTypeId, Name
                            Table: playlists
                            Columns: PlaylistId, Name
                            Table: playlist_track
                            Columns: PlaylistId, TrackId
                            Table: tracks
                            Columns: TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice
                            The query should be returned in plain text, not in JSON.
                            """,
                }
            },
            "required": ["query"],
        },

    },
]




#%%

q1 = chatgpt_run_conversation_with_function_calls("What's the weather like in Dallas Fort Worth?")

print(q1[0])


#%%

q1 = chatgpt_run_conversation_with_function_calls(
        prompt = "What's the weather like in Dallas Fort Worth?", 
        functions_definitions = functions_definitions,
        )

print(q1[0])


#%%

q2 = chatgpt_run_conversation_with_function_calls(
        system_message = "You are an sarcastic and grumpy weather forecaster who never misses and opportunity to complain. ",
        prompt = "What's the weather like in Dallas Fort Worth, Hong Kong, and in Paris?", 
        functions_definitions = functions_definitions,
        )

print(q2[0])


#%%

q3 = chatgpt_run_conversation_with_function_calls(
        "Please find out what's the weather like in Paris and send the information to my wife (rose.smith@gmail.com) and son (mike.smith@gmail.com) and copy me as well (charlie.smith@gmail.com).",
        functions_definitions = functions_definitions,
        )

print(q3[0])


#%%
q4 = chatgpt_run_conversation_with_function_calls(
        prompt = """Please find out what's the weather like in Little Rock, AR.  
                If it seems a good day for a picnic, then please send the information to my wife (rose.smith@gmail.com) and son (mike.smith@gmail.com) and copy me as well (charlie.smith@gmail.com). 
                If it seems not a good day for a picnic, then don't send the email and just let me know why.
                """,
        functions_definitions = functions_definitions,
        )

print(q4[0])


#%%

q5 = chatgpt_run_conversation_with_function_calls(
        system_message = "Answer user questions by generating SQL queries against the Chinook Music Database.",
        prompt = "Hi, who are the top 5 artists by number of tracks?", 
        functions_definitions = functions_definitions,
        )

print(q5[0])


#%%

q5_response_content, q5_messages, q5_response_attributes = q5

q6 = chatgpt_run_conversation_with_function_calls(
        prior_messages = q5_messages,
        prompt = "What is the total number of tracks among the top 3?", 
        functions_definitions = functions_definitions,
        )

print(q6[1])


#%% END



