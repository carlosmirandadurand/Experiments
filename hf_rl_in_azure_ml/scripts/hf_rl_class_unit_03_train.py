import os
import argparse
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

import torch
import tensorflow as tf


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
    print("TRAINING SCRIPT... START!")
    print(" ".join(f"{k}={v}" for k, v in vars(args).items()))


    #     # Show environment
    #     !cat /etc/*-release
    #     !cat /proc/cpuinfo
    #     !nvidia-smi
    #     !whoami
    #     !python --version
    #     !pip freeze > requirements_first_layer.txt
    #     !apt list --installed | sed s/Listing...// | awk -F "/" '{print $1}' > apt_installed_packages_first_later.txt
    #     print(torch.__version__)
    #     print(tf.__version__)


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
    print("TRAINING SCRIPT... END!")


if __name__ == "__main__":
    train()