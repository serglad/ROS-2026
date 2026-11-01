"""Test command source publishing fresh Ackermann commands on /drive/safe."""

from ackermann_msgs.msg import AckermannDriveStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rosgraph_msgs.msg import Clock


class TestCommand(Node):
    """Publish a configurable command stamped with the latest /clock value."""

    def __init__(self):
        """Create the clock subscription and the safe-topic publisher."""
        super().__init__('test_command')
        self.declare_parameter('speed', 0.5)
        self.declare_parameter('steering_angle', 0.1)
        self.declare_parameter('drive_safe_topic', '/drive/safe')
        self.last_clock = None
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10)
        safe_topic = self.get_parameter('drive_safe_topic').value
        self.clock_sub = self.create_subscription(
            Clock, '/clock', self.on_clock, 10)
        self.drive_pub = self.create_publisher(
            AckermannDriveStamped, safe_topic, qos)
        self.timer = self.create_timer(0.2, self.on_timer)

    def on_clock(self, message):
        """Store the latest simulation clock sample."""
        self.last_clock = message

    def on_timer(self):
        """Publish one command stamped with the freshest simulation time."""
        if self.last_clock is None:
            return
        message = AckermannDriveStamped()
        message.header.stamp = self.last_clock.clock
        message.drive.speed = float(
            self.get_parameter('speed').value)
        message.drive.steering_angle = float(
            self.get_parameter('steering_angle').value)
        self.drive_pub.publish(message)


def main(args=None):
    """Run the test command source until Ctrl+C."""
    rclpy.init(args=args)
    node = TestCommand()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
