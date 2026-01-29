import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Constants for paths to different files and folders
    pkg_share = get_package_share_directory('gazebo_ros_actor_plugin')
    namespace = LaunchConfiguration('namespace', default='')

    declare_actor_namespace_cmd = DeclareLaunchArgument(
        name='namespace',
        default_value='',
        description='Namespace of the path publisher.'
    )

    path_publisher_cmd = Node(
        package='gazebo_ros_actor_plugin', 
        executable='path_publisher.py',
        namespace=namespace,
        parameters=[os.path.join(pkg_share, 'config', 'path_publisher.yaml')],
        name='path_publisher',
        output='screen'              
    )


    # 
    ld = LaunchDescription()
    ld.add_action(declare_actor_namespace_cmd)
    ld.add_action(path_publisher_cmd)

    return ld
