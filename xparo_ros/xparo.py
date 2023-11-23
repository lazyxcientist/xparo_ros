
import websocket
import json
import threading
import requests
import time
import os
import datetime
import time
import threading


xparo_website = '127.0.0.1:8000' # 'xparo-website.onrender.com'
DEBUG = True

# 'https://'+xparo_website

########### shedule control ###########
#######################################
shedule_control_path = os.path.join(os.path.dirname(__file__), 'shedule_control.json')
shedule_control = {}
if os.path.exists(shedule_control_path):
    with open(shedule_control_path) as f:
        try:
            shedule_control = json.load(f)
        except:
            shedule_control = {}
if not shedule_control:
    with open(shedule_control_path, 'w') as f:
        json.dump(shedule_control, f)

def update_shedule_control(data):
    if DEBUG:
        print("updating shedule control  ",data)
    global shedule_control_path
    with open(shedule_control_path, 'w') as f:
        json.dump(data, f)


############### error #############
###################################
def read_files_in_directory(root_directory, exclude_files=None):
    if exclude_files is None:
        exclude_files = []

    data_dict = {}

    # Walk through the root directory and its subdirectories
    for root, dirs, files in os.walk(root_directory):
        current_dict = data_dict

        # Create a nested dictionary structure based on the directory hierarchy
        for dir_name in os.path.relpath(root, root_directory).split(os.path.sep):
            current_dict = current_dict.setdefault(dir_name, {})

        # Process files in the current directory
        for filename in files:
            # Skip files in the exclude list
            if filename in exclude_files:
                continue

            filepath = os.path.join(root, filename)

            # Check if it's a file (not a directory)
            if os.path.isfile(filepath):
                with open(filepath, 'r') as file:
                    # Read the contents of the file
                    file_content = file.read()

                    # Store the content in the nested dictionary with the full path as the key
                    current_dict[filename] = file_content

    return data_dict

# Example: Read files in the ROS2 log directory excluding 'logger_all.log' and 'events.log'
ros2_log_directory = 'log'
exclude_files_list = ['logger_all.log', 'events.log']
'''
{'file name': {
            "build_id":{
                        "package":{"file_name":"data"}
                        }
                }
}'''








############### websocket #############
#######################################

class Xparo(websocket.WebSocketApp):
    def __init__(self, *args, **kwargs):
        super(Xparo, self).__init__(*args, **kwargs)



