import subprocess as sp
import os
from pathlib import Path
from urllib.parse import urlparse
import shutil
from ruamel.yaml import YAML
import json

BASE_PATH = os.path.abspath(".")

USER_INPUTS = { 
               "KUBECONFG_NAME" : "TEST_KUBECONFIG", 
               "REPO_URL" : "https://git.neuralcompany.team/in-house-agents/agent-hr/frontend.git",
               "INGRESS_URL" : "example-hr",
               "APP_TYPE" : "react",
               "APP_RUNNING_PORT" : 8000,
               "CLUSTER_NAMESPACE" : "platformops"
               }

yaml = YAML()

def get_repo_dir_from_url(repo_url, base_dir):
    parsed_url = urlparse(repo_url)
    repo_name = Path(parsed_url.path).stem  
    repo_dir = os.path.join(base_dir, repo_name)
    Path(repo_dir).mkdir(parents=True, exist_ok=True)
    return repo_dir

def clone_and_setup_repo(url, app_type, deploy_branch="deploy"):
    all_repo_destination = os.path.abspath("./deployments")
    repo_dir = get_repo_dir_from_url(url, all_repo_destination)
    print(repo_dir)

    sp.run(["git", "clone", f"https://{url}", repo_dir],check=True)

    os.chdir(repo_dir)
    #fetch all remote branches
    sp.run(["git", "fetch", "--all"], check=True)
    sp.run(["git", "checkout", "-b", deploy_branch], check=True)
    sp.run(["git", "pull", "--rebase", "--strategy=recursive", "-X", "theirs", "origin", "main"], check=True)

    #check if dockerfile exist 
    check_and_setup_dockerfile(repo_dir, app_type)

def check_and_setup_dockerfile(repo_dir, app_type):
    #check if dockerfile exist or not
    os.chdir(repo_dir)
    
    dockerfile_path = os.path.join(repo_dir, "Dockerfile")
    
    if os.path.exists(dockerfile_path):
        print("Dockerfile exist.")
    else:
        print("create dockerfile for directory")
        #here now, we will copay from template docker file according to app type
        source = os.path.join(BASE_PATH, "template_dockerfile", f"{app_type}.txt")
        print("source", source)
        target = os.path.join(repo_dir, "Dockerfile")
        print("target", target)
      
        shutil.copy(source, target)
   
    # #check if docker image is successfully build or not
    # docker_image_name = repo_dir.split("/")[-1]
    # print("Will now build dockerfile")
    # process = sp.Popen(["docker", "build", "-t", docker_image_name, "."], stdout=None, stderr=None)
    
    # docker_build_code = process.wait()
    
    # if docker_build_code == 0:
    #     print("\n✅ Docker build succeeded!")
    # else:
    #     print(f"\n❌ Docker build failed with exit code {exit_code}")

    check_and_setup_helm(repo_dir, app_type)
    
def check_and_setup_helm(repo_dir, app_type):
    #check if helm directory exist or not
    
    all_dirs = [d for d in os.listdir(repo_dir) if os.path.isdir(os.path.join(repo_dir, d))]
    
    helm_dir = [ d for d in all_dirs if "helm" in d.lower()]
    
    if len(helm_dir) == 0:
        print("helm does not exist, Creating now")
        source = os.path.join(BASE_PATH, "template_helm")
        print("source", source)
        target = os.path.join(repo_dir, "deployment-helm")
        print("target", target)
        shutil.copytree(source, target)
        
    check_and_setup_ci_file(repo_dir, app_type)
        
        
def check_and_setup_ci_file(repo_dir, app_type):
    #check if ci-cd file exist or not
    
    if not os.path.exists(f"{repo_dir}/.gitlab-ci.yml"):
        source = os.path.join(BASE_PATH, "template_ci_cd_file/.gitlab-ci.yml")
        target = os.path.join(repo_dir, ".gitlab-ci.yml")
        shutil.copy(source, target)
        print("Gitlab CI/CD file, created successfully....")

    
    with open(f"{repo_dir}/.gitlab-ci.yml", "r") as file:
        ci_file = yaml.load(file) 

    if "variables" not in ci_file:
        ci_file["variables"] = {}

    ci_file["variables"]["CLUSTER"] = USER_INPUTS.get("KUBECONFG_NAME")
    ci_file["variables"]["KUBE_NAMESPACE"] = USER_INPUTS.get("CLUSTER_NAMESPACE")
    ci_file["variables"]["INGRESS_URL"] = USER_INPUTS.get("INGRESS_URL")
    ci_file["variables"]["APP_RUNNING_PORT"] = USER_INPUTS.get("APP_RUNNING_PORT") 

    with open(f"{repo_dir}/.gitlab-ci.yml", "w") as file:
        yaml.dump(ci_file, file)
            



prompt_url = "git.neuralcompany.team/in-house-agents/agent-hr/frontend.git"
deploy_branch = "deploy"
app_type = "react"


clone_and_setup_repo(prompt_url, app_type, deploy_branch)