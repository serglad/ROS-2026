"""Tests for the pure patrol command selection."""

from patrol.patrol import choose_command
from turtlesim.msg import Pose


def test_zero_command_without_pose():
    """Before the first pose the command must be zero."""
    command = choose_command(None)
    assert command.linear.x == 0.0
    assert command.linear.y == 0.0
    assert command.angular.z == 0.0


def test_cruise_command_after_normal_pose():
    """After a normal pose the fixed cruise command is issued."""
    pose = Pose()
    pose.x = 5.5
    pose.y = 6.0
    pose.theta = 1.2
    command = choose_command(pose)
    assert command.linear.x == 0.5
    assert command.angular.z == 0.3
