"""Odometry adapter normalizing Gazebo frames and owning the odom->base tf."""

import math

import geometry_msgs.msg
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
import tf2_ros

SOURCE_ODOM_FRAME = 'course_ackermann/odom'
SOURCE_CHILD_FRAME = 'course_ackermann/base_link'
ODOM_FRAME = 'odom'
CHILD_FRAME = 'base_link'
SOURCE_PREFIX = 'course_ackermann/'


def _finite_vector(values):
    """Return True when every component of values is a finite number."""
    return all(isinstance(v, float) and math.isfinite(v) for v in values)


def normalize_odometry(message):
    """Strip the model prefix from frames or return None for invalid input."""
    if message.header.frame_id != SOURCE_ODOM_FRAME:
        return None
    if message.child_frame_id != SOURCE_CHILD_FRAME:
        return None
    pose = message.pose.pose
    twist = message.twist.twist
    if not _finite_vector([pose.position.x, pose.position.y, pose.position.z]):
        return None
    orientation = pose.orientation
    if not _finite_vector(
        [orientation.x, orientation.y, orientation.z, orientation.w]
    ):
        return None
    lin = twist.linear
    ang = twist.angular
    if not _finite_vector([lin.x, lin.y, lin.z, ang.x, ang.y, ang.z]):
        return None
    out = Odometry()
    out.header = message.header
    out.header.frame_id = ODOM_FRAME
    out.child_frame_id = CHILD_FRAME
    out.pose = message.pose
    out.twist = message.twist
    out.pose.covariance = message.pose.covariance
    out.twist.covariance = message.twist.covariance
    return out


def transform_from_odometry(message):
    """Build the odom->base_link TransformStamped from normalized odometry."""
    transform = geometry_msgs.msg.TransformStamped()
    transform.header.stamp = message.header.stamp
    transform.header.frame_id = ODOM_FRAME
    transform.child_frame_id = CHILD_FRAME
    transform.transform.translation.x = message.pose.pose.position.x
    transform.transform.translation.y = message.pose.pose.position.y
    transform.transform.translation.z = message.pose.pose.position.z
    transform.transform.rotation = message.pose.pose.orientation
    return transform


class OdomAdapter(Node):
    """Publish normalized /vehicle/odom and the single dynamic odom tf."""

    def __init__(self):
        """Create the source subscription, publisher and tf broadcaster."""
        super().__init__('odom_adapter')
        self.declare_parameter('source_topic', '/vehicle/odom_gz')
        self.declare_parameter('target_topic', '/vehicle/odom')
        source = self.get_parameter('source_topic').value
        target = self.get_parameter('target_topic').value
        self.source_sub = self.create_subscription(
            Odometry, source, self.on_odom, 10)
        self.odom_pub = self.create_publisher(Odometry, target, 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

    def on_odom(self, message):
        """Publish the message only when its source frames and values pass."""
        normalized = normalize_odometry(message)
        if normalized is None:
            self.get_logger().warning(
                'rejected odometry: unexpected frames or non-finite values')
            return
        self.odom_pub.publish(normalized)
        self.tf_broadcaster.sendTransform(transform_from_odometry(normalized))


def main(args=None):
    """Run the odometry adapter until Ctrl+C."""
    rclpy.init(args=args)
    node = OdomAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
