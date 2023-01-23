import os
import time
import argparse
import pandas as pd

from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# import mlflow
# import mlflow.sklearn
# from sklearn.ensemble import GradientBoostingClassifier
# from sklearn.metrics import classification_report
# from sklearn.model_selection import train_test_split

import torch
import tensorflow as tf
import huggingface_hub as hf


 # Helper Functions
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="path to input data")
    parser.add_argument("--test_train_ratio", type=float, required=False, default=0.25)
    parser.add_argument("--n_estimators", required=False, default=100, type=int)
    parser.add_argument("--learning_rate", required=False, default=0.1, type=float)
    parser.add_argument("--registered_model_name", type=str, help="model name")
    args = parser.parse_args()

    # Show parametrs
    log_title("TRAINING SCRIPT... START!")
    log_item("SCRIPT PARAMETERS:")
    log_item("\n".join(f"{k} = {v}" for k, v in vars(args).items()))

    # Record environment
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
    log_os_command("PIP FREEZE SNAPHOT", 'pip freeze > snapshot_requirements.txt && cat snapshot_requirements.txt')
    log_os_command("APT LIST SNAPHOT",   "apt list --installed | sed s/Listing...// | awk -F '/' '{print $1}' > snapshot_apt_installed_packages.txt && cat snapshot_apt_installed_packages.txt")
    log_os_command("ROOT DIRECTORY CONTENTS",           'ls -al /')
    log_os_command("CURRENT DIRECTORY FULL CONTENTS",   'ls -alR')
    
    # Load RL libraries
    log_os_command("CLONE STABLE BASELINES 3 ZOO", "git clone https://github.com/DLR-RM/rl-baselines3-zoo")
    log_os_command("CURRENT DIRECTORY FULL CONTENTS",   'ls -alR')
    # !pip install -r requirements.txt already in the image


    # Modify RL parameters
    log_title("UPDATING JOB PARAMETERS")
    os.chdir( os.path.join(os.getcwd(), "rl-baselines3-zoo")  )
    log_os_command("CURRENT DIRECTORY",               "pwd")
    log_os_command("PRINT ORIGINAL DQN PARAMETERS",  "cat ./hyperparams/dqn.yml")
    log_os_command("UPDATE DQN PARAMETERS",          "cp ../dqn_modified.yml ./hyperparams/dqn.yml")
    log_os_command("PRINT MODIFIED DQN PARAMETERS",  "cat ./hyperparams/dqn.yml")

    # Initialize virtual display
    log_title("Virtual display")
    from pyvirtualdisplay import Display
    virtual_display = Display(visible=0, size=(1400, 900))
    virtual_display.start()


    # Train & evaluate the agent
    log_os_command("TRAIN AGENT",    "python train.py --algo dqn --env SpaceInvadersNoFrameskip-v4  -f logs/ ")
    log_os_command("VALIDATE AGENT", "python enjoy.py --algo dqn --env SpaceInvadersNoFrameskip-v4  --no-render  --n-timesteps 5000  --folder logs/ ")
    
    # # Log to Hugging Face account to be able to upload models to the Hub.
    # credential = DefaultAzureCredential()
    # secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
    # hf.login(token = z, add_to_git_credential = True)
    # log_os_command("PUBLICH AGENT", "python -m rl_zoo3.push_to_hub --algo dqn --env SpaceInvadersNoFrameskip-v4 --repo-name rl-class-dqn-SpaceInvadersNoFrameskip-v4 -orga carlosmirandad -f logs/ ")
 
    # End of training
    log_title("TRAINING SCRIPT... END!")


if __name__ == "__main__":
    train()