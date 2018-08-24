from api import Addon
from env import ROOTPATH
import subprocess
from api import format_response, parse_php_response

class LaunchAddon(Addon):

    def execute(self, duplex):
        if(".php" in duplex.request.uri):
            env = dict()
            env["SCRIPT_FILENAME"] = ROOTPATH + '/www/' + duplex.request.uri
            conn = duplex.socket

            with subprocess.Popen(["C:\php\php-cgi.exe"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as process:
                stdout, stderr = process.communicate()
                response = parse_php_response(stdout)
                response = format_response(response)
                duplex.response = response.encode()