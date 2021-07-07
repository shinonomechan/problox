from urllib.parse import urlsplit
import os
import requests

def random_user_agent():
    url = "https://jnrbsn.github.io/user-agents/user-agents.json"
    user_agents = requests.get(url).json()
    return user_agents[0]

def hostname_from_url(url):
    purl = urlsplit(url)
    return purl.hostname.lower()

def get_latest_client_path():
    if os.name != "nt":
        raise NotImplementedError("Your OS platform is not supported")

    version_url = "https://s3.amazonaws.com/setup.roblox.com/version"
    version = requests.get(version_url).text.rstrip()
    
    paths = (
        os.environ["LOCALAPPDATA"] + "\\" + f"Roblox\\Versions\\{version}",
        os.environ["SYSTEMDRIVE"] + "\\" + f"Program Files (x86)\\Roblox\\Versions\\{version}",
        os.environ["SYSTEMDRIVE"] + "\\"+ f"Program Files\\Roblox\\Versions\\{version}"
    )
    for path in paths:
        if os.path.isdir(path):
            return os.path.join(path, "RobloxPlayerBeta.exe")
        
    raise FileNotFoundError("Could not find path to Roblox client")
