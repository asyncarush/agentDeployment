from urllib.parse import urlparse
from pathlib import Path
import subprocess as sp
import shutil
import os

class GitHandle:
    user_inputs = {}
    REPO_PATH = ""
    BASE_PATH = os.path.abspath(".")
    
    def __init__(self, user_inputs) -> None:
        self.user_inputs = user_inputs
        
    def setup_repo(self):
        self.set_repo_dir_from_url()
        self.clone_and_setup_repo()
        
    def set_repo_dir_from_url(self):
        parsed_url = urlparse(self.user_inputs['REPO_URL'])
        repo_name = Path(parsed_url.path).stem  
        #here we are setting the specific paths for all deployments
        self.REPO_PATH = os.path.join(self.BASE_PATH, "deployments", repo_name)
        Path(self.REPO_PATH).mkdir(parents=True, exist_ok=True)
        
        
    def clone_and_setup_repo(self):
        clone_check = sp.run(["git", "clone", self.user_inputs['REPO_URL'], self.REPO_PATH], check=True)

        if clone_check.returncode != 0:
            print("Clone of repo failed !!")

        os.chdir(self.REPO_PATH)
        
        #fetch all remote branches
        try:
            sp.run(["git", "fetch", "--all"], check=True)
        except sp.CalledProcessError as e:
            print(f"Unable to fetch all branches for repo, errorcode - {e.returncode}")
        
        #Checkout to deploy branch
        try:
            check_checkout = sp.run(["git", "checkout", "-b", self.user_inputs["DEPLOY_BRANCH"]], check=True)
            if check_checkout.returncode == 0:
                print("Successfully, pulled all the remote changes !! (override)")
        except sp.CalledProcessError as e:
            print(f"Unable to checkout to branch {self.user_inputs['DEPLOY_BRANCH']} , errorcode - {e.returncode}")
        
        #Pull all the changes from remote origin
        try:
            check_pull = sp.run(["git", "pull", "--rebase", "--strategy=recursive", "-X", "theirs", "origin", self.user_inputs["DEPLOY_BRANCH"]], check=True)
            if check_pull.returncode == 0:
                print("Successfully, pulled all the remote changes !! (override)")
        except sp.CalledProcessError as e:
            print(f"Unable to checkout to branch {self.user_inputs['DEPLOY_BRANCH']} , errorcode - {e.returncode}")
            
    def get_repo_path(self):
        return self.REPO_PATH