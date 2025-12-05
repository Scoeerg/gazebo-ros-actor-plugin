#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch import LaunchDescription


def generate_launch_description():
    pkg_gazebo_ros_actor_plugin = get_package_share_directory('gazebo_ros_actor_plugin')
    model_path = os.path.join(pkg_gazebo_ros_actor_plugin, 'config', 'skins')

    # starts Gazebo. Takes the model path as argument to be able to find the models
    # that we spawn later on with the spawner launch file. This way you can easily
    # copy the working of this launch file to use your own .world files and models
    # since you most likely want to use different ones than this minimal example.
    gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_gazebo_ros_actor_plugin, 'launch', 'gazebo.launch.py')]),
        launch_arguments={
            'gazebo_resource_path': model_path,
        }.items()
    )
    # spawns the actor model in Gazebo. The launch file responsible to start Gazebo, and the ROS2-bridge
    # needs to have the model path in the GZ_SIM_RESOURCE_PATH environment variable so that
    # Gazebo can find the model when we spawn it here.
    spawner_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_gazebo_ros_actor_plugin, 'launch', 'spawn.launch.py')])
    )

    ld = LaunchDescription()
    ld.add_action(gazebo_cmd)
    ld.add_action(spawner_cmd)

    return ld
