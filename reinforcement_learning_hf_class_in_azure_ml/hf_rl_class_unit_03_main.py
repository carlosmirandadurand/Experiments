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
from azure.ai.ml import Input, Output
from azure.ai.ml.entities import Environment, BuildContext
from azure.ai.ml.entities import ComputeInstance, AmlCompute
from azure.ai.ml.entities import ManagedOnlineEndpoint, ManagedOnlineDeployment, Model
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient



#%%
# Load Azure ML parameters from environment variables

load_dotenv()

az_subscription_id = os.getenv('az_subscription_id')
aml_resource_group_name = os.getenv('aml_resource_group_name')
aml_workspace_name = os.getenv('aml_workspace_name')
aml_compute_name = os.getenv('aml_compute_name_gpu')
aml_environment_name = os.getenv('aml_environment_name_rl')
aml_environment_label = os.getenv('aml_environment_label_rl')
aml_key_vault_url = os.getenv('aml_key_vault_url')
hf_access_token = os.getenv('hf_access_token')

print("Loaded process paramenetrs from environment file.")


#%%
# Securely store Hugging Face access token 

aml_credential = DefaultAzureCredential()
aml_secret_client = SecretClient(vault_url = aml_key_vault_url, credential = aml_credential)
#aml_secret_client.set_secret("hf-access-token", hf_access_token)  # Uncomment when the secret changes

print("Handled Hugging Face access token.")


#%%
# Set input / output parameters for the training job (largely unused / illustrative only)

job_timestamp = datetime.now()

aml_command_display_name = f"HF RL Course - Unit 03 - Training Job {job_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
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
        key_vault_url = aml_key_vault_url,
        job_timestamp = job_timestamp.strftime('%Y%m%d_%H%M%S'),
    )

training_output_parameters = dict(
    model_output = Output(
        type=AssetTypes.URI_FOLDER,
        path=f"azureml://subscriptions/{az_subscription_id}/resourcegroups/{aml_resource_group_name}/workspaces/{aml_workspace_name}/datastores/workspaceblobstore/paths/",
        )
    )



#%%
# Get workspace handle. List available compute nodes and custom environments (not curated) in the Azure ML Service worspace 

ml_client = MLClient(
    DefaultAzureCredential(), az_subscription_id, aml_resource_group_name, aml_workspace_name
)

for i in ml_client.compute.list():
    print("Compute:", i.name)

for i in ml_client.environments.list():
    if "AzureML-" not in i.name:
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
# Execute!!! launch the remote training job...

print(f"Run training command...")

training_command = "python " + training_script_name \
    + " --data ${{inputs.data}}" \
    + " --test_train_ratio ${{inputs.test_train_ratio}}" \
    + " --learning_rate ${{inputs.learning_rate}}" \
    + " --registered_model_name ${{inputs.registered_model_name}}" \
    + " --job_timestamp ${{inputs.job_timestamp}}" \
    + " --key_vault_url ${{inputs.key_vault_url}}" \
    + " --model_output ${{outputs.model_output}}" 
    

training_job_command = command(
        inputs = training_input_parameters,
        outputs = training_output_parameters,
        code = training_script_folder, 
        command = training_command,
        environment = f"{pipeline_job_env.name}:{pipeline_job_env.version}",
        compute = aml_compute_name,
        experiment_name = aml_experiment_name,
        display_name = aml_command_display_name,
    )

training_job_resource = ml_client.create_or_update(training_job_command)
print(f'Training command created. Job {training_job_resource.name} is {training_job_resource.status}...')

training_job_url = training_job_resource.services["Studio"].endpoint
print(f'URL for the status of the training job {training_job_url}  ')


#%%
# Check progress until job has finished running....

i = 0
while True:
    job_status = ml_client.jobs.get(training_job_resource.name).status
    if job_status not in ['Provisioning', 'Queued', 'Preparing', 'Starting', 'Running', 'Finalizing']:
        print(f"Exit Condition Met {i}: {job_status}")
        break
    print(f"Training Job Status {i}: {job_status}")
    time.sleep(60)
    i = i + 1
    if i > 60*24*2:
        print(f"Timeout Condition")
        break 

print(f"Training Job FINAL STATUS: {ml_client.jobs.get(training_job_resource.name).status}")


#%%
# END!  Stop the compute instance when the script is over. 

if ml_compute_instance.state == "Running":
    print("Stopping GPU compute instance...")
    ml_client.compute.begin_stop(aml_compute_name).wait()
    ml_compute_instance = ml_client.compute.get(aml_compute_name)
    print(f"Compute {ml_compute_instance.name}: state:{ml_compute_instance.state}.")


print("END!")

