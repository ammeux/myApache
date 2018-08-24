from api import Addon

class LaunchAddon(Addon):
    
    def execute(self, duplex):
        if(".html" in duplex.request.uri):
            print("This is an html")