
#%%

# Load helper functions from gist 
import requests
exec(requests.get("https://bit.ly/cmd-clear-console-output-latest").text)


# # Load helper functions from local directory
# import os
# import datetime
# from clear_console import clear_console_title, clear_console_item, clear_console_os_command


#%%

clear_console_title("Section One")
clear_console_title("Section One", "End")

clear_console_item("Logging Items now....")
clear_console_item("Item One",   "Say Hello")
clear_console_item("Item Two",   "Ask how are you?", "Listen")
clear_console_item("Item Three", "Acknowledge")

clear_console_os_command("Command One", "ls -al")
clear_console_os_command("Command Two", "ps")


# %%
x = ["List with one item"]
print(x,"\n")
clear_console_item(x)

x = {"Key": "Dict with one item"}
print(x,"\n")
clear_console_item(x)

x = ("Tuple with single item",)
print(x,"\n")
clear_console_item(x)


# %%
x = [10, 20, 30, 40, 50]
print(x,"\n")
clear_console_item(x)

x = {"k1": "v1", "k2": 2, 3:"v3", 4.0: 4.1, "k5":"v5"}
print(x,"\n")
clear_console_item(x)

x = ("a", "b", "c", 4, 5.0)
print(x,"\n")
clear_console_item(x)



#%%
x = ["Long list with nested lists up to three levels deep", 100, 200, 300, ["410", "420"], ["510", "520", "530"], [610,620,[631,632,633],640,650], 700, 800]
print(x,"\n")
clear_console_item(x)


#%%
x = ("Long tuple with nested tuples up to three levels deep", 100, 200, 300, ("410", "420"), ("510", "520", "530"), (610,620,(631,632,633),640,650), 700, 800)
print(x,"\n")
clear_console_item(x)


#%%
x = {   "L1.0":"Long dictionary with nested dicionaries up to three levels deep", 
        "L1.1":100, 
        "L1.2":200, 
        "L1.3":300, 
        "L1.4":{"L2.1":"410", "L2.2":"420"}, 
        "L1.5":{"L2.3":"510", "L2.4":"520", "L2.5":"530"}, 
        "L1.6":{"L2.6.LONER":610, "L2.7":620, "L2.8.LONGEST-KEY":(631,632,633), "L2.9":640, "L2.10":650}, 
        "L1.7":700, 
        "L1.8":800}
print(x,"\n")
clear_console_item(x)



#%%
x = ["List with some dictionaries and tuples", "a", "b", {"c": "cv"}, 4, {5:5.1, 6.0:6.1}, (8,9,10,11,12), 13, 14, 15]
print(x,"\n")
clear_console_item(x)


#%%

