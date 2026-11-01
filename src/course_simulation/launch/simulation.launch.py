"""Launch Gazebo headless, robot_state_publisher, one bridge and both adapters."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition, UnlessCondition
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
    """Build the full course simulation launch description."""
    declared_arguments = [
        DeclareLaunchArgument(
            'world',
            default_value=PathJoinSubstitution([
                FindPackageShare('course_simulation'),
                'worlds', 'mcity-minimal.sdf']),
            description='SDF world file with the included course robot.'),
        DeclareLaunchArgument(
            'bridge_config',
            default_value=PathJoinSubstitution([
                FindPackageShare('course_simulation'),
                'config', 'bridge.yaml']),
            description='ros_gz_bridge YAML configuration.'),
        DeclareLaunchArgument(
            'headless', default_value='false',
            description='Run gz sim -s -r --headless-rendering (OGRE2/EGL).'),
        DeclareLaunchArgument(
            'namespace', default_value='/',
            description='Namespace for the drive adapter; contract topics are '
                        'absolute and therefore stay unchanged.'),
    ]

    world = LaunchConfiguration('world')
    headless = LaunchConfiguration('headless')

    urdf_path = PathJoinSubstitution([
        FindPackageShare('course_description'), 'urdf', 'vehicle.urdf.xacro'])
    robot_description = Command([FindExecutable(name='xacro'), ' ', urdf_path])

    gz_headless = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', '--headless-rendering', world],
        output='screen',
        condition=IfCondition(headless))
    gz_windowed = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world],
        output='screen',
        condition=UnlessCondition(headless))

    state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                robot_description, value_type=str),
            'use_sim_time': True,
        }])

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge',
        output='screen',
        parameters=[{
            'config_file': LaunchConfiguration('bridge_config'),
            'use_sim_time': True,
        }])

    drive_adapter = Node(
        package='course_simulation',
        executable='drive_adapter',
        output='screen',
        namespace=LaunchConfiguration('namespace'),
        parameters=[{'use_sim_time': True}])

    odom_adapter = Node(
        package='course_simulation',
        executable='odom_adapter',
        output='screen',
        parameters=[{'use_sim_time': True}])

    return LaunchDescription([
        *declared_arguments,
        gz_headless,
        gz_windowed,
        state_publisher,
        bridge,
        drive_adapter,
        odom_adapter,
    ])
