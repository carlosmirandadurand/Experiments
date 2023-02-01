# Testing the Pythion SDK v2 
# Azure Machine Learning Service 


#%%
import os
from dotenv import load_dotenv
import pandas as pd

from azure.ai.ml import MLClient 
from azure.ai.ml import Input, Output
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.storage.blob import BlobClient
from azure.identity import DefaultAzureCredential

import mltable
from mltable import MLTableHeaders, MLTableFileEncoding


#%%
# Load Azure ML parameters from environment variables
load_dotenv()

subscription_id = os.getenv('az_subscription_id')
resource_group = os.getenv('aml_resource_group_name')
workspace = os.getenv('aml_workspace_name')



#%% 
# List the available compute nodes and environments (both curated and custom) in the Azure ML Service worspace 

ml_client = MLClient(
    DefaultAzureCredential(), subscription_id, resource_group, workspace
)




####################################################################################################################### 
# 
#  REGISTER DATA AS AZURE ML DATA ASSETS  
# 
####################################################################################################################### 


#%% 
# Register data from an external public url as an AzureML Data Asset

credit_data = Data(
    name = "creditcard_defaults",
    path = "https://archive.ics.uci.edu/ml/machine-learning-databases/00350/default%20of%20credit%20card%20clients.xls",
    type = AssetTypes.URI_FILE,
    description = "Dataset for credit card defaults",
    tags = {"source_type": "web", "source": "UCI ML Repo", "file_format": "csv"},
    version = "1.0.0",
)

credit_data = ml_client.data.create_or_update(credit_data)

print(
    f"Dataset with name {credit_data.name} was registered to workspace, the dataset version is {credit_data.version}"
)



#%%
# Register data from a Azure Storage Account as an AzureML Data Asset

housing_data = Data(
    name = "us_fhfa_hpi_master_new",
    path = "https://storageproactiveing01std.blob.core.windows.net/storage-container-data-science-001/hpi_data/hpi.csv",
    type = AssetTypes.URI_FILE,
    description = "Federal Housing Finance Agency (FHFA) House Price Indexes (HPIs)",
    tags = {"source_type": "web", "source": "FHFA Website", "file_format": "csv"},
    version = "2023.01.24",
)

housing_data = ml_client.data.create_or_update(housing_data)

print(
    f"Dataset with name {housing_data.name} was registered to workspace, the dataset version is {housing_data.version}"
)



####################################################################################################################### 
# 
#  CONSUMING AZURE ML DATA ASSETS  
# 
####################################################################################################################### 

#%%
# Read a registered AML dataset  

#aml_dataset = ml_client.data.get('us_fhfa_hpi_master_new', version='2023.01.24')
aml_dataset = ml_client.data.get('creditcard_defaults', version='1.0.0')

my_job_inputs = {
    "input_data": Input(type=AssetTypes.URI_FILE, path=aml_dataset.id)
}

print("dataset description:", aml_dataset.description)
print("dataset path:", aml_dataset.path)
print("dataset base_path:", aml_dataset.base_path)
print("dataset version:", aml_dataset.version)

print("\ninput items:", my_job_inputs.items())

# Input can be read from a job... 
#   parser = argparse.ArgumentParser()
#   parser.add_argument("--input_data", type=str)
#   args = parser.parse_args()
#   df = pd.read_csv(args.input_data)
#   print(df.head(10))



####################################################################################################################### 
# 
#  READING / LOADING / DOWNLOADING DATA 
# 
####################################################################################################################### 

#%%
# Read a single csv file directly into pandas (accessing data via http, but works the same for a local file)

file_name_iris = "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv"

df_iris = pd.read_csv(file_name_iris)
df_iris.shape



#%% 
# Read a csv file into a mtable and pandas (accessing data via http, but works the same for a local file)

file_path_iris = {
    'file': "https://azuremlexamples.blob.core.windows.net/datasets/iris.csv"
}

tbl_iris = mltable.from_delimited_files(
    paths =  [ file_path_iris ],
    header = MLTableHeaders.all_files_same_headers,
    delimiter = ',',
    encoding = MLTableFileEncoding.utf8,
    empty_as_string = False,
    include_path_column = False,
    infer_column_types = True,
    support_multi_line = False)

df_iris = tbl_iris.to_pandas_dataframe()
print("Shape:", df_iris.shape)




####################################################################################################################### 
# 
#  WRITING / SAVING / UPLOADING DATA / REGISTER DATA 
# 
####################################################################################################################### 


#%% 
# Save mtable locally
local_folder_iris = "downloads/iris"
tbl_iris.save(local_folder_iris) 


#%%
# Read again from the local definition (just a test)

tbl_new = mltable.load(local_folder_iris)
df_new = tbl_new.to_pandas_dataframe()
print(df_new.shape)

del tbl_new, df_new


#%% 
# Upload mtable to Azure Storage Account
storage_account_url = "https://storageproactiveing01std.blob.core.windows.net"
container_name = "storage-container-data-science-001"
data_folder_on_storage = 'iris_data'

blob_client = BlobClient(
    credential = DefaultAzureCredential(), 
    account_url = storage_account_url, 
    container_name = container_name,
    blob_name = f'{data_folder_on_storage}/MLTable'
)

with open(f'{local_folder_iris}/MLTable', "rb") as mltable_file:
    blob_client.upload_blob(mltable_file)

# TODO: DEBUG PERMISSIONS ISSUE



# %%
