"""Launch patrol with turtlesim, pose relay, QoS probe and optional recording."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Build the launch description with namespace, QoS and recording args."""
    namespace = LaunchConfiguration('namespace')
    record = LaunchConfiguration('record')
    bag_dir = LaunchConfiguration('bag_dir')
    reliability = LaunchConfiguration('subscriber_reliability')

    declared_arguments = [
        DeclareLaunchArgument(
            'namespace', default_value='robot_a',
            description='Namespace for the robot nodes.'),
        DeclareLaunchArgument(
            'record', default_value='true',
            description='Start the rosbag2 recorder when true.'),
        DeclareLaunchArgument(
            'bag_dir', default_value='bags',
            description='Output directory (prefix) for the MCAP recording.'),
        DeclareLaunchArgument(
            'subscriber_reliability', default_value='best_effort',
            description='Reliability of the pose_probe subscriber.'),
    ]

    turtlesim = Node(
        package='turtlesim', executable='turtlesim_node', name='turtlesim',
        output='screen')

    patrol = Node(
        package='patrol', executable='patrol', name='patrol',
        namespace=namespace,
        remappings=[('cmd_vel', '/turtle1/cmd_vel')],
        output='screen')

    pose_relay = Node(
        package='course_bringup', executable='pose_relay', name='pose_relay',
        namespace=namespace,
        output='screen')

    pose_probe = Node(
        package='course_bringup', executable='pose_probe', name='pose_probe',
        namespace=namespace,
        parameters=[{'reliability': reliability}],
        output='screen')

    recorder = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'record',
            '-s', 'mcap',
            '-o', bag_dir,
            '--topics', ['/', namespace, '/sensor_pose'],
        ],
        output='screen',
        condition=IfCondition(record))

    return LaunchDescription(
        declared_arguments +
        [turtlesim, patrol, pose_relay, pose_probe, recorder])
