this version is currently tested and suported with ros2 humble 

you can modify https://github.com/lazyxcientist/xparo_ros/xparo_ros/xparo_node.py to make supported with other ros distro easily

```
    ██╗░░██╗██████╗░░█████╗░██████╗░░█████╗░
    ╚██╗██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
    ░╚███╔╝░██████╔╝███████║██████╔╝██║░░██║
    ░██╔██╗░██╔═══╝░██╔══██║██╔══██╗██║░░██║
    ██╔╝╚██╗██║░░░░░██║░░██║██║░░██║╚█████╔╝
    ╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝░╚════╝░
        Live   your   DREAMS   parrallely
```



website: https://xparo-website.onrender.com/

github: https://github.com/lazyxcientist/xparo_ros

email:   xpassistantpersonal@gmail.com


> requriements = websocket_client

<br>

-------------
## getting started with X.P.A.R.O
-------------

step 1 : go to https://xparo-website.onrender.com/dashboard_app and create an new project by clicking on "add new" button.

step 2 : now go to your project 

step 3 : copy the project_id (or secret_key if any) of your project. 

step 4 : copy the code given below and paste your keys there.





-------------
## how to use xparo with ros2
-------------

#### baisc setup
```bash
cd your_workspace/src  # move to src , where all packages are placed
git clone https://github.com/lazyxcientist/xparo_ros.git
```



#### build package
```bash
cd your_workspace  # move to workspace
colcon build    # build the workspace
source install/setup.bash
```

#### run the ros2_node
```bash
ros2 run xparo_ros xparo
```

