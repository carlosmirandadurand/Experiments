import os
import shutil
import argparse
import pandas as pd
import torch
import tensorflow as tf

from pathlib import Path
from datetime import datetime
from uuid import uuid4
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pyvirtualdisplay import Display
    
import huggingface_hub as hf
from huggingface_hub import list_models
from huggingface_hub import hf_hub_download

# import mlflow
# import mlflow.sklearn
# from sklearn.ensemble import GradientBoostingClassifier
# from sklearn.metrics import classification_report
# from sklearn.model_selection import train_test_split


# Helper Functions 
# TODO: Replace with the clear console functions later
#       # Load helper functions from gist 
#       import requests
#       exec(requests.get("https://bit.ly/cmd-clear-console-output-latest").text)
def log_title(*args):
    print('-'*10, "LOG :", datetime.now(), ":", " / ".join(args), '-'*10, flush=True)

def log_item(*args):
    print("\t".join(args), flush=True)

def log_os_command(command_title, cmd):
    log_item("-" * 80)
    log_title(command_title)
    log_item(cmd)
    os.system(cmd)
    log_item("-" * 80, "\n")


# Main training function
def train():
    """Main function of the training script."""

    # Get input and output arguments
    # NOTE: Parameters passed from main largely unused (left for future use.) Currently, the real parameters come from a config file.
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="path to input data")
    parser.add_argument("--test_train_ratio", type=float, required=False, default=0.25)
    parser.add_argument("--n_estimators", required=False, default=100, type=int)
    parser.add_argument("--learning_rate", required=False, default=0.1, type=float)
    parser.add_argument("--registered_model_name", type=str, help="model name")
    parser.add_argument("--job_timestamp", type=str, help="timestamp to identify the job in output and UI")
    parser.add_argument("--key_vault_url", type=str, help="key vault URL")
    parser.add_argument("--model_output", type=str, help="Path of output model")
    args = parser.parse_args()

    # Show parametrs
    log_title("TRAINING SCRIPT... START!")
    log_item("SCRIPT PARAMETERS:")
    log_item("\n".join(f"{k} = {v}" for k, v in vars(args).items()))

    # Install git-lfs (zip file was uploaded with the remote scripts / TODO: install in the Azure custom environment)
    log_os_command("EXTRACT:", "cd downloads/ && tar -xf git-lfs-linux-amd64-v3.3.0.tar.gz && cd git-lfs-3.3.0 && ./install.sh && cd ../.. && pwd && echo GIT_LFS Installed")
    log_os_command("INITIALIZE GIT",     'git config --global credential.helper store')
    log_os_command("INITIALIZE GIT-LFS", 'git lfs install')
    
    # Load RL libraries
    log_os_command("CLONE STABLE BASELINES 3 ZOO", "git clone https://github.com/DLR-RM/rl-baselines3-zoo")
    # pip install -r requirements.txt   # not needed - packages were installed when creating the custom python environment

    # Load credentials from Azure Identity and Connect to HF
    log_title("CONNECTING TO HUGING FACE...")    
    aml_credential = DefaultAzureCredential()
    aml_secret_client = SecretClient(vault_url = args.key_vault_url, credential = aml_credential)
    hf_access_token = aml_secret_client.get_secret("hf-access-token")
    hf_access_token = hf_access_token.value
    log_item("Hugging Face Access Token", hf_access_token[-2:])
    hf.login(token = hf_access_token, add_to_git_credential = True)
    log_item("Hugging Face login complete...")
    hf_models = list_models()
    hf_hub_download(repo_id="carlosmirandad/rl-class-q-taxi-v3", filename="replay.mp4")
    log_item("Hugging Face pre-checks complete...")

    # Record everything in the environment in case we need to troubleshoot later
    log_os_command("OPERATING SYSTEM", 'cat /etc/*-release')
    log_os_command("HARDWARE: CPU",    'cat /proc/cpuinfo')
    log_os_command("HARDWARE: GPU",    'nvidia-smi')
    log_os_command("ALIASES",          'alias')
    log_os_command("USER",             'whoami')
    log_item("CURRENT DIRECTORY ",  os.getcwd(), "\n")

    log_os_command("VERSIONS",         'python --version')
    log_item("PyTorch ", torch.__version__)
    log_item("TensorFlow ", tf.__version__, "\n")

    log_os_command("PROCESSES",          'ps -aux')
    log_os_command("DISK SPACE",         'df -h')

    log_os_command("PIP FREEZE SNAPHOT", 'pip freeze > snapshot_requirements.txt && cat snapshot_requirements.txt')
    log_os_command("APT LIST SNAPHOT",   "apt list --installed | sed s/Listing...// | awk -F '/' '{print $1}' > snapshot_apt_installed_packages.txt && cat snapshot_apt_installed_packages.txt")

    log_os_command("ROOT DIRECTORY CONTENTS",          'ls -al /') 
    log_os_command("AML MOUNTS FULL CONTENTS",         'ls -alR /mnt/azureml/ ') 
    log_os_command("CURRENT DIRECTORY FULL CONTENTS",  'ls -alR')
    
    # Modify RL parameters
    log_title("CONFIGURING THE RL BASELINES ZOO JOBS...")
    os.chdir( os.path.join(os.getcwd(), "rl-baselines3-zoo")  )
    log_os_command("CURRENT DIRECTORY",              "pwd")
    log_os_command("PRINT ORIGINAL DQN PARAMETERS",  "cat ./hyperparams/dqn.yml")
    log_os_command("UPDATE DQN PARAMETERS",          "cp ../dqn_modified.yml ./hyperparams/dqn.yml")
    log_os_command("PRINT MODIFIED DQN PARAMETERS",  "cat ./hyperparams/dqn.yml")

    # Initialize virtual display
    log_title("Virtual display")
    virtual_display = Display(visible=0, size=(1400, 900))
    virtual_display.start()

    # Train and evaluate the agent
    model_output_subdirectory = "logs/dqn/"
    log_os_command("TRAIN RL AGENT",    "python train.py --algo dqn --env SpaceInvadersNoFrameskip-v4  -f logs/ ")
    log_os_command("VALIDATE RL AGENT", "python enjoy.py --algo dqn --env SpaceInvadersNoFrameskip-v4  --no-render  --n-timesteps 5000  --folder logs/ ")
    log_os_command("LOCAL OUTPUT FULL CONTENTS", f"ls -alR {model_output_subdirectory} ")
    
    # Save model output
    model_output_external_path = os.path.join(
        args.model_output, 
        f"output_{args.registered_model_name}_{args.job_timestamp}",
        model_output_subdirectory)
    log_item("Saving model outputs to path:", model_output_external_path)
    shutil.copytree(model_output_subdirectory, model_output_external_path)
    log_os_command("EXTERNAL OUTPUT FULL CONTENTS", f"ls -alR {model_output_external_path} ")

    # Upload model to Hugging Face Hub.
    log_os_command("PUBLISH RL AGENT", "python -m rl_zoo3.push_to_hub --algo dqn --env SpaceInvadersNoFrameskip-v4 --repo-name rl-class-dqn-SpaceInvadersNoFrameskip-v4 -orga carlosmirandad -f logs/ ")

    # End of training
    log_title("TRAINING SCRIPT... END!")


if __name__ == "__main__":
    train()