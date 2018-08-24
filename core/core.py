from core.network import ApacheNetwork
import yaml
import os

fileDir = os.path.dirname(os.path.realpath('__file__')) 
pathName = os.path.join(fileDir, ".\configs\core.yml")
file = open(pathName)
rawYaml = yaml.load(file)
addonsList = []
for addon in rawYaml["addons"]:
    addonsList.append(getattr(getattr(__import__('addons.'+addon),addon),'LaunchAddon'))

host = rawYaml["listening"]["host"]
port = rawYaml["listening"]["port"]

def launchNetwork():
    apNetwork = ApacheNetwork(addonsList, host, port)
    apNetwork.start()
