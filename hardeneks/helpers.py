from pathlib import Path
import urllib3
import yaml

#
# get_kube_config
# returns kube config in json
# 
# we need to update this function to take in a config string, so users can pass in kubeconfig as a param
def get_kube_config():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # need to fix this, so user can pass in .kube/config as a param (joshkurz)
    kube_config_orig = f"{Path.home()}/.kube/config"

    with open(kube_config_orig, "r") as fd:
        kubeconfig = yaml.safe_load(fd)
    return kubeconfig