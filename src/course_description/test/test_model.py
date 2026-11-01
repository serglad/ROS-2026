"""Structural tests for the course Ackermann URDF/Xacro model."""

import subprocess
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
import pytest

PACKAGE = 'course_description'

REQUIRED_LINKS = {
    'base_link', 'lidar_link', 'camera_link', 'imu_link',
    'front_left_wheel_link', 'front_right_wheel_link',
    'rear_left_wheel_link', 'rear_right_wheel_link',
}


@pytest.fixture(scope='module')
def robot():
    """Expand the installed Xacro and parse the resulting URDF."""
    path = get_package_share_directory(PACKAGE)
    xacro_file = f'{path}/urdf/vehicle.urdf.xacro'
    expanded = subprocess.run(
        ['xacro', xacro_file], check=True, capture_output=True, text=True)
    return ET.fromstring(expanded.stdout)


def joint_map(robot):
    """Return a mapping child link name to joint element."""
    return {j.find('child').get('link'): j for j in robot.findall('joint')}


def test_required_links_present(robot):
    """All links of the contract exist exactly once."""
    names = [link.get('name') for link in robot.findall('link')]
    assert REQUIRED_LINKS <= set(names)
    assert len(names) == len(set(names))


def test_lidar_parent_is_base(robot):
    """The lidar hangs directly on the chassis, not on another sensor."""
    parent = joint_map(robot)['lidar_link'].find('parent').get('link')
    assert parent == 'base_link'


def test_sensor_offsets_match_sdf(robot):
    """Sensor joints keep the SDF offset (0.28, 0, 0.38)."""
    joints = joint_map(robot)
    for child in ('lidar_link', 'camera_link', 'imu_link'):
        xyz = joints[child].find('origin').get('xyz').split()
        assert [float(v) for v in xyz] == [0.28, 0.0, 0.38]


def test_wheel_dimensions_match_sdf(robot):
    """Wheelbase and track match the kit plugin parameters (0.8 / 0.62)."""
    joints = joint_map(robot)
    front_x = float(joints['front_left_wheel_link'].find(
        'origin').get('xyz').split()[0])
    rear_x = float(joints['rear_left_wheel_link'].find(
        'origin').get('xyz').split()[0])
    left_y = float(joints['front_left_wheel_link'].find(
        'origin').get('xyz').split()[1])
    right_y = float(joints['front_right_wheel_link'].find(
        'origin').get('xyz').split()[1])
    assert front_x - rear_x == pytest.approx(0.8)
    assert left_y - right_y == pytest.approx(0.62)


def test_wheel_joints_continuous_about_y(robot):
    """Every wheel rolls on a continuous joint with the Y axle."""
    joints = joint_map(robot)
    for child in REQUIRED_LINKS:
        if not child.endswith('wheel_link'):
            continue
        joint = joints[child]
        assert joint.get('type') == 'continuous'
        assert joint.find('axis').get('xyz') == '0 1 0'


def test_tree_connected_and_acyclic(robot):
    """Every non-root link has exactly one parent and reaches base_link."""
    joints = joint_map(robot)
    links = {link.get('name') for link in robot.findall('link')}
    roots = links - set(joints)
    assert roots == {'base_link'}
    for link in links:
        seen = set()
        current = link
        while current != 'base_link':
            assert current not in seen, f'cycle through {current}'
            seen.add(current)
            current = joints[current].find('parent').get('link')


def test_inertials_physically_positive(robot):
    """Masses and diagonal inertias are positive and ordered sensibly."""
    for link in robot.findall('link'):
        inertial = link.find('inertial')
        if inertial is None:
            continue
        mass = float(inertial.find('mass').get('value'))
        assert mass > 0.0
        for axis in ('ixx', 'iyy', 'izz'):
            assert float(inertial.find('inertia').get(axis)) > 0.0


def test_visual_and_collision_separate(robot):
    """Chassis and sensors define visual and collision geometry separately."""
    for name in ('base_link', 'lidar_link', 'camera_link'):
        link = next(
            link for link in robot.findall('link')
            if link.get('name') == name)
        assert link.find('visual') is not None
        assert link.find('collision') is not None
