"""Tests for patrol command selection and dynamic parameters."""

from types import SimpleNamespace

from patrol.patrol import compute_command, Patrol
import rclpy
from rclpy.context import Context
from rclpy.parameter import Parameter
from turtlesim.msg import Pose


def make_pose():
    """Return a normal-looking turtle pose."""
    pose = Pose()
    pose.x = 5.5
    pose.y = 6.0
    pose.theta = 1.2
    return pose


def make_node(**kwargs):
    """Create a patrol node on a fresh ROS context."""
    context = Context()
    rclpy.init(context=context)
    return Patrol(context=context, **kwargs), context


def destroy_node(node, context):
    """Dispose a node created by make_node."""
    node.destroy_node()
    context.shutdown()


def test_zero_command_without_pose():
    """Before the first pose the command must be zero."""
    params = SimpleNamespace(initial_speed=0.5, turn_speed=0.3, period=0.1)
    command = compute_command(None, params)
    assert command.linear.x == 0.0
    assert command.linear.y == 0.0
    assert command.angular.z == 0.0


def test_command_with_params_given_at_startup():
    """Speeds specified at startup appear in the issued command."""
    pose = make_pose()
    params = SimpleNamespace(initial_speed=0.8, turn_speed=0.6, period=0.1)
    command = compute_command(pose, params)
    assert command.linear.x == 0.8
    assert command.angular.z == 0.6


def test_command_with_params_changed_in_callback():
    """After a parameter callback the new speeds drive the command."""
    pose = make_pose()
    params = SimpleNamespace(initial_speed=0.2, turn_speed=0.1, period=0.1)
    command = compute_command(pose, params)
    assert command.linear.x == 0.2
    assert command.angular.z == 0.1


def test_startup_params_reach_node_state():
    """Parameter overrides at node construction reach the node state."""
    node, context = make_node(parameter_overrides=[
        Parameter('initial_speed', Parameter.Type.DOUBLE, 0.8),
        Parameter('period', Parameter.Type.DOUBLE, 0.2),
    ])
    try:
        assert node.params.initial_speed == 0.8
        assert node.params.period == 0.2
        assert node.timer.timer_period_ns == 200000000
    finally:
        destroy_node(node, context)


def test_period_callback_changes_timer():
    """Setting period updates the state and the issuing timer."""
    node, context = make_node()
    try:
        old_timer = node.timer
        result = node.set_parameters(
            [Parameter('period', Parameter.Type.DOUBLE, 0.4)])
        assert result[0].successful
        assert node.params.period == 0.4
        assert node.timer is not old_timer
        assert node.timer.timer_period_ns == 400000000
        assert old_timer.is_canceled()
    finally:
        destroy_node(node, context)


def test_invalid_period_is_rejected():
    """Out-of-range period values are rejected and keep old state."""
    node, context = make_node()
    try:
        result = node.set_parameters(
            [Parameter('period', Parameter.Type.DOUBLE, -1.0)])
        assert not result[0].successful
        assert node.params.period == 0.1
    finally:
        destroy_node(node, context)