class Project():
    def __init__(self,project_key,unique_name,secret="public"):
        self.websocket_connected = False
        self.email = unique_name
        self.project_key = project_key
        self.secret = secret

        # calbacks
        self.remote_callback = None # takes on parameter
        self.config_callback = None # config_callback take 2 paramenter
        self.ai_callback = None 
        self.video_callback = None


        self.connection_type = "websocket"

        self.config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        self.config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                try:
                    self.config = json.load(f)
                except:
                    self.config = {}
        if not self.config:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f)
        self.schedule_control = {}
        self.connect()
        



    def connect(self):
        print('''
    connencting to ...
    ██╗░░██╗██████╗░░█████╗░██████╗░░█████╗░
    ╚██╗██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
    ░╚███╔╝░██████╔╝███████║██████╔╝██║░░██║
    ░██╔██╗░██╔═══╝░██╔══██║██╔══██╗██║░░██║
    ██╔╝╚██╗██║░░░░░██║░░██║██║░░██║╚█████╔╝
    ╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░
        Live   your   DREAMS   parrallely
        ''')
        if self.connection_type == "websocket":
            if not self.websocket_connected:
                # socket_server = 'ws://xparo-robot-remote.onrender.com/ws/remote/xparo_remote/123456789/robot/'
                #FIXME: wss://
                socket_server='ws://'+xparo_website+'/ws/remote/'+str(self.project_key)+'/'+str(self.secret)+'/'+str(self.email)+'/'
                self.ws = Xparo(str(socket_server),
                                on_message=self.on_ws_message,
                                on_error=self.on_ws_error,
                                on_open=self.on_ws_open,
                                on_close=self.on_ws_close,
                                )
                self.websocket_connected = True
                threading.Thread(target=self.ws.run_forever).start()
                self.send_error()
            else:
                print("already connected to xparo remote")
        elif self.connection_type == "rest":
            threading.Thread(target=self.start_reset_framework).start()
            # self.start_reset_framework()
           

    def send(self,message,remote_name="default"):
        filtered_data = json.dumps({"command":message})
        self.private_send(filtered_data)


    def private_send(self,message):
        pass
        if self.connection_type == "websocket":
            try:
                self.ws.send(message)
            except Exception as e:
                print(e)
        elif self.connection_type == "rest":
            try:
                api_url = 'https://'+xparo_website+'/remote/api_project_control/'+self.secret+'/'+self.project_key
                response = requests.post(api_url, data=message,headers={'Content-type': 'application/json'})
                if response.status_code == 201:
                    self.on_ws_message('self.ws', response.json())
                    if DEBUG:
                        print(f"command sent successfully {message}")
                    return True
                else:
                    print(str(response))
                    print('''
Truble shooting:
    1. internal server error. make sure you provide correct project id and secret key
    2. check your project id correct ( available in project dashboard home page )
    3. make sure your secret key is correct and acitvated (if any)
    
''')
                    return False
            except Exception as e:
                print(e)
                print('''
Truble shooting:
    1. check your internet connection
    2. if that not working download latest version of xparo or from github = https://github.com/lazyxcientist/xparo
    3. try to switch to websocket connection or rest framework
    
''')
                return False


    def on_ws_message(self, ws, message):
        print(message)
        message = json.loads(message)
        # if self.connection_type == "websocket":
        #     if self.remote_callback:
        #         self.remote_callback(message)
        # elif self.connection_type == "rest":
        for ii ,jj in message.items():
            try:
                if 'command'==ii:  #TODO: {'command':[['data','id'] , [], ]}
                    if self.remote_callback:
                        # for i in jj:
                        try:
                            self.remote_callback(jj)
                        except Exception as e:
                            print(e)
                if 'schedule_control'==ii:
                    global shedule_control_path
                    with open(shedule_control_path, 'w') as f:
                        json.dump(jj, f)
                if 'change_config'==ii:
                    for i,j in jj.items():
                        self.update_config(i,j)
                        print('sdl',self.config)
                        if self.config_callback:
                            try:
                                self.config_callback(i,j)
                            except Exception as e:
                                print(e)
                if 'ai_bot'==ii: 
                    if self.ai_callback:
                        for i in jj:
                            try:
                                self.ai_callback(str(i))
                            except Exception as e:
                                print(e)
                if 'tele_video'==ii: 
                    if self.video_callback:
                        for i in jj:
                            try:
                                self.video_callback(str(i))
                            except Exception as e:
                                print(e)
                if 'error'==ii:
                    self.send_error()
                if 'core'==ii:
                    result = eval(jj)
                    self.private_send(json.dumps({"core_result":str(result)}))
            except Exception as e:
                print(e)

    def on_ws_error(self, ws, error):
        print(error)

    # def ws_connection(self, dt, **kwargs):
    #     print("connecting to websocket")
    #     threading.Thread(target=self.ws.run_forever).start()


    def on_ws_open(self, ws):
        self.websocket_connected = True
        print('''
        \\\\Connection Sussessfull//
           \\\\X.P.A.R.O remote//
            \\\\is 🄻🄸🅅🄴 now//
        
        ''')


    def on_ws_close(self, *args):
        self.websocket_connected = False
        print('''
    Connection with XPARO  is
    █▀▀ █── █▀▀█ █▀▀ █▀▀ █▀▀▄ 
    █── █── █──█ ▀▀█ █▀▀ █──█ 
    ▀▀▀ ▀▀▀ ▀▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀─
        retry again !!!

        ''')
        time.sleep(10)
        self.connect()


    def start_reset_framework(self):
        print("starting reset framework")
        check = self.private_send(json.dumps({"config":self.config, "initiliaze":True}))
        self.send_error()
        if check:
            while True:
                response = requests.get('https://'+xparo_website+'/remote/api_project_control/'+self.secret+'/'+self.project_key)
                if response.status_code == 201:
                    data = response.json()
                    self.on_ws_message('self.ws',data)

                time.sleep(0.1)
        else:
            print("unable to connect with X.P.A.R.O server")
            self.on_ws_close('self.ws')


    ############################
    ###### custom send #########
    ############################
    
    def send_error(self):
        try:
            errors = read_files_in_directory(ros2_log_directory, exclude_files=exclude_files_list)
            self.private_send(json.dumps({"error":errors}))
        except Exception as e:
            print(e)


    def update_config(self,key,value):
        self.config[key] = value
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
        if self.config_callback:
            try:
                self.config_callback(key,value)
            except Exception as e:
                print(e)
        self.private_send(json.dumps({"config":self.config}))



# Wait for the monitor thread to finish gracefully
# monitor_thread.join() #FIXME: uncomment it for error tracking


if __name__ == "__main__":

    remote = Project("test_remote","e99dd21e-f7b2-4a4c-a74f-4658ad4dd2bd")

    def remote_callback(message):
        print(message)
    remote.remote_callback = remote_callback

    remote.send("hello")
