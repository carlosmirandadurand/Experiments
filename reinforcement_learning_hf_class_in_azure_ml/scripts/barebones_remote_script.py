# Barebones remote script 
# Meant for testing and debuging of infrastructure 

import argparse
from datetime import datetime

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

    print(f"STARTING EXECUTION: {datetime.now()} ")
    print("PARAMETERS RECEIVED:")
    print("\n".join(f"{k} = {v}" for k, v in vars(args).items()))
    print(f"COMPLETED EXECUTION: {datetime.now()} ")

if __name__ == "__main__":
    main()