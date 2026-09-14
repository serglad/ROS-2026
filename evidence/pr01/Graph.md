
`ros2 node list --no-daemon --spin-time 2`
```
/teleop_turtle
/turtlesim
```
`ros2 topic list -t`
```
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim/msg/Color]
/turtle1/pose [turtlesim/msg/Pose]
```
`ros2 node info /turtlesim`
```
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim/msg/Color
    /turtle1/pose: turtlesim/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim/srv/Spawn
    /turtle1/set_pen: turtlesim/srv/SetPen
    /turtle1/teleport_absolute: turtlesim/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/get_type_description: type_description_interfaces/srv/GetTypeDescription
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim/action/RotateAbsolute
  Action Clients:
```
`ros2 topic type /turtle1/pose`
```
turtlesim/msg/Pose
```
`ros2 topic echo /turtle1/pose --once`
```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
---
```
`ros2 topic hz /turtle1/pose`
```
average rate: 62.547
	min: 0.014s max: 0.017s std dev: 0.00059s window: 64
average rate: 62.509
	min: 0.014s max: 0.018s std dev: 0.00068s window: 127
average rate: 62.527
	min: 0.014s max: 0.018s std dev: 0.00066s window: 190
average rate: 62.519
	min: 0.014s max: 0.018s std dev: 0.00067s window: 253
average rate: 62.513
	min: 0.014s max: 0.018s std dev: 0.00065s window: 316
average rate: 62.507
	min: 0.014s max: 0.018s std dev: 0.00065s window: 379
average rate: 62.506
	min: 0.014s max: 0.018s std dev: 0.00066s window: 442
average rate: 62.513
	min: 0.014s max: 0.018s std dev: 0.00065s window: 505
average rate: 62.510
	min: 0.014s max: 0.018s std dev: 0.00064s window: 568

```


teleop_turtle - ввод пользователя для передачи целевой линейной и угловой скорости черепахе
turtlesim - симуляция черепахи

/turtle1/cmd_vel - линейная и угловая скорость
/turtle1/color_sensor - цвет под черепахой, 60 гц
/turtle1/pose - положение черепахи (x,y,угол,линейная скорость, угловая скорость), 60 гц

До (teleop_turtle{16},turtlesim{16}):
```
cat pose-working.txt 
x: 5.734466552734375
y: 4.372170448303223
theta: -1.9839999675750732
linear_velocity: 0.0
angular_velocity: 0.0
---
```

```
printf 'exit=%s\n' "$?"
exit=0
```
Сбой (teleop_turtle{17},turtlesim{16}):
```
cat pose-broken.txt

```

```
exit=124
```
После (teleop_turtle{16},turtlesim{16}):
```
cat pose-fixed.txt 
x: 6.4340434074401855
y: 10.103102684020996
theta: -2.4800000190734863
linear_velocity: 0.0
angular_velocity: 0.0
---
```

```
printf 'exit=%s\n' "$?"
exit=0
```