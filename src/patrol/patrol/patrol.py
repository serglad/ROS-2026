"""Patrol node: keeps the last turtle pose and publishes twist commands."""

from types import SimpleNamespace

from geometry_msgs.msg import Twist
from rcl_interfaces.msg import (
    FloatingPointRange,
    ParameterDescriptor,
    SetParametersResult,
)
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

CRUISE_LINEAR_X = 0.5
TURN_ANGULAR_Z = 0.3

MIN_PERIOD = 0.01
MAX_PERIOD = 10.0


def choose_command(pose):
    """Return a Twist command for the latest pose, zero before the first pose."""
    command = Twist()
    if pose is None:
        return command
    command.linear.x = CRUISE_LINEAR_X
    command.angular.z = TURN_ANGULAR_Z
    return command


def compute_command(pose, params):
    """Return a Twist command from the latest pose and the node parameters."""
    command = Twist()
    if pose is None:
        return command
    command.linear.x = params.initial_speed
    command.angular.z = params.turn_speed
    return command


class Patrol(Node):
    """Node storing the latest pose and publishing commands on a timer."""

    def __init__(self, **kwargs):
        """Declare parameters, create IO and the publishing timer."""
        super().__init__('patrol', **kwargs)
        self.declare_parameter('initial_speed', CRUISE_LINEAR_X)
        self.declare_parameter('turn_speed', TURN_ANGULAR_Z)
        self.declare_parameter(
            'period', 0.1, ParameterDescriptor(
                description='Publish period in seconds.',
                floating_point_range=[FloatingPointRange(
                    from_value=MIN_PERIOD, to_value=MAX_PERIOD)],
            ))
        self.params = SimpleNamespace(
            initial_speed=self.get_parameter('initial_speed').value,
            turn_speed=self.get_parameter('turn_speed').value,
            period=self.get_parameter('period').value,
        )
        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(self.params.period, self.on_timer)
        self.add_on_set_parameters_callback(self.on_set_parameters)

    def on_pose(self, message):
        """Store the last received pose."""
        self.latest_pose = message

    def on_timer(self):
        """Publish the command chosen from the latest pose and parameters."""
        self.cmd_pub.publish(compute_command(self.latest_pose, self.params))

    def on_set_parameters(self, parameters):
        """Validate period, set state first, then recreate the timer itself."""
        result = SetParametersResult(successful=True)
        for parameter in parameters:
            if parameter.name != 'period':
                continue
            value = parameter.value
            if not isinstance(value, float) or not MIN_PERIOD <= value <= MAX_PERIOD:
                result.successful = False
                result.reason = f'period must be in [{MIN_PERIOD}, {MAX_PERIOD}]'
                return result
            self.params.period = value
            self.timer.cancel()
            self.timer = self.create_timer(value, self.on_timer)
        return result


def main(args=None):
    """Run the patrol node until Ctrl+C."""
    rclpy.init(args=args)
    node = Patrol()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
