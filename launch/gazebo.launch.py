#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

def generate_launch_description():
    pkg_gazebo_ros_actor_plugin = get_package_share_directory('gazebo_ros_actor_plugin')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    world_file = os.path.join(pkg_gazebo_ros_actor_plugin, 'config', 'worlds', 'move_actor.world')

    # Declare launch arguments
    verbose_arg = DeclareLaunchArgument(
        'verbose', 
        default_value='True', 
        description='Enable verbose mode for Gazebo'
    )
    headless_arg = DeclareLaunchArgument(
        'headless', 
        default_value='False', 
        description='Enable headless mode for Gazebo'
    )
    world_name_arg = DeclareLaunchArgument(
        'world_name', 
        default_value='move_actor', 
        description='Gazebo world name'
    )

    verbose = LaunchConfiguration('verbose')
    headless = LaunchConfiguration('headless')
    world_name = LaunchConfiguration('world_name')

    # The model path ("pkg_gazebo_ros_actor_plugin") needs to be added to the GZ_SIM_RESOURCE_PATH environment variable
    # to be able to find the models when spawning them in Gazebo. If this is not done here,
    # the models spawned into the world later will not be found. This includes .world-files
    # that might be in other packages as well.
    # Since this environment variable is appended, you can also easily add this manually
    # in any terminal before you start Gazebo within that terminal. 
    gz_resource_path = AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', pkg_gazebo_ros_actor_plugin)    
    gazebo_arguments = PythonExpression([f"'{world_file} -r'", " + (' -v' if '", verbose, "' == 'True' else '')", " + (' -s' if '", headless, "' == 'True' else '')"])
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')]),
        launch_arguments={
            'gz_args': gazebo_arguments
        }.items()
    )
    
    # for the ROS-Gazebo bridge, we need to bridge the /clock topic (used by node with use_sim_time=True) and the /spawn_entity service
    # the spawn-entity service is used to spawn models into the Gazebo world using ROS2 service calls (see spawn.launch.py)
    ros_gz_clock_bridge = PythonExpression(['"/world/', world_name, '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock"'])
    ros_gz_spawn_entity_bridge = PythonExpression(['"/world/', world_name, '/create@ros_gz_interfaces/srv/SpawnEntity"'])
    # The clock topic needs to be remapped from /world/<world_name>/clock to /clock since nodes expect the /clock topic in ROS2
    # without namespaces.
    remappings_gz_clock = [(PythonExpression(['"/world/', world_name, '/clock"']), '/clock')]
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gazebo_bridge',
        arguments=[
            ros_gz_clock_bridge, 
            ros_gz_spawn_entity_bridge
        ],
        remappings=remappings_gz_clock,
        output='screen'
    )

    ld = LaunchDescription()
    ld.add_action(verbose_arg)
    ld.add_action(headless_arg)
    ld.add_action(world_name_arg)
    ld.add_action(gz_resource_path)
    ld.add_action(gz_sim)
    ld.add_action(ros_gz_bridge)
    
    return ld