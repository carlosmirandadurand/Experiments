import os
from datetime import datetime
import argparse
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

import torch
import tensorflow as tf



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
    log_title("SCRIPT PARAMETERS")
    log_item("\n".join(f"{k} = {v}" for k, v in vars(args).items()))

    # Record environment
    log_os_command("OPERATING SYSTEM", 'cat /etc/*-release')
    log_os_command("HARDWARE: CPU",    'cat /proc/cpuinfo')
    log_os_command("HARDWARE: GPU",    'nvidia-smi')
    log_os_command("PROCESSES",        'ps -aux')

    log_os_command("VERSIONS",         'python --version')
    log_item("PyTorch ", torch.__version__)
    log_item("TensorFlow ", tf.__version__, "\n")

    log_os_command("PIP FREEZE SNAPHOT", 'pip freeze > snapshot_requirements.txt && cat snapshot_requirements.txt')
    log_os_command("APT LIST SNAPHOT",   "apt list --installed | sed s/Listing...// | awk -F '/' '{print $1}' > snapshot_apt_installed_packages.txt && cat snapshot_apt_installed_packages.txt")

    log_os_command("USER",               'whoami')
    log_os_command("CURRENT DIRECORY",   'pwd')
    log_os_command("DIRECORY CONTENTS",  'ls -alR')
    log_os_command("ALL PYTHON FILES",   'find / -name *.py')


    #     # Virtual display
    #     from pyvirtualdisplay import Display
    #     virtual_display = Display(visible=0, size=(1400, 900))
    #     virtual_display.start()

    #     #define the hyperparameters in rl-baselines3-zoo/hyperparams/dqn.yml

    #     # Train the agent
    #    !python train.py --algo dqn --env SpaceInvadersNoFrameskip-v4  -f logs/

    #     # Evaluate agent
    #     !python enjoy.py  --algo dqn  --env SpaceInvadersNoFrameskip-v4  --no-render  --n-timesteps 5000  --folder logs/

    #     # Publish agent
    #     from huggingface_hub import notebook_login # To log to our Hugging Face account to be able to upload models to the Hub.
    #     notebook_login()
    #     !git config --global credential.helper store
    #     !python -m rl_zoo3.push_to_hub  --algo dqn  --env SpaceInvadersNoFrameskip-v4  --repo-name dqn-SpaceInvadersNoFrameskip-v4  -orga ThomasSimonini  -f logs/

    # End of training
    log_title("TRAINING SCRIPT... END!")


if __name__ == "__main__":
    train()