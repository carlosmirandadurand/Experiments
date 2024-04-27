
import os
import time

import threading
from queue import Queue

from dotenv import load_dotenv
from datetime import datetime

import random


    
#####################################################################################
# Load Process parameters
#####################################################################################

load_dotenv()

time_stamp = datetime.today().strftime('%Y%m%d_%H%M%S')
n_max_threads = 32

g_base_output_directory  = os.getenv('OUTPUT_DIRECTORY', '.')
g_base_output_directory  = os.path.join(g_base_output_directory, 'downloads', f'job_{time_stamp}')


# Make file writing thread-safe (if different threads could save to same file)
lock = threading.Lock()


#####################################################################################
# Define functions
#####################################################################################

def run_query(query):

    # Totally dummy function (replace your thread execution code here...)
    log_message = f'{datetime.today()}: run_query started with parameter {query}. Not really executing any query. This is a dummy function just waiting {query} seconds.'
    result = f'run_query waited {query} seconds.'

    # Do the hard work
    time.sleep(query)
    
    # Persist results
    output_directory = os.path.join(g_base_output_directory, f'query_{query}')
    output_file = os.path.join(output_directory, f'log_{query}.txt')

    with lock:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        with open(output_file, "a") as f:
            f.write(log_message)
            f.write('\n')

    return result



def run_query__parallel_worker__helper_function (
            query_queue, 
            result_queue, 
            print_to_console = False,
            ):
    while not query_queue.empty():
        query = query_queue.get()
        try:
            if print_to_console:
                print(f"Starting query in parallel:\n{query}\n\n", flush=True)
            result = run_query(query)
            result_queue.put(result)
            if print_to_console:
                print(f"Finished query:\n{query}\nResult:\n{result}\n\n", flush=True)
        finally:
            query_queue.task_done()



def run_queries_in_parallel (
            list_of_sql_select_statements, 
            n_threads, 
            ):

    # Create thread-safe queues to store inputs & outputs
    result_queue = Queue()
    query_queue = Queue()
    for query in list_of_sql_select_statements:
        query_queue.put(query)

    # Create threads running in parallel
    threads = []
    for _ in range(n_threads):
        thread = threading.Thread(
                        target = run_query__parallel_worker__helper_function, 
                        args = (    query_queue, 
                                    result_queue 
                                ))
        thread.start()
        threads.append(thread)

    # Wait for all tasks in the queue to be complete 
    query_queue.join()
    for thread in threads:
        thread.join()

    # Retrieve results from result queue
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    return results


#####################################################################################
# Execute 
#####################################################################################

list_of_queries = [random.randint(1, 10) for _ in range(100)]  # Dummy example

print('list_of_queries:', list_of_queries, "\n")

final_results = run_queries_in_parallel(
    list_of_queries,
    n_max_threads,
    )

for index, value in enumerate(final_results):
    print(f"#{index+1}: {value}")

