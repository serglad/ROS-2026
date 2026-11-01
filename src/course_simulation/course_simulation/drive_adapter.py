"""Drive adapter translating /drive/safe Ackermann commands into Gazebo Twist."""

import math

from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

MAX_SPEED = 1.2
MAX_STEERING = 0.45
WHEELBASE = 0.8
STALE_TIMEOUT = 0.25


def twist_from_drive(speed, steering_angle, age_sec):
    """Return a (Twist, reason) pair; reason is non_finite, stale or empty."""
    twist = Twist()
    if not math.isfinite(speed) or not math.isfinite(steering_angle):
        return twist, 'non_finite'
    if age_sec is not None and age_sec > STALE_TIMEOUT:
        return twist, 'stale'
    v = min(max(speed, 0.0), MAX_SPEED)
    delta = min(max(steering_angle, -MAX_STEERING), MAX_STEERING)
    twist.linear.x = v
    twist.angular.z = v * math.tan(delta) / WHEELBASE
    return twist, ''


class DriveAdapter(Node):
    """Republish the clamped command at a fixed rate; never repeat a stale one."""

    def __init__(self):
        """Create the safe-command subscription, command and diagnostic publishers."""
        super().__init__('drive_adapter')
        self.declare_parameter('drive_safe_topic', '/drive/safe')
        self.declare_parameter('cmd_topic', '/vehicle/gz_cmd_vel')
        self.last_msg = None
        self.last_reason = None
        safe_topic = self.get_parameter('drive_safe_topic').value
        cmd_topic = self.get_parameter('cmd_topic').value
        self.safe_sub = self.create_subscription(
            AckermannDriveStamped, safe_topic, self.on_drive, 10)
        self.cmd_pub = self.create_publisher(Twist, cmd_topic, 10)
        self.diag_pub = self.create_publisher(
            String, cmd_topic + '/diagnostic', 10)
        self.timer = self.create_timer(0.05, self.on_timer)

    def on_drive(self, message):
        """Store the latest safe command."""
        self.last_msg = message

    def on_timer(self):
        """Publish the command derived from the latest message age."""
        age = None
        speed, steering = 0.0, 0.0
        if self.last_msg is not None:
            stamp = self.last_msg.header.stamp
            now = self.get_clock().now().nanoseconds
            age = (now - (stamp.sec * 10**9 + stamp.nanosec)) / 1e9
            if age < 0.0:
                age = 0.0
            speed = self.last_msg.drive.speed
            steering = self.last_msg.drive.steering_angle
        twist, reason = twist_from_drive(speed, steering, age)
        self.cmd_pub.publish(twist)
        if reason != self.last_reason:
            self.last_reason = reason
            if reason:
                self.get_logger().warning(f'zero command: {reason}')
            self.diag_pub.publish(String(data=reason or 'ok'))


def main(args=None):
    """Run the drive adapter until Ctrl+C."""
    rclpy.init(args=args)
    node = DriveAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
