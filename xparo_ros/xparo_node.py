import rclpy
from rclpy.node import Node 
from std_msgs.msg import String
from sensor_msgs.msg import Image
from .xparo import Project
from datetime import datetime
from dateutil import parser
import json




class Xparo_node(Node):
    def __init__(self, **kwargs):
        super().__init__("xparo")
        self.create_timer(1.0, self.timmer_fun) # for running shedule control commands

        # remote commmand send and receive for teleoperation
        self.remote_receive = self.create_publisher(String,"/xparo/remote",10)
        self.remote_send = self.create_subscription(String,"/xparo/remote/send",self.remote_command_reviced, 10)

        # make global configuration which you can change remotely
        self.change_config = self.create_publisher(String,"/xparo/config",10) 
        # self.change_config_sub = self.create_subscription(String,"/xparo/config/send", self.config_recive,10) 

        # interact with realworld ai chatbot to make your robot smart
        self.ai_receive = self.create_publisher(String,"/xparo/ai", 10)
        self.ai_send = self.create_subscription(String,"/xparo/ai/send",self.ai_chatbot_command , 10)

        # send video frame remotely
        self.video_receive = self.create_publisher(Image,"/xparo/video", 10)
        self.video_send = self.create_subscription(Image,"/xparo/video/send",self.revive_video_frame , 10)


        #################################
        ############ X.P.A.R.O ##########
        email = 'test_remote'
        project_key = 'd6da039f-06ae-4ccd-a2fc-2f817caae6de'
        secret = 'public'
        self.project = Project(project_key,secret,email)
        self.project.remote_callback = self.remote_callback
        self.project.config_callback = self.config_callback
        self.project.ai_callback = self.ai_callback
        self.project.video_callback = self.video_callback




    def remote_callback(self,msg):
        ss = String()
        ss.data = str(msg)
        self.remote_receive.publish(ss)
    def config_callback(self,key,val):
        ss = String()
        ss.data = str({key:val})
        self.change_config.publish(ss)
    def ai_callback(self,msg):
        ss = String()
        ss.data = str(msg)
        self.ai_receive.publish(ss)
    def video_callback(self,msg):
        ss = Image()
        ss.data = str(msg)
        self.video_receive.publish(ss)


    def remote_command_reviced(self,message):
        self.project.send(str(message.data))
    def ai_chatbot_command(self, message):
        self.project.private_send(json.dumps({"ai":str(message.data)}))
    def revive_video_frame(self,message):
        self.project.private_send(json.dumps({"media":str(message.data)}))
    def config_recive(self,message):
        try:
            for ii , jj in json.loads(message.data):
                self.project.update_config(ii,jj)
        except Exception as e:
            print(e)



        
    def timmer_fun(self,**kwargs):
        current_time = datetime.now()
        for command, details in self.project.schedule_control.items():
            scheduled_time = parser.parse(details['date'] + ' ' + details['time'])
            if current_time >= scheduled_time:
                self.get_logger().info(f"Executing scheduled command '{command}' at {current_time}")
                ss = String()
                ss.data = str(command)
                self.remote_receive.publish(ss)
        


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(Xparo_node())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
