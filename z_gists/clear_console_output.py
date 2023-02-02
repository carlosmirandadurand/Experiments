# Source code for the gist: clear_console_output.py at https://gist.github.com/carlosmirandadurand
# Installation:
#   !wget -q bit.ly/cmd-clear-console-output-latest
#   %run cmd-clear-console-output-latest

import os
import datetime

def clear_console_title (*args):
    """
    Clear console functions help produce readable console output that is comprhensive, verbose, and quick to follow.

    The clear_console_title function writes a visible section header (or section title) in the console. 
    It also adds additional tracking information about the process.  
    Use it to mark each major milestone of your process, so you can quickly follow later. 

    Parameters:
        args (strings): One or more names, titles, or messages to display.
        
    Note:
        The clear console functions are not meant as a replacement of proper logs. 
        Please continue to use the logging module in addition to these functions 
        (especially logging.warning, logging.error, and logging.critical) throughout your scripts. 
        One may substitute logging.info with these functions when it's desirable to always print to console 
        and to always have this information "on" (never disabled based on logging level) in a thread safe context.
        In fact, there is no concept of level in these functions (same items are reported in all environments.) 
    """
    print('-'*10, datetime.datetime.now(), ":", " / ".join(args), '-'*10, flush=True)



def clear_console_item (*args):
    """
    Clear console functions help produce readable console output that is comprhensive, verbose, and quick to follow. 

    The clear_console_item function writes the contents of the parameter. 

    Parameters:
        args (strings): One or more items to display.
        
    Note:
        The clear console functions are not meant as a replacement of proper logs. 
        Please continue to use the logging module in addition to these functions 
        (especially logging.warning, logging.error, and logging.critical) throughout your scripts. 
        One may substitute logging.info with these functions when it's desirable to always print to console 
        and to always have this information "on" (never disabled based on logging level) in a thread safe context.
        In fact, there is no concept of level in these functions (same items are reported in all environments.) 
    """

    # Define a recursive helper function to deal with each data type as desired for a clear output
    def _cc_item_helper (item, indent=0):
        output = ''
        output_indent_string = ' ' * indent
        if isinstance(item, tuple):
            output +=  '(\n'
            for i in item:
                output += output_indent_string + ' + ' + _cc_item_helper(i, indent+3) + '\n'
            output += output_indent_string + ')\n'

        elif isinstance(item, list):
            output +=  '[\n'
            for i in item:
                output += output_indent_string + ' - ' + _cc_item_helper(i, indent+3) + '\n'
            output += output_indent_string + ']\n'

        elif isinstance(item, dict):
            output +=  '{\n'
            for i in item.keys():
                key = f' {i} > ' 
                value = item[i]
                output += output_indent_string + key + _cc_item_helper(value, indent + len(key) ) + '\n'
            output += output_indent_string + '}\n'

        else:
            output = f"{item}\t"

        return output

    # Now process all the items...
    output = ""
    item_is_string = True
    for i in args:
        output += _cc_item_helper(i)
    print(output, flush=True)


def clear_console_os_command(command_title, cmd):
    """
    Clear console functions help produce readable console output that is comprhensive, verbose, and quick to follow. 

    The clear_console_os_command function executes an operating system command writes the ouput. 

    Parameters:
        command_title (string): A section title for the run of this command.
        cmd           (string): The actual operating system command to be ran.
    """
    clear_console_title(command_title, "START OF COMMAND")
    clear_console_item(cmd)
    os.system(cmd)
    clear_console_title(command_title, "END OF COMMAND")
