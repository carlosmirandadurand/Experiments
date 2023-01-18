
#%%
import os
from dotenv import load_dotenv


#%%
# Load environment variables
load_dotenv()

subscription_id = os.getenv('aml_subscription_id')
resource_group = os.getenv('aml_resource_group')
workspace = os.getenv('aml_workspace')



#%%
# List Azure ML Service compute nodes and environments (curated and custom) 
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment, BuildContext
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(), subscription_id, resource_group, workspace
)

for i in ml_client.compute.list():
    print("Compute:", i.name)

for i in ml_client.environments.list():
    print("Env:", i.name)



# %%
# For reference only... creating environments...

# # Create a custom environment from a docker image
# env_docker_image = Environment(
#     image="pytorch/pytorch:latest",
#     name="CMD-pytorch-docker-image-example",
#     description="Environment created from a Docker image.",
# )
# #ml_client.environments.create_or_update(env_docker_image)

# # Create a custom environment from Docker build context
# env_docker_context = Environment(
#     build=BuildContext(path="docker-contexts/python-and-pip"),
#     name="CMD-python-docker-context-example",
#     description="Environment created from a Docker context.",
# )
# ml_client.environments.create_or_update(env_docker_context)

# # Create environment from docker image with a conda YAML
# env_docker_conda = Environment(
#     image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
#     conda_file="conda-yamls/pydata.yml",
#     name="CMD-python-docker-image-plus-conda-example",
#     description="Environment created from a Docker image plus Conda environment.",
# )
# ml_client.environments.create_or_update(env_docker_conda)


