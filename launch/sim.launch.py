#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch import LaunchDescription


def generate_launch_description():
    pkg_gazebo_ros_actor_plugin = get_package_share_directory('gazebo_ros_actor_plugin')

    gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_gazebo_ros_actor_plugin, 'launch', 'gazebo.launch.py')]),
    )

    spawner_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_gazebo_ros_actor_plugin, 'launch', 'spawn.DoctorFemaleWalk.launch.py')])
    )

    ld = LaunchDescription()
    ld.add_action(gazebo_cmd)
    ld.add_action(spawner_cmd)

    return ld
