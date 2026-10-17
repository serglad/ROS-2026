
# Терминал 1
```
degradedtomato@degradedtomato-BRI-XX:~/robotics_ws$ source install/setup.bash
degradedtomato@degradedtomato-BRI-XX:~/robotics_ws$ export ROS_DOMAIN_ID=16
degradedtomato@degradedtomato-BRI-XX:~/robotics_ws$ ros2 pkg prefix turtle_bringup
/home/degradedtomato/robotics_ws/install/turtle_bringup
degradedtomato@degradedtomato-BRI-XX:~/robotics_ws$ ls "$(ros2 pkg prefix turtle_bringup)/share/turtle_bringup/launch"
__pycache__  sim.launch.py
degradedtomato@degradedtomato-BRI-XX:~/robotics_ws$ ros2 launch turtle_bringup sim.launch.py 
[INFO] [launch]: All log files can be found below /home/degradedtomato/.ros/log/2026-10-12-22-32-38-738697-degradedtomato-BRI-XX-3824
[INFO] [launch]: Default logging verbosity is set to INFO
[INFO] [turtlesim_node-1]: process started with pid [3827]
[turtlesim_node-1] [INFO] [1791819158.965648215] [turtlesim]: Starting turtlesim with node name /turtlesim
[turtlesim_node-1] [INFO] [1791819158.975617279] [turtlesim]: Spawning turtle [turtle1] at x=[5,544445], y=[5,544445], theta=[0,000000]
^C[WARNING] [launch]: user interrupted with ctrl-c (SIGINT)
[turtlesim_node-1] [INFO] [1791819201.418288508] [rclcpp]: signal_handler(SIGINT/SIGTERM)
[INFO] [turtlesim_node-1]: process has finished cleanly [pid 3827]
```
# Терминал 2
```
degradedtomato@degradedtomato-BRI-XX:~$ export ROS_DOMAIN_ID=16
degradedtomato@degradedtomato-BRI-XX:~$ ros2 node list --no-daemon --spin-time 2
/turtlesim
degradedtomato@degradedtomato-BRI-XX:~$ ros2 node list --no-daemon --spin-time 2
degradedtomato@degradedtomato-BRI-XX:~$
```

# Отправка команды
```
degradedtomato@degradedtomato-BRI-XX:~$ ros2 topic echo /turtle1/pose --once
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
degradedtomato@degradedtomato-BRI-XX:~$ ros2 topic echo /turtle1/pose --once
x: 6.509308815002441
y: 5.796990871429443
theta: 0.5040000081062317
linear_velocity: 0.0
angular_velocity: 0.0
---
```

# Ошибка
```
degradedtomato@degradedtomato-BRI-XX:~$ ros2 topic info /cmd_vel --verbose
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_9426
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.7d.93.d2.24.f9.4a.00.00.00.00.00.00.07.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 0

degradedtomato@degradedtomato-BRI-XX:~$ ros2 topic info /turtle1/cmd_vel --verbose
Type: geometry_msgs/msg/Twist

Publisher count: 0

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.7d.93.7d.23.6f.bb.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```

# Исправление
```
degradedtomato@degradedtomato-BRI-XX:~$ ros2 topic info /cmd_vel --verbose
Unknown topic '/cmd_vel'
degradedtomato@degradedtomato-BRI-XX:~$ ros2 topic info /turtle1/cmd_vel --verbose
Type: geometry_msgs/msg/Twist

Publisher count: 1

Node name: _ros2cli_9529
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: PUBLISHER
GID: 01.0f.7d.93.39.25.84.24.00.00.00.00.00.00.07.03
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite

Subscription count: 1

Node name: turtlesim
Node namespace: /
Topic type: geometry_msgs/msg/Twist
Topic type hash: RIHS01_9c45bf16fe0983d80e3cfe750d6835843d265a9a6c46bd2e609fcddde6fb8d2a
Endpoint type: SUBSCRIPTION
GID: 01.0f.7d.93.7d.23.6f.bb.00.00.00.00.00.00.1d.04
QoS profile:
  Reliability: RELIABLE
  History (Depth): UNKNOWN
  Durability: VOLATILE
  Lifespan: Infinite
  Deadline: Infinite
  Liveliness: AUTOMATIC
  Liveliness lease duration: Infinite
```