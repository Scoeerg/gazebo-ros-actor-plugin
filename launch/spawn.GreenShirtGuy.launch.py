import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, AppendEnvironmentVariable
from launch.substitutions import LaunchConfiguration, Command, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # Constants for paths to different files and folders
    pkg_share = get_package_share_directory('gazebo_ros_actor_plugin')

    # Add model path to environment variable
    models_path = os.path.join(pkg_share, 'config', 'skins')
    xacro_sdf_model_path = os.path.join(models_path, 'GreenShirtGuy', 'model.sdf.xacro')

    # Launch configuration variables specific to simulation
    model_name = LaunchConfiguration('model_name', default='GreenShirtGuy')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    z_pose = LaunchConfiguration('z_pose', default='1.0')
    roll_pose = LaunchConfiguration('roll_pose', default='0.0')
    pitch_pose = LaunchConfiguration('pitch_pose', default='0.0')
    yaw_pose = LaunchConfiguration('yaw_pose', default='0.0')
    namespace = LaunchConfiguration('actor_namespace', default='')
    follow_mode = LaunchConfiguration('follow_mode', default='velocity')
    linear_velocity = LaunchConfiguration('max_velocity', default='1.0')
    publish_pose = LaunchConfiguration('publish_pose', default='true')
    pose_publish_rate = LaunchConfiguration('pose_publish_rate', default='30.0')
    gazebo_topic_prefix = LaunchConfiguration('gazebo_topic_prefix', default='')
    gazebo_resource_path = LaunchConfiguration('gazebo_resource_path')

    declare_model_name_cmd = DeclareLaunchArgument(
        name='model_name',
        default_value='GreenShirtGuy',
        description='Name of the model in Gazebo.'
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
        default_value='1.0',
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

    declare_actor_namespace_cmd = DeclareLaunchArgument(
        name='actor_namespace',
        default_value='',
        description='Namespace of the Gazebo actor in ROS'
    )

    declare_follow_mode_cmd = DeclareLaunchArgument(
        name='follow_mode',
        default_value='velocity',
        description='Mode of the actor. Can be string "velocity" or "path"'
    )

    declare_max_velocity_cmd = DeclareLaunchArgument(
        name='max_velocity',
        default_value='1.0',
        description='Maximum translational velocity of actor. Must be positive float.'
    )

    declare_publish_pose_cmd = DeclareLaunchArgument(
        name='publish_pose',
        default_value='true',
        description='If Actor should publish its gazebo-world-frame pose to a topic.'
    )

    declare_pose_publish_rate_cmd = DeclareLaunchArgument(
        name='pose_publish_rate',
        default_value='30.0',
        description='Publishing rate of the actor pose in Hz.'
    )

    declare_gazebo_topic_prefix_cmd = DeclareLaunchArgument(
        name='gazebo_topic_prefix',
        default_value='',
        description='Prefix of Gazebo(!) topics of actor. Useful when spawning multiple actors to avoid topic name clashes.'
    )

    model_string = Command([
        'xacro ', xacro_sdf_model_path,
        ' actor_name:=', model_name,
        ' gazebo_topic_prefix:=', gazebo_topic_prefix,
        ' follow_mode:=', follow_mode,
        ' linear_velocity:=', linear_velocity,
        ' publish_pose:=', publish_pose,
        ' pose_publish_rate:=', pose_publish_rate,
        ' pose_offset_x:=', x_pose,
        ' pose_offset_y:=', y_pose,
        ' pose_offset_z:=', z_pose,
        ' pose_offset_roll:=', roll_pose,
        ' pose_offset_pitch:=', pitch_pose,
        ' pose_offset_yaw:=', yaw_pose
    ])

    # add to environment 
    gz_resource_path = AppendEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=gazebo_resource_path) 
    append_gazebo_model_path_env_models = AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", models_path) 

    # Spawn the actor in Gazebo
    spawn_cmd = Node(
        package='ros_gz_sim', 
        executable='create',
        arguments=[
            '-string', model_string,
            '-name', model_name,
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-Y', yaw_pose,
            '-P', pitch_pose,
            '-R', roll_pose,
            '-allow_renaming' # so you can spawn multiple actors
        ],
        output='screen'              
    )

    # Bridge to control the actor via ROS2 topics
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='actor_bridge',
        arguments=[
             PythonExpression([
                "'", model_name, "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'"
            ]),
            PythonExpression([
                "'", model_name, "/cmd_path@geometry_msgs/msg/PoseArray]gz.msgs.Pose_V'"
            ]),
            PythonExpression([
                "'", model_name, "/pose@geometry_msgs/msg/Pose[gz.msgs.Pose'"
            ]),
        ],
        namespace=namespace,
        output='screen'
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    # launch arguments
    ld.add_action(gazebo_resource_path_arg)
    ld.add_action(declare_model_name_cmd)
    ld.add_action(declare_spawn_x_val_cmd)
    ld.add_action(declare_spawn_y_val_cmd)
    ld.add_action(declare_spawn_z_val_cmd)
    ld.add_action(declare_spawn_roll_cmd)
    ld.add_action(declare_spawn_pitch_cmd)
    ld.add_action(declare_spawn_yaw_cmd)
    ld.add_action(declare_actor_namespace_cmd)
    ld.add_action(declare_follow_mode_cmd)
    ld.add_action(declare_max_velocity_cmd)
    ld.add_action(declare_publish_pose_cmd)
    ld.add_action(declare_pose_publish_rate_cmd)
    ld.add_action(declare_gazebo_topic_prefix_cmd)
    # Gazebo model path adding / environmet variables
    ld.add_action(append_gazebo_model_path_env_models) 
    ld.add_action(gz_resource_path)
    # ROS-Gazebo bridge
    ld.add_action(ros_gz_bridge)
    # Spawn model
    ld.add_action(spawn_cmd)

    return ld
