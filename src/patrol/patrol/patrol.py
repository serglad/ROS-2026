"""Patrol node: keeps the last turtle pose and publishes twist commands."""

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

CRUISE_LINEAR_X = 0.5
TURN_ANGULAR_Z = 0.3


def choose_command(pose):
    """Return a Twist command for the latest pose, zero before the first pose."""
    command = Twist()
    if pose is None:
        return command
    command.linear.x = CRUISE_LINEAR_X
    command.angular.z = TURN_ANGULAR_Z
    return command


class Patrol(Node):
    """Node storing the latest pose and publishing commands on a timer."""

    def __init__(self):
        """Create the pose subscription, command publisher and timer."""
        super().__init__('patrol')
        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.on_timer)

    def on_pose(self, message):
        """Store the last received pose."""
        self.latest_pose = message

    def on_timer(self):
        """Publish the command chosen from the latest pose."""
        self.cmd_pub.publish(choose_command(self.latest_pose))


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
