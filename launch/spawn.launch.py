import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, AppendEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Constants for paths to different files and folders
    pkg_share = get_package_share_directory('gazebo_ros_actor_plugin')

    # Add model path to environment variable
    models_path = os.path.join(pkg_share, 'config', 'skins')
    params_file = os.path.join(pkg_share, 'params', 'spawner.yaml')
    sdf_model_path = os.path.join(models_path, 'DoctorFemaleWalk', 'model.sdf')
    append_gazebo_model_path_env_models = AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", models_path) 

    # Launch configuration variables specific to simulation
    model_name = LaunchConfiguration('model_name', default='Female-Doctor-Walking')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='0.0')
    roll_pose = LaunchConfiguration('roll_pose', default='0.0')
    pitch_pose = LaunchConfiguration('roll_pose', default='0.0')
    yaw_pose = LaunchConfiguration('yaw_pose', default='0.0')

    # Declare the launch arguments

    declare_model_name_cmd = DeclareLaunchArgument(
        name='model_name',
        default_value='Female-Doctor-Walking',
        description='Name of the model'
    )

    declare_spawn_x_val_cmd = DeclareLaunchArgument(
        name='x_pose',
        default_value='0.0',
        description='x pose of model to spawn'
    )

    declare_spawn_y_val_cmd = DeclareLaunchArgument(
        name='y_pose',
        default_value='0.0',
        description='y pose of model to spawn'
    )

    declare_spawn_z_val_cmd = DeclareLaunchArgument(
        name='z_pose',
        default_value='0.0',
        description='z pose of model to spawn'
    )

    declare_spawn_roll_cmd = DeclareLaunchArgument(
        name='roll_pose',
        default_value='0.0',
        description='Roll pose of model to spawn'
    )

    declare_spawn_pitch_cmd = DeclareLaunchArgument(
        name='pitch_pose',
        default_value='0.0',
        description='Pitch pose of model to spawn'
    )

    declare_spawn_yaw_cmd = DeclareLaunchArgument(
        name='yaw_pose',
        default_value='0.0',
        description='Yaw pose of model to spawn'
    )

    gazebo_resource_path_arg = DeclareLaunchArgument(
        'gazebo_resource_path', 
        default_value='', 
        description='Path(s) to add to environment so that Gazebo is capable to search for model files there.'
    )

    # 
    gazebo_resource_path = LaunchConfiguration('gazebo_resource_path')

    # add to environment 
    gz_resource_path = AppendEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gazebo_resource_path) 

    spawn_cmd = Node(
        package='ros_gz_sim', 
        executable='create',
        arguments=[
            '-file', sdf_model_path,
            '-name', model_name,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-Y', yaw_pose
        ],
        output='screen'              
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='actor_bridge',
        arguments=[
            'cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            'cmd_path@geometry_msgs/msg/PoseArray]gz.msgs.Pose_V',
        ],
        output='screen'
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(append_gazebo_model_path_env_models) 
    ld.add_action(declare_model_name_cmd)
    ld.add_action(declare_spawn_x_val_cmd)
    ld.add_action(declare_spawn_y_val_cmd)
    ld.add_action(declare_spawn_z_val_cmd)
    ld.add_action(declare_spawn_roll_cmd)
    ld.add_action(declare_spawn_pitch_cmd)
    ld.add_action(declare_spawn_yaw_cmd)
    ld.add_action(gazebo_resource_path_arg)
    ld.add_action(gz_resource_path)
    ld.add_action(ros_gz_bridge)

    # Add any actions
    ld.add_action(spawn_cmd)

    return ld
