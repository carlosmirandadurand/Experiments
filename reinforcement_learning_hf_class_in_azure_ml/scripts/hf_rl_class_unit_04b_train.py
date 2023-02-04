import os
import shutil
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import json
import tempfile

from pathlib import Path
from datetime import datetime
from collections import deque
from uuid import uuid4

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

import imageio
from pyvirtualdisplay import Display

import tensorflow as tf
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Categorical

import huggingface_hub as hf
from huggingface_hub import list_models, hf_hub_download
from huggingface_hub import HfApi, snapshot_download
from huggingface_hub.repocard import metadata_eval_result, metadata_save

import gym
import gym_pygame


# import mlflow
# import mlflow.sklearn
# from sklearn.ensemble import GradientBoostingClassifier
# from sklearn.metrics import classification_report
# from sklearn.model_selection import train_test_split

# Load helper functions from gist
try: 
    import requests
    exec(requests.get("https://bit.ly/cmd-clear-console-output-latest").text)
except:
    pass

# Load helper functions from local directory
try:
    from z_gists.clear_console_output import clear_console_item, clear_console_os_command, clear_console_title
except:
    pass


######################## GLOBAL VARIABLES ##########################################################

# Real training parameters are harcoded for now.  Some variables are global for now.  Script parameters most are ignored.  
# TODO: 
#    - Pass values via param from the local script
#    - Remove unsused script parameters
#    - use optuna for tunning
#    - Ensure functions are not relying on global variables

# Create the envs
env_id   = "Pixelcopter-PLE-v0"
env      = gym.make(env_id)
eval_env = gym.make(env_id)


# CUDA device, if available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
clear_console_item("GPU check from pytorch", device)



######################## SCRIPT CLASSES AND FUNCTIONS ##########################################################

class Policy(nn.Module):
    def __init__(self, s_size, a_size, h_size):
        super(Policy, self).__init__()
        # Define the three layers here
        self.fc1 = nn.Linear(s_size,   h_size)
        self.fc2 = nn.Linear(h_size,   h_size*2)
        self.fc3 = nn.Linear(h_size*2, a_size)

    def forward(self, x):
        # Define the forward process here
        x = F.Relu(self.fc1(x))
        x = F.Relu(self.fc2(x))
        return F.softmax(self.fc3(x), dim=1)
    
    def act(self, state):
        state = torch.from_numpy(state).float().unsqueeze(0).to(device)
        probs = self.forward(state).cpu()
        m = Categorical(probs)
        action = m.sample()
        return action.item(), m.log_prob(action)


