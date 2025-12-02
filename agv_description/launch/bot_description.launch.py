from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration,FileContent,PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch.conditions import UnlessCondition
from launch.actions import SetEnvironmentVariable
from ament_index_python.packages import get_package_share_directory
import xacro
import os

def setEnvironment(setVariable,newPath):
    try:
        currentPath=os.environ[setVariable]
    except KeyError:
        os.environ[setVariable]=''
        currentPath=os.environ[setVariable]
    if newPath not in currentPath:
        newPath = currentPath+os.pathsep+newPath
        os.environ[setVariable]=newPath
        return 1
    return 0
    
    
def generate_launch_description():
    # setEnvironment('GZ_SIM_RESOURCE_PATH',get_package_share_directory('agv_description'))
    use_sim_time=LaunchConfiguration('use_sim_time',default='false')
    urdf_file=LaunchConfiguration('urdf_file')
    # urdf_path=LaunchConfiguration('urdf_path',default=PathJoinSubstitution([FindPackageShare('agv_description'),'urdf','agv.urdf.xacro']))
    # urdf_content=FileContent(urdf_file)

    # urdf_path=os.path.join(FindPackageShare('agv_description').find('agv_description'),'urdf','aecbot.urdf')
    urdf_path=os.path.join(FindPackageShare('agv_description').find('agv_description'),'urdf','agv.urdf.xacro')
    urdf_content= xacro.process_file(urdf_path).toxml()
    # urdf_content=FileContent(PathJoinSubstitution([FindPackageShare('agv_description'),'urdf', 'aecbot.urdf']))
    # with open(urdf_path, 'r') as infp:
    #     urdf_content = infp.read()

    rviz_config_file=LaunchConfiguration('rviz_file',default=PathJoinSubstitution([FindPackageShare('agv_description'),'config','rviz_config.rviz']))

    start_rviz_node=Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=["-d",rviz_config_file],
        output='screen'

    )
    start_rsp_node=Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description':urdf_content,
        }],
        output='screen'
    )
    start_jsp_node=Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        arguments=[
        '--ros-args',
        '--log-level', 'joint_state_publisher:=debug'
    ],
        output='screen',
        condition=UnlessCondition(use_sim_time),
        
    )


    return LaunchDescription([
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=get_package_share_directory('agv_description')),
        start_rsp_node,
        start_rviz_node,
        start_jsp_node
    ])