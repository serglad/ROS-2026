"""Unit tests for the drive and odometry adapter contracts."""

import math

from course_simulation.drive_adapter import twist_from_drive
from course_simulation.odom_adapter import normalize_odometry
from nav_msgs.msg import Odometry


def test_straight_motion():
    """Positive speed with zero steering gives forward linear motion only."""
    twist, reason = twist_from_drive(0.5, 0.0, 0.0)
    assert reason == ''
    assert twist.linear.x == 0.5
    assert twist.angular.z == 0.0


def test_turn_from_steering_angle():
    """Steering is mapped to body yaw rate with the 0.8 m wheelbase."""
    twist, reason = twist_from_drive(0.4, 0.2, 0.0)
    assert reason == ''
    assert math.isclose(twist.angular.z, 0.4 * math.tan(0.2) / 0.8)


def test_zero_speed_no_rotation_in_place():
    """At v = 0 the Ackermann chassis must not rotate."""
    twist, reason = twist_from_drive(0.0, 0.4, 0.0)
    assert reason == ''
    assert twist.linear.x == 0.0
    assert twist.angular.z == 0.0


def test_speed_and_steering_are_clamped():
    """Out-of-range commands are clamped to the contract limits."""
    twist, reason = twist_from_drive(5.0, 1.0, 0.0)
    assert reason == ''
    assert twist.linear.x == 1.2
    assert math.isclose(twist.angular.z, 1.2 * math.tan(0.45) / 0.8)
    twist, _ = twist_from_drive(-1.0, -1.0, 0.0)
    assert twist.linear.x == 0.0


def test_stale_command_is_zero():
    """A command older than 0.25 s yields a zero Twist with a reason."""
    twist, reason = twist_from_drive(0.5, 0.1, 0.26)
    assert reason == 'stale'
    assert twist.linear.x == 0.0
    assert twist.angular.z == 0.0


def test_non_finite_command_is_zero():
    """A NaN or infinite field yields a zero Twist with a reason."""
    for speed, steering in [(float('nan'), 0.0), (0.5, float('inf'))]:
        twist, reason = twist_from_drive(speed, steering, 0.0)
        assert reason == 'non_finite'
        assert twist.linear.x == 0.0
        assert twist.angular.z == 0.0


def _source_odometry():
    message = Odometry()
    message.header.stamp.sec = 7
    message.header.stamp.nanosec = 250
    message.header.frame_id = 'course_ackermann/odom'
    message.child_frame_id = 'course_ackermann/base_link'
    message.pose.pose.position.x = 1.5
    message.pose.pose.position.y = -0.25
    message.pose.pose.orientation.w = 1.0
    message.twist.twist.linear.x = 0.5
    message.pose.covariance[0] = 0.01
    message.twist.covariance[0] = 0.02
    return message


def test_odometry_frames_normalized_and_stamp_preserved():
    """Frames lose exactly the course_ackermann/ prefix, stamp is kept."""
    out = normalize_odometry(_source_odometry())
    assert out is not None
    assert out.header.frame_id == 'odom'
    assert out.child_frame_id == 'base_link'
    assert out.header.stamp.sec == 7
    assert out.header.stamp.nanosec == 250


def test_odometry_pose_twist_and_covariance_preserved():
    """Pose, twist and both covariance matrices survive normalization."""
    source = _source_odometry()
    out = normalize_odometry(source)
    assert out.pose.pose.position.x == 1.5
    assert out.pose.pose.position.y == -0.25
    assert out.twist.twist.linear.x == 0.5
    assert out.pose.covariance[0] == 0.01
    assert out.twist.covariance[0] == 0.02
    assert list(out.pose.covariance) == list(source.pose.covariance)
    assert list(out.twist.covariance) == list(source.twist.covariance)


def test_odometry_with_unexpected_frames_rejected():
    """Messages with other source frames are rejected."""
    source = _source_odometry()
    source.header.frame_id = 'map'
    assert normalize_odometry(source) is None
    source = _source_odometry()
    source.child_frame_id = 'base_link'
    assert normalize_odometry(source) is None


def test_odometry_with_non_finite_values_rejected():
    """Messages with non-finite pose or twist are rejected."""
    source = _source_odometry()
    source.pose.pose.position.x = float('nan')
    assert normalize_odometry(source) is None
    source = _source_odometry()
    source.twist.twist.linear.x = float('inf')
    assert normalize_odometry(source) is None
