# Testing the Pythion SDK v2 
# Azure Machine Learning Service 
# Source: https://learn.microsoft.com/en-us/azure/machine-learning/tutorial-azure-ml-in-a-day


#%%
import os
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

subscription_id = os.getenv('aml_subscription_id')
resource_group = os.getenv('aml_resource_group')
workspace = os.getenv('aml_workspace')



#%%

# List the available compute nodes and environments (both curated and custom) in the Azure ML Service worspace 

ml_client = MLClient(
    DefaultAzureCredential(), subscription_id, resource_group, workspace
)

for i in ml_client.compute.list():
    print("Compute:", i.name)

for i in ml_client.environments.list():
    print("Environment:", i.name)


#%%

# Get a GPU compute instance (or create it, if it doesnt exist) 
ml_compute_name = "compins-carlosm-gpu-nv6"

try:
    ml_compute_instance = ml_client.compute.get(ml_compute_name)
    print(f"You already have a compute named {ml_compute_name}, we'll reuse it as is.")

except Exception:
    ml_compute_instance = ComputeInstance(
        name=ml_compute_name, 
        size="Standard_NV6")
    print("Creating a new GPU compute instance...")
    ml_client.begin_create_or_update(ml_compute_instance)

print(f"Compute {ml_compute_instance.name}: state:{ml_compute_instance.state}, size:{ml_compute_instance.size}.")

if ml_compute_instance.state == "Stopped":
    print("Starting GPU compute instance...")
    ml_client.compute.begin_start(ml_compute_name).wait()
    ml_compute_instance = ml_client.compute.get(ml_compute_name)
    print(f"Compute {ml_compute_instance.name}: state:{ml_compute_instance.state}.")


# %%

# Get a python environment environment (or create it, if it doesnt exist) 
custom_env_name = "cmd-aml-test-20230118-env"
dependencies_dir = "./dependencies"

try:
    pipeline_job_env = ml_client.environments.get(custom_env_name, label="latest")
    print(f"You already have an environment named {custom_env_name}, we'll reuse it as is.")

except Exception:
    pipeline_job_env = Environment(
        name=custom_env_name,
        description="Custom environment for Azure ML Service test",
        tags={"scikit-learn": "0.24.2"},
        conda_file=os.path.join(dependencies_dir, f"{custom_env_name}.yml"),
        image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04:latest",
    )
    pipeline_job_env = ml_client.environments.create_or_update(pipeline_job_env)

print(f"Environment with name {pipeline_job_env.name} is registered to workspace, the version is {pipeline_job_env.version}")


# For reference: Sample code to create new python virtual environments in various ways...

# # Create a custom environment from a docker image:
# env_docker_image = Environment(
#     image="pytorch/pytorch:latest",
#     name="CMD-pytorch-docker-image-example",
#     description="Environment created from a Docker image.",
# )
# #ml_client.environments.create_or_update(env_docker_image)

# # Create a custom environment from a docker image + conda YAML:
# env_docker_conda = Environment(
#     image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
#     conda_file="conda-yamls/pydata.yml",
#     name="CMD-python-docker-image-plus-conda-example",
#     description="Environment created from a Docker image plus Conda environment.",
# )
# ml_client.environments.create_or_update(env_docker_conda)

# # Create a custom environment from a Docker build context:
# env_docker_context = Environment(
#     build=BuildContext(path="docker-contexts/python-and-pip"),
#     name="CMD-python-docker-context-example",
#     description="Environment created from a Docker context.",
# )
# ml_client.environments.create_or_update(env_docker_context)


#%%

ml_model_name = "cmd_aml_test_credit_defaults_model" 

training_script_folder = "./scripts/"

training_script_name = "credit_classification_train.py"

training_data = Input(
        type="uri_file",
        path="https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls",
    )

training_input_parameters = dict(
        data = training_data,
        test_train_ratio = 0.2,
        learning_rate = 0.25,
        registered_model_name = ml_model_name,
    )

training_command = "python " + training_script_name \
    + " --data ${{inputs.data}}" \
    + " --test_train_ratio ${{inputs.test_train_ratio}}" \
    + " --learning_rate ${{inputs.learning_rate}}" \
    + " --registered_model_name ${{inputs.registered_model_name}}"

training_job = command(
        inputs = training_input_parameters,
        code = training_script_folder, 
        command = training_command,
        environment = f"{pipeline_job_env.name}@latest",
        compute = ml_compute_name,
        experiment_name = "cmd_aml_test_train_model_credit_default_prediction",
        display_name = "CMD AML Test: credit_default_prediction",
    )

# Uncomment to re-run....
# ml_client.create_or_update(training_job)


#%%

# Creating an online endpoint to serve the model for inference

online_endpoint_name = "credit-endpoint-" + str(uuid.uuid4())[:8]

endpoint = ManagedOnlineEndpoint(
    name = online_endpoint_name,
    description = "CMD AML Test online endpoint for credit application",
    auth_mode="key",
    tags={
        "training_dataset": "credit_defaults",
        "model_type": "sklearn.GradientBoostingClassifier",
    },
)

endpoint = ml_client.online_endpoints.begin_create_or_update(endpoint).result()

print(f"Endpoint {endpoint.name} provisioning state: {endpoint.provisioning_state}")



#%%

# Retrieve the online endpoint and publish model for inference

endpoint = ml_client.online_endpoints.get(name = online_endpoint_name)

print(f'Endpoint "{endpoint.name}" with provisioning state "{endpoint.provisioning_state}" is retrieved')

latest_model_version = max(
    [int(m.version) for m in ml_client.models.list(name=ml_model_name)]
)

print(f"Latest version of model: {latest_model_version}")

ml_model_for_inference = ml_client.models.get(name=ml_model_name, version=latest_model_version)

blue_deployment = ManagedOnlineDeployment(
    name = "blue",
    endpoint_name = online_endpoint_name,
    model = ml_model_for_inference,
    instance_type = "Standard_DS3_v2",
    instance_count = 1,
)

# # Uncomment when quota has been raised...
# blue_deployment = ml_client.begin_create_or_update(blue_deployment).result()


#%%

# Test the blue deployment with some sample data
ml_client.online_endpoints.invoke(
    endpoint_name = online_endpoint_name,
    request_file = "./deploy/credit_sample_request-request.json",
    deployment_name = "blue",
)



#%%

# Cleanup

ml_client.online_endpoints.begin_delete(name=online_endpoint_name)



#%%

# END!  Stop the compute instance when the script is over. 

if ml_compute_instance.state == "Running":
    print("Stopping GPU compute instance...")
    ml_client.compute.begin_stop(ml_compute_name).wait()
    ml_compute_instance = ml_client.compute.get(ml_compute_name)
    print(f"Compute {ml_compute_instance.name}: state:{ml_compute_instance.state}.")



# %%
