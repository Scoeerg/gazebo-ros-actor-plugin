#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Quaternion, PoseArray, Pose


class PoseArrayPublisher(Node):
    def __init__(self):
        super().__init__('path_publisher')

        # Declare parameter with default circle
        self.declare_parameter(
            'waypoints',
            [  2.0, 0.0, 0.0, 0.0, 0.0, 1.5707963267948966,
               1.618033988749895, 1.1755705045849463, 0.0, 0.0, 0.0, 2.199114857512855,
               0.6180339887498949, 1.902113032590307, 0.0, 0.0, 0.0, 2.827433388230814,
               -0.6180339887498947, 1.9021130325903073, 0.0, 0.0, 0.0, 3.4557519189487724,
               -1.6180339887498947, 1.1755705045849465, 0.0, 0.0, 0.0, 4.084070449666731,
               -2.0, 2.4492935982947064e-16, 0.0, 0.0, 0.0, 4.71238898038469,
               -1.6180339887498951, -1.175570504584946, 0.0, 0.0, 0.0, 5.340707511102648,
               -0.6180339887498951, -1.902113032590307, 0.0, 0.0, 0.0, 5.969026041820607,
               0.6180339887498945, -1.9021130325903073, 0.0, 0.0, 0.0, 6.5973445725385655,
               1.6180339887498947, -1.1755705045849467, 0.0, 0.0, 0.0, 7.225663103256524
            ]
        )
        self.declare_parameter('frame', "")
        self.declare_parameter('topic', "cmd_path")

        # If no waypoints provided, fall back to generating the circle
        waypoints_param = self.get_parameter('waypoints').get_parameter_value().double_array_value
        if len(waypoints_param) % 6 != 0:
            self.get_logger().error('Waypoints parameter must be multiples of 6 [x,y,z,roll,pitch,yaw]')
            raise ValueError("Invalid waypoints format")
        self.waypoints = []
        for i in range(0, len(waypoints_param), 6):
            x, y, z, roll, pitch, yaw = waypoints_param[i:i+6]
            self.waypoints.append((x, y, z, roll, pitch, yaw))

        # Publisher
        self.publisher = self.create_publisher(PoseArray, self.get_parameter('topic').value, 10)
        self.get_logger().info('PoseArray publisher node started')

    def publish_pose_array(self):
        pose_array_msg = PoseArray()
        pose_array_msg.header.stamp = self.get_clock().now().to_msg()
        pose_array_msg.header.frame_id = self.get_parameter('frame').value

        for x, y, z, roll, pitch, yaw in self.waypoints:
            pose = Pose()
            pose.position = Point(x=x, y=y, z=z)

            quat = self.euler_to_quaternion(roll, pitch, yaw)
            pose.orientation = Quaternion(x=quat[0], y=quat[1], z=quat[2], w=quat[3])

            pose_array_msg.poses.append(pose)

        self.publisher.publish(pose_array_msg)
        self.get_logger().info(f'Published PoseArray with {len(self.waypoints)} poses')

    def euler_to_quaternion(self, roll, pitch, yaw):
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)

        return (
            sr * cp * cy - cr * sp * sy,  # x
            cr * sp * cy + sr * cp * sy,  # y
            cr * cp * sy - sr * sp * cy,  # z
            cr * cp * cy + sr * sp * sy   # w
        )


def main(args=None):
    rclpy.init(args=args)
    node = PoseArrayPublisher()
    node.publish_pose_array()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()