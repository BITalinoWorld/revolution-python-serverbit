import rumps
import webbrowser
import os

def restart():
    os.popen("./start_mac.sh")
    # os.popen("pkill -f ServerBIT")
    rumps.quit_application()

def init_rumps_osx():
    class ServerBIT_statusbar_app(rumps.App):
        def __init__(self):
            super(ServerBIT_statusbar_app, self).__init__("", icon="static/images/BITalino.icns", quit_button=None)
            self.menu = ["Preferences", "localhost:9001/config", "relaunch", "close"]
        @rumps.clicked("Preferences")
        def prefs(self, _):
            webbrowser.open('http://localhost:9001/config', new=2)
        @rumps.clicked("relaunch")
        def relaunch(self, _):
            os.popen("./start_mac.sh")
            # os.popen("pkill -f ServerBIT")
            rumps.quit_application()
        @rumps.clicked("close")
        def kill(self, _):
            os.popen("pkill -f Python")
            # os.popen("pkill -f ServerBIT")
            rumps.quit_application()
    ServerBIT_statusbar_app().run()

if __name__ == '__main__':
        init_rumps_osx();
