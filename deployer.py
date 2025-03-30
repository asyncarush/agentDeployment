import os
import shutil
import subprocess as sp
from ruamel.yaml import YAML

yaml = YAML()

class Deployer:
    user_inputs = {}
    REPO_PATH = ""
    BASE_PATH = os.path.abspath(".")
    DOCKERFILE_PATH = ""
   
    def __init__(self, user_inputs, repo_path) -> None:
        self.user_inputs = user_inputs
        self.REPO_PATH = repo_path
        print("printing repo path", repo_path)
    
    def start_deployment(self):
        self.check_and_setup_dockerfile()
        self.check_and_setup_helm()
        self.check_and_setup_ci_file()
    
    def check_and_setup_dockerfile(self):
        #check if dockerfile exist or not
        os.chdir(self.REPO_PATH)
        
        self.DOCKERFILE_PATH = os.path.join(self.REPO_PATH, "Dockerfile")
        
        if os.path.exists(self.DOCKERFILE_PATH):
            print("Dockerfile exist.")
        else:
            print("create dockerfile for directory")
            #Here now, we will copay from template docker file according to app type
            source = os.path.join(self.BASE_PATH, "template_dockerfile", f"{self.user_inputs['APP_TYPE']}.txt")
            target = os.path.join(repo_dir, "Dockerfile")
            shutil.copy(source, target)
    
        #check if docker image is successfully build or not
        docker_image_name = self.REPO_PATH.split("/")[-1]
        print("Will now build dockerfile")
        
        process = sp.Popen(["docker", "build", "-t", docker_image_name, "."], stdout=None, stderr=None)
        exist_code = process.wait()
        
        if exist_code == 0:
            print("\n✅ Docker build succeeded!")
        else:
            print(f"\n❌ Docker build failed with exit code {exist_code}")

        
        ## here check and setup helm will proceed
        
    def check_and_setup_helm(self):
        #check if helm directory exist or not
        all_dirs = [d for d in os.listdir(self.REPO_PATH) if os.path.isdir(os.path.join(self.REPO_PATH, d))]
        
        helm_dir = [ d for d in all_dirs if "helm" in d.lower()]
        
        if len(helm_dir) == 0:
            print("helm does not exist, Creating now")
            source = os.path.join(self.BASE_PATH, "template_helm")
            print("source", source)
            target = os.path.join(self.REPO_PATH, "deployment-helm")
            print("target", target)
            shutil.copytree(source, target)
            
        ##here check and setup ci file
      
    def check_and_setup_ci_file(self):
        #check if ci-cd file exist or not
        if not os.path.exists(f"{self.REPO_PATH}/.gitlab-ci.yml"):
            source = os.path.join(self.BASE_PATH, "template_ci_cd_file/.gitlab-ci.yml")
            target = os.path.join(self.REPO_PATH, ".gitlab-ci.yml")
            shutil.copy(source, target)
            print("Gitlab CI/CD file, created successfully....")
        
        with open(f"{self.REPO_PATH}/.gitlab-ci.yml", "r") as file:
            ci_file = yaml.load(file) 

        if "variables" not in ci_file:
            ci_file["variables"] = {}

        ci_file["variables"]["CLUSTER"] = self.user_inputs.get("KUBECONFG_NAME")
        ci_file["variables"]["KUBE_NAMESPACE"] = self.user_inputs.get("CLUSTER_NAMESPACE")
        ci_file["variables"]["INGRESS_URL"] = self.user_inputs.get("INGRESS_URL")
        ci_file["variables"]["APP_RUNNING_PORT"] = self.user_inputs.get("APP_RUNNING_PORT") 

        with open(f"{self.REPO_PATH}/.gitlab-ci.yml", "w") as file:
            yaml.dump(ci_file, file) # update the ci file here
            