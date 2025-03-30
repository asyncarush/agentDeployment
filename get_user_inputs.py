import questionary as q
import subprocess as sp
import os
import shutil
from deployer import Deployer
from git_handle import GitHandle

class GetUserInputs:
    USER_INPUTS = {}
    ALL_BRANCHES = []
    
    def ask_questions(self):
        self.USER_INPUTS["APP_TYPE"] = q.select("🚀 What type of app do you want to deploy?", choices=["⚛️ React","🐍 FastAPI (Python)",]).ask()
        repo_url = q.text("🔗 May I have the GitLab repository URL, please?").ask()
        self.validate_repo_url(repo_url)
        self.USER_INPUTS["DEPLOY_BRANCH"] = q.select("🌿 which branch do you wanna deploy?", choices=self.ALL_BRANCHES).ask()
        self.USER_INPUTS["KUBECONFG_NAME"] = q.text("🔧 KubeConfig of the cluster for this repo?").ask()
        self.USER_INPUTS["CLUSTER_NAMESPACE"] = q.text("📦 In which namespace should your app run?").ask()
        self.USER_INPUTS["APP_RUNNING_PORT"] = q.text("🚪 Which port will your app run on?").ask()
        self.USER_INPUTS["INGRESS_URL"] = q.text("✨ What’s the magic URL for your app?").ask()
        
        #lets go ahead with deployment
        self.get_it_deployed()
        
    def validate_repo_url(self, url):
        valid_url = False
        test_repo_dir = "./test"

        # Ensure directory is clean before cloning
        if os.path.exists(test_repo_dir):
            shutil.rmtree(test_repo_dir)

        os.makedirs(test_repo_dir, exist_ok=True)

        try:
            check = sp.run(["git", "clone", url, test_repo_dir], stdout=sp.DEVNULL, stderr=sp.DEVNULL, check=True)
            if check.returncode == 0:
                valid_url = True
        except sp.CalledProcessError as e:
            print(f"!! Cloning failed, please check the URL. Error code: {e.returncode}")
        
        # Retry if not valid
        while not valid_url:
            try:
                url = q.text("🔗 Try Again ! please provide valid GitLab repository URL, please?").ask()
                try_again = sp.run(["git", "clone", url, test_repo_dir], check=True)

                if try_again.returncode == 0:
                    valid_url = True
                    exit
            except sp.CalledProcessError as e:
                print(f"!! Retry failed, check your repo URL. Error Code {e.returncode}")

        
        #get all branches for next step
        result = sp.run(["git", "ls-remote", "--heads", url], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            self.ALL_BRANCHES = [ line.split("\t")[1].replace("refs/heads/", "") for line in result.stdout.strip().split("\n")]
        
        # Forcefully delete the directory and all contents
        if os.path.exists(test_repo_dir):
            shutil.rmtree(test_repo_dir)

        # now set the valid URL to userinput
        self.USER_INPUTS["REPO_URL"] = url

# https://git.neuralcompany.team/in-house-agents/agentqa/frontend.git
    
    def get_it_deployed(self):
        git_handler = GitHandle(self.USER_INPUTS)
        git_handler.setup_repo()
        deployment_handler = Deployer(self.USER_INPUTS, git_handler.get_repo_path())
        deployment_handler.start_deployment()