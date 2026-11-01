"""Launch robot_state_publisher with the course Ackermann description."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """Build the description launch with optional RViz."""
    urdf_path = PathJoinSubstitution([
        FindPackageShare('course_description'), 'urdf', 'vehicle.urdf.xacro'])
    robot_description = Command([FindExecutable(name='xacro'), ' ', urdf_path])

    declared_arguments = [
        DeclareLaunchArgument(
            'gui', default_value='false',
            description='Also start RViz with the RobotModel display.'),
    ]

    state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                robot_description, value_type=str),
        }])

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        condition=IfCondition(LaunchConfiguration('gui')))

    return LaunchDescription(
        declared_arguments + [state_publisher, rviz])
