"""Relay the turtle pose to sensor_pose and probe it with a chosen QoS."""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from turtlesim.msg import Pose

RELAY_TOPIC = 'sensor_pose'
RELAY_RATE_HZ = 20.0


def make_publisher_qos(depth=10):
    """Return the sensor QoS: best effort, keep last depth messages."""
    return QoSProfile(
        reliability=QoSReliabilityPolicy.BEST_EFFORT,
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
    )


def make_subscriber_qos(reliability, depth=10):
    """Return the subscriber QoS for a reliability policy name."""
    mapping = {
        'best_effort': QoSReliabilityPolicy.BEST_EFFORT,
        'reliable': QoSReliabilityPolicy.RELIABLE,
    }
    if reliability not in mapping:
        raise ValueError(f'unknown reliability {reliability!r}')
    return QoSProfile(
        reliability=mapping[reliability],
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
    )


class PoseRelay(Node):
    """Republish the latest /turtle1/pose on relative sensor_pose."""

    def __init__(self):
        """Create the reliable pose input and the best effort output."""
        super().__init__('pose_relay')
        self.latest_pose = None
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.pose_pub = self.create_publisher(
            Pose, RELAY_TOPIC, make_publisher_qos())
        self.timer = self.create_timer(1.0 / RELAY_RATE_HZ, self.on_timer)

    def on_pose(self, message):
        """Store the last received pose."""
        self.latest_pose = message

    def on_timer(self):
        """Publish the latest pose if one arrived."""
        if self.latest_pose is not None:
            self.pose_pub.publish(self.latest_pose)


class PoseProbe(Node):
    """Count messages on relative sensor_pose with a chosen QoS."""

    def __init__(self):
        """Declare the reliability parameter and subscribe with its QoS."""
        super().__init__('pose_probe')
        self.declare_parameter('reliability', 'best_effort')
        self.received = 0
        name = self.get_parameter('reliability').value
        qos = make_subscriber_qos(name)
        self.get_logger().info(f'pose_probe subscribing with {name}')
        self.pose_sub = self.create_subscription(
            Pose, RELAY_TOPIC, self.on_pose, qos)
        self.timer = self.create_timer(2.0, self.on_timer)

    def on_pose(self, message):
        """Count one received pose."""
        self.received += 1

    def on_timer(self):
        """Report how many poses arrived since start."""
        self.get_logger().info(f'pose_probe received {self.received} poses')


def _run(node_class):
    """Spin a node of the given class until Ctrl+C."""
    rclpy.init()
    node = node_class()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


def main(args=None):
    """Run the pose relay publisher node."""
    _run(PoseRelay)


def probe_main(args=None):
    """Run the QoS-configurable subscriber node."""
    _run(PoseProbe)


if __name__ == '__main__':
    main()
