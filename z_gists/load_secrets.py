# Source code for the gist: load_secrets.py at https://gist.github.com/carlosmirandadurand
# Installation:
#   !wget -q bit.ly/cmd-load-secrets
#   %run cmd-load-secrets

import json
import os
from getpass import getpass
from pathlib import Path
from typing import Dict, List, Optional, Union


def load_secrets (secrets: Optional[Union[str, Dict[str, str]]] = None, overwrite=False) -> None:
    """
    Loads secrets (passed as a parameter or interatively) and sets up some env vars and credential files.
    
    If the `secrets` param is empty, you will be prompted to input a stringified json dict containing your secrets. 
    For example: {"github_user": "...", "github_pat": "...", "openai_organization": "...", "openai_organization_key": "..."}
    
    Otherwise, the secrets will be loaded from the given string or dict passed as a parameter.

    This function could be an alternative to using the dotenv.load_dotenv() function 

    The following types of credentials are supported:    
    - OpenAI Credentials:
        `openai_organization`: OpenAI Organization ID
        `openai_organization_key`: OpenAI Secret Key   
    - GitHub Credentials:
        `github_user`: GitHub Username
        `github_pat`: GitHub Personal Access Token
    - AWS Credentials:
        `aws_access_key_id`: AWS Key ID
        `aws_secret_access_key`: AWS Access Key
                
    Credits: Alexander Seifert (modifications by Carlos Miranda Durand) 
    Source: https://aseifert.com/p/secrets-management-colab/ 
    """

    if secrets and isinstance(secrets, str):
        secrets = json.loads(secrets)

    if not secrets:
        input = getpass("Secrets (JSON string): ")
        secrets = json.loads(input) if input else {}

    if "openai_organization" in secrets:
        os.environ["OPENAI_ORG"] = secrets["openai_organization"]
        os.environ["OPENAI_KEY"] = secrets["openai_organization_key"]

    if "github_user" in secrets:
        os.environ["GH_USER"] = secrets["github_user"]
        os.environ["GH_PAT"] = secrets["github_pat"]
        # provide a custom credential helper to git so that it uses your env vars
        os.system("""git config --global credential.helper '!f() { printf "%s\n" "username=$GH_USER" "password=$GH_PAT"; };f'""")

    if "aws_access_key_id" in secrets:
        home = Path.home()
        aws_id = secrets["aws_access_key_id"]
        aws_key = secrets["aws_secret_access_key"]
        (home / ".aws/").mkdir(parents=True, exist_ok=True)
        with open(home / ".aws/credentials", "w") as fp:
            fp.write(f"[default]\naws_access_key_id = {aws_id}\naws_secret_access_key = {aws_key}\n")
            