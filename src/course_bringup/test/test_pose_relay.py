"""Tests for course_bringup QoS selection."""

from course_bringup.pose_relay import (
    make_publisher_qos,
    make_subscriber_qos,
)
import pytest
from rclpy.qos import QoSReliabilityPolicy


def test_publisher_is_best_effort():
    """The sensor relay publishes with best effort."""
    assert make_publisher_qos().reliability == QoSReliabilityPolicy.BEST_EFFORT


def test_subscriber_best_effort_matches_publisher():
    """best_effort subscriber profile matches the best effort publisher."""
    qos = make_subscriber_qos('best_effort')
    assert qos.reliability == QoSReliabilityPolicy.BEST_EFFORT
    assert qos.depth == 10


def test_subscriber_reliable_profile():
    """Reliable name yields the RELIABLE policy."""
    qos = make_subscriber_qos('reliable')
    assert qos.reliability == QoSReliabilityPolicy.RELIABLE


def test_unknown_reliability_rejected():
    """Unknown reliability names are rejected with ValueError."""
    with pytest.raises(ValueError):
        make_subscriber_qos('once_in_a_while')
