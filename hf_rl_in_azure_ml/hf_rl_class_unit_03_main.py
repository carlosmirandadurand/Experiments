# Hugging Face Reiforcement Lerning Class 
# Running on Azure Machine Learning Service
# Unit3: Deep Q-Learning with Atari games 
# Home Page: https://huggingface.co/deep-rl-course/unit3/introduction?fw=pt
# Source: https://colab.research.google.com/github/huggingface/deep-rl-class/blob/main/notebooks/unit3/unit3.ipynb

#%%
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import uuid

from azure.ai.ml import MLClient
from azure.ai.ml import command
from azure.ai.ml import Input
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment, BuildContext
from azure.ai.ml.entities import ComputeInstance, AmlCompute
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model


#%%

# Load Azure ML parameters from environment variables
load_dotenv()

aml_subscription_id = os.getenv('aml_subscription_id')
aml_resource_group_name = os.getenv('aml_resource_group_name')
aml_workspace_name = os.getenv('aml_workspace_name')
aml_compute_name = os.getenv('aml_compute_name_gpu')
aml_environment_name = os.getenv('aml_environment_name_rl')
aml_environment_label = os.getenv('aml_environment_label_rl')
hf_access_token = os.getenv('hf_access_token')

print("Loaded process paramenetrs from environment file.")


#%%

aml_command_display_name = f"HF RL Course - Unit 03 - Training Job {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
aml_experiment_name = 'hf_rl_class_unit_03_experiment'
aml_model_name = "hf_rl_class_unit_03_model" 

training_script_folder = "./scripts/"
training_script_name = "hf_rl_class_unit_03_train.py"

training_data = Input(
        type="uri_file",
        path="https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls",
    )

training_input_parameters = dict(
        data = training_data,
        test_train_ratio = 0.2,
        learning_rate = 0.25,
        registered_model_name = aml_model_name,
    )

training_command = "python " + training_script_name \
    + " --data ${{inputs.data}}" \
    + " --test_train_ratio ${{inputs.test_train_ratio}}" \
    + " --learning_rate ${{inputs.learning_rate}}" \
    + " --registered_model_name ${{inputs.registered_model_name}}"


#%%

# List the available compute nodes and environments (both curated and custom) in the Azure ML Service worspace 

ml_client = MLClient(
    DefaultAzureCredential(), aml_subscription_id, aml_resource_group_name, aml_workspace_name
)

for i in ml_client.compute.list():
    print("Compute:", i.name)

for i in ml_client.environments.list():
    print("Environment:", i.name)


#%%

# Get handle to the GPU compute instance 
ml_compute_instance = ml_client.compute.get(aml_compute_name)
print(f"Compute {ml_compute_instance.name}: state:{ml_compute_instance.state}, size:{ml_compute_instance.size}.")

if ml_compute_instance.state == "Stopped":
    print("Starting GPU compute instance...")
    ml_client.compute.begin_start(aml_compute_name).wait()
    ml_compute_instance = ml_client.compute.get(aml_compute_name)
    print(f"Compute {ml_compute_instance.name}: state:{ml_compute_instance.state}.")


# %%

# Get handle to the python environment environment 
pipeline_job_env = ml_client.environments.get(aml_environment_name, label=aml_environment_label)
print(f"Environment with name {pipeline_job_env.name} is registered to workspace, the version is {pipeline_job_env.version}")



#%%

# Execute....
print(f"Run training command {command}...")
training_job_command = command(
        inputs = training_input_parameters,
        code = training_script_folder, 
        command = training_command,
        environment = f"{pipeline_job_env.name}:{pipeline_job_env.version}",
        compute = aml_compute_name,
        experiment_name = aml_experiment_name,
        display_name = aml_command_display_name,
    )

training_job_resource = ml_client.create_or_update(training_job_command)
print(f'Training command created. Job {training_job_resource.name} is {training_job_resource.status}...')


#%%

# Check progress until job has finished running....
while True:
    job_status = ml_client.jobs.get(training_job_resource.name).status
    if job_status not in ['Provisioning', 'Queued', 'Preparing', 'Starting', 'Running', 'Finalizing']:
        break
    print(f"Training Job Status: {job_status}")
    time.sleep(30)

print(f"Training Job FINAL STATUS: {ml_client.jobs.get(training_job_resource.name).status}")


#%%

# END!  Stop the compute instance when the script is over. 
if ml_compute_instance.state == "Running":
    print("Stopping GPU compute instance...")
    ml_client.compute.begin_stop(aml_compute_name).wait()
    ml_compute_instance = ml_client.compute.get(aml_compute_name)
    print(f"Compute {ml_compute_instance.name}: state:{ml_compute_instance.state}.")


print("END!")

