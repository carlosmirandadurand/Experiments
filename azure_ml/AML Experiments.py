
#%%
import os
from dotenv import load_dotenv

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Environment, BuildContext
from azure.ai.ml.entities import ComputeInstance, AmlCompute



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
    print(
        f"You already have a cluster named {ml_compute_name}, we'll reuse it as is."
    )

except Exception:
    ml_compute_instance = ComputeInstance(
        name=ml_compute_name, 
        size="Standard_NV6")
    print("Creating a new GPU compute instance...")
    ml_client.begin_create_or_update(ml_compute_instance)

print(
    f"Compute {ml_compute_instance.name} exists: state:{ml_compute_instance.state}, size:{ml_compute_instance.size}."
)




# %%

# Get a python environment environment (or create it, if it doesnt exist) 
custom_env_name = "cmd-aml-test-20230118-env"
dependencies_dir = "./dependencies"

try:
    pipeline_job_env = ml_client.environments.get(custom_env_name, label="latest")
    print(
        f"You already have an environment named {custom_env_name}, we'll reuse it as is."
    )

except Exception:
    pipeline_job_env = Environment(
        name=custom_env_name,
        description="Custom environment for Azure ML Service test",
        tags={"scikit-learn": "0.24.2"},
        conda_file=os.path.join(dependencies_dir, f"{custom_env_name}.yml"),
        image="mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu18.04:latest",
    )
    pipeline_job_env = ml_client.environments.create_or_update(pipeline_job_env)

print(
    f"Environment with name {pipeline_job_env.name} is registered to workspace, the version is {pipeline_job_env.version}"
)


# For reference only: Sample code to create a new python virtual environment in the cloud...

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