def reinforce(env, policy, optimizer, n_training_episodes, max_t, gamma, print_every):
    # Help us to calculate the score during the training
    full_scores_deque = deque(maxlen=100)
    full_scores_list = []

    # Line 3 of pseudocode (iterate for N episodes)
    for i_episode in range(1, n_training_episodes+1):
        episode_saved_log_probs = []
        episode_rewards = []
        state = env.reset()

        # Line 4 of pseudocode (one complete episode)
        for t in range(max_t):
            action, log_prob = policy.act(state)
            state, reward, done, _ = env.step(action)
            episode_saved_log_probs.append(log_prob)
            episode_rewards.append(reward)
            if done:
                break 
        
        full_scores_deque.append(sum(episode_rewards))
        full_scores_list.append(sum(episode_rewards))
        
        # Line 5-6 of pseudocode: calculate discounted future returns for each step (from current step til end of episode)
        episode_future_returns = deque(maxlen=max_t)
        for t in range(len(episode_rewards))[::-1]:
            cumm_discounted_future_return_t = (episode_future_returns[0] if len(episode_future_returns)>0 else 0)
            episode_future_returns.appendleft(episode_rewards[t] + gamma * cumm_discounted_future_return_t)
       
        # standardization of the returns to make training more stable
        eps = np.finfo(np.float32).eps.item()  # smallest representable float (added for numerical stability)
        episode_future_returns = torch.tensor(episode_future_returns)
        episode_future_returns = (episode_future_returns - episode_future_returns.mean()) / (episode_future_returns.std() + eps)
        
        # Line 7:
        policy_loss = []
        for log_prob, disc_return in zip(episode_saved_log_probs, episode_future_returns):
            policy_loss.append(-log_prob * disc_return)
        policy_loss = torch.cat(policy_loss).sum()
        
        # Line 8: PyTorch prefers gradient descent 
        optimizer.zero_grad()
        policy_loss.backward()
        optimizer.step()
        
        if i_episode % print_every == 0:
            clear_console_title('Episode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(full_scores_deque)))
        
    return full_scores_list


def evaluate_agent(env, max_steps, n_eval_episodes, policy):
  """
  Evaluate the agent for ``n_eval_episodes`` episodes and returns average reward and std of reward.
  :param env: The evaluation environment
  :param n_eval_episodes: Number of episode to evaluate the agent
  :param policy: The Reinforce agent
  """
  episode_rewards = []
  for episode in range(n_eval_episodes):
    state = env.reset()
    step = 0
    done = False
    total_rewards_ep = 0
    
    for step in range(max_steps):
      action, _ = policy.act(state)
      new_state, reward, done, info = env.step(action)
      total_rewards_ep += reward
        
      if done:
        break
      state = new_state
    episode_rewards.append(total_rewards_ep)
  mean_reward = np.mean(episode_rewards)
  std_reward = np.std(episode_rewards)

  return mean_reward, std_reward


def record_video(env, policy, out_directory, fps=30):
    """
    Generate a replay video of the agent
    :param env
    :param Qtable: Qtable of our agent
    :param out_directory
    :param fps: how many frame per seconds (with taxi-v3 and frozenlake-v1 we use 1)
    """
    images = []  
    done = False
    state = env.reset()
    img = env.render(mode='rgb_array')
    images.append(img)
    while not done:
        # Take the action (index) that have the maximum expected future reward given that state
        action, _ = policy.act(state)
        state, reward, done, info = env.step(action) # We directly put next_state = state for recording logic
        img = env.render(mode='rgb_array')
        images.append(img)
    imageio.mimsave(out_directory, [np.array(img) for i, img in enumerate(images)], fps=fps)

def push_to_hub(repo_id, 
                model,
                hyperparameters,
                eval_env,
                video_fps=30
                ):
  """
  Evaluate, Generate a video and Upload a model to Hugging Face Hub.
  This method does the complete pipeline:
  - It evaluates the model
  - It generates the model card
  - It generates a replay video of the agent
  - It pushes everything to the Hub

  :param repo_id: repo_id: id of the model repository from the Hugging Face Hub
  :param model: the pytorch model we want to save
  :param hyperparameters: training hyperparameters
  :param eval_env: evaluation environment
  :param video_fps: how many frame per seconds to record our video replay 
  """

  _, repo_name = repo_id.split("/")
  api = HfApi()
  
  # Step 1: Create the repo
  repo_url = api.create_repo(
        repo_id=repo_id,
        exist_ok=True,
  )

  with tempfile.TemporaryDirectory() as tmpdirname:
    local_directory = Path(tmpdirname)
  
    # Step 2: Save the model
    torch.save(model, local_directory / "model.pt")

    # Step 3: Save the hyperparameters to JSON
    with open(local_directory / "hyperparameters.json", "w") as outfile:
      json.dump(hyperparameters, outfile)
    
    # Step 4: Evaluate the model and build JSON
    mean_reward, std_reward = evaluate_agent(eval_env, 
                                            hyperparameters["max_t"],
                                            hyperparameters["n_evaluation_episodes"], 
                                            model)
    # Get datetime
    eval_datetime = datetime.datetime.now()
    eval_form_datetime = eval_datetime.isoformat()

    evaluate_data = {
          "env_id": hyperparameters["env_id"], 
          "mean_reward": mean_reward,
          "n_evaluation_episodes": hyperparameters["n_evaluation_episodes"],
          "eval_datetime": eval_form_datetime,
    }

    # Write a JSON file
    with open(local_directory / "results.json", "w") as outfile:
        json.dump(evaluate_data, outfile)

    # Step 5: Create the model card
    env_name = hyperparameters["env_id"]
    
    metadata = {}
    metadata["tags"] = [
          env_name,
          "reinforce",
          "reinforcement-learning",
          "custom-implementation",
          "deep-rl-class"
      ]

    # Add metrics
    eval = metadata_eval_result(
        model_pretty_name=repo_name,
        task_pretty_name="reinforcement-learning",
        task_id="reinforcement-learning",
        metrics_pretty_name="mean_reward",
        metrics_id="mean_reward",
        metrics_value=f"{mean_reward:.2f} +/- {std_reward:.2f}",
        dataset_pretty_name=env_name,
        dataset_id=env_name,
      )

    # Merges both dictionaries
    metadata = {**metadata, **eval}

    model_card = f"""
        # **Reinforce** Agent playing **{env_id}**
        This is a trained model of a **Reinforce** agent playing **{env_id}** .
        To learn to use this model and train yours check Unit 4 of the Deep Reinforcement Learning Course: https://huggingface.co/deep-rl-course/unit4/introduction
        """

    readme_path = local_directory / "README.md"
    readme = ""
    if readme_path.exists():
        with readme_path.open("r", encoding="utf8") as f:
          readme = f.read()
    else:
      readme = model_card

    with readme_path.open("w", encoding="utf-8") as f:
      f.write(readme)

    # Save our metrics to Readme metadata
    metadata_save(readme_path, metadata)

    # Step 6: Record a video
    video_path =  local_directory / "replay.mp4"
    record_video(env, model, video_path, video_fps)

    # Step 7. Push everything to the Hub
    api.upload_folder(
          repo_id=repo_id,
          folder_path=local_directory,
          path_in_repo=".",
    )

    clear_console_item(f"Your model is pushed to the Hub. You can view your model here: {repo_url}")




######################## SCRIPT MAIN FUNCTION ##########################################################

def main():
    """Executes the training, that's it."""

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


    ############ CHECK THE MACHINE ####################################  

    # Show parametrs
    clear_console_title("MAIN", "START")
    clear_console_item("SCRIPT PARAMETERS:", "\n".join(f"{k} = {v}" for k, v in vars(args).items()))

    # Check git-lfs
    clear_console_os_command("INITIALIZE GIT",     'git config --global credential.helper store')
    clear_console_os_command("INITIALIZE GIT-LFS", 'git lfs install')

    # Load credentials from Azure Identity and Connect to HF
    clear_console_title("CONNECTING TO HUGING FACE...")    
    aml_credential = DefaultAzureCredential()
    aml_secret_client = SecretClient(vault_url = args.key_vault_url, credential = aml_credential)
    hf_access_token = aml_secret_client.get_secret("hf-access-token")
    hf_access_token = hf_access_token.value
    clear_console_item("Hugging Face Access Token", hf_access_token[-2:])
    hf.login(token = hf_access_token, add_to_git_credential = True)
    clear_console_item("Hugging Face login complete...")
    hf_models = list_models()
    hf_hub_download(repo_id="carlosmirandad/rl-class-q-taxi-v3", filename="replay.mp4")
    clear_console_item("Hugging Face pre-checks complete...")


    # Record everything in the environment in case we need to troubleshoot later
    clear_console_os_command("OPERATING SYSTEM", 'cat /etc/*-release')
    clear_console_os_command("HARDWARE: CPU",    'cat /proc/cpuinfo')
    clear_console_os_command("HARDWARE: GPU",    'nvidia-smi')

    clear_console_os_command("ALIASES",      'alias')
    clear_console_os_command("USER",         'whoami')
    clear_console_item("CURRENT DIRECTORY ", os.getcwd(), "\n")

    clear_console_os_command("VERSIONS", 'python --version')
    clear_console_item("PyTorch ", torch.__version__)
    clear_console_item("TensorFlow ", tf.__version__, "\n")

    clear_console_os_command("PROCESSES",  'ps -aux')
    clear_console_os_command("DISK SPACE", 'df -h')

    clear_console_os_command("PIP FREEZE SNAPHOT", 'pip freeze > snapshot_requirements.txt && cat snapshot_requirements.txt')
    clear_console_os_command("APT LIST SNAPHOT",   "apt list --installed | sed s/Listing...// | awk -F '/' '{print $1}' > snapshot_apt_installed_packages.txt && cat snapshot_apt_installed_packages.txt")

    clear_console_os_command("ROOT DIRECTORY CONTENTS",          'ls -al /') 
    clear_console_os_command("AML MOUNTS FULL CONTENTS",         'ls -alR /mnt/azureml/ ') 
    clear_console_os_command("CURRENT DIRECTORY FULL CONTENTS",  'ls -alR')

    # Initialize virtual display
    clear_console_title("Virtual display")
    virtual_display = Display(visible=0, size=(1400, 900))
    virtual_display.start()

    ############ EXECUTE THE TRAINING ####################################
    clear_console_title("TRAINING", "START") 

    # # Create the envs 
    # # TODO: Move from global section over here to main
    # env      = gym.make(env_id)
    # eval_env = gym.make(env_id)

    # Get the state space and action space
    s_size = env.observation_space.shape[0]
    a_size = env.action_space.n

    clear_console_item("_____OBSERVATION SPACE_____ \n")
    clear_console_item("The State Space is: ", s_size)
    clear_console_item("Sample observation", env.observation_space.sample()) # Get a random observation

    clear_console_item("\n _____ACTION SPACE_____ \n")
    clear_console_item("The Action Space is: ", a_size)
    clear_console_item("Action Space Sample", env.action_space.sample()) # Take a random action

    # Real training parameters are harcoded for now.  Some variables are global for now.  Script parameters most are ignored.  See TODOs above.
    pixelcopter_hyperparameters = {
        "h_size": 64,
        "n_training_episodes": 100_000,
        "n_evaluation_episodes": 10,
        "max_t": 10000,
        "gamma": 0.99,
        "lr": 1e-4,
        "env_id": env_id,
        "state_space": s_size,
        "action_space": a_size,
    }

    # Create policy and place it to the device
    # torch.manual_seed(50)
    pixelcopter_policy = Policy(pixelcopter_hyperparameters["state_space"], pixelcopter_hyperparameters["action_space"], pixelcopter_hyperparameters["h_size"]).to(device)
    pixelcopter_optimizer = optim.Adam(pixelcopter_policy.parameters(), lr=pixelcopter_hyperparameters["lr"])

    # Train
    scores = reinforce(env,
                    pixelcopter_policy,
                    pixelcopter_optimizer,
                    pixelcopter_hyperparameters["n_training_episodes"], 
                    pixelcopter_hyperparameters["max_t"],
                    pixelcopter_hyperparameters["gamma"], 
                    1000)

    ############ EVALUATE MODEL ####################################
    clear_console_title("EVALUATION", "START") 
        
    evaluate_agent(eval_env, 
                pixelcopter_hyperparameters["max_t"], 
                pixelcopter_hyperparameters["n_evaluation_episodes"],
                pixelcopter_policy)    


    ############ PUBLISH THE FINAL MODEL ####################################  
    clear_console_title("PUBLICATION", "START") 

    hf_account_id = "carlosmirandad"
    algo_id = "reinforce"
    repo_id = f"{hf_account_id}/rl-class-{algo_id}-{env_id}" #TODO Define your repo id {username/Reinforce-{model-id}}
    clear_console_item(repo_id)

    push_to_hub(repo_id,
                pixelcopter_policy, # The model we want to save
                pixelcopter_hyperparameters, # Hyperparameters
                eval_env, # Evaluation environment
                video_fps=30
                )

    # TODO: Persist and register in azure portal, also log the stats with mlflow.
    # # Save model output
    # model_output_subdirectory = "logs/dqn/"
    # model_output_external_path = os.path.join(
    #     args.model_output, 
    #     f"output_{args.registered_model_name}_{args.job_timestamp}",
    #     model_output_subdirectory)
    # clear_console_item("Saving model outputs to path:", model_output_external_path)
    # shutil.copytree(model_output_subdirectory, model_output_external_path)
    # clear_console_os_command("EXTERNAL OUTPUT FULL CONTENTS", f"ls -alR {model_output_external_path} ")

    # End of training
    clear_console_title("MAIN", "END")


if __name__ == "__main__":
    main()