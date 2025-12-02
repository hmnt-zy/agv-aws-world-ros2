from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription,LogInfo
from launch.actions import AppendEnvironmentVariable, TimerAction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration,FileContent,PathJoinSubstitution,EnvironmentVariable
from launch_ros.substitutions import FindPackageShare
from launch.conditions import UnlessCondition
import xacro
from launch.actions import SetEnvironmentVariable
from ament_index_python.packages import get_package_share_directory
import os
from ament_index_python.packages import get_package_share_directory
# os.environ['GZ_SIM_RESOURCE_PATH'] = os.environ.get('GZ_SIM_RESOURCE_PATH', '') + ':' + os.path.join(
#     get_package_share_directory('aws-robomaker-small-warehouse-world'), 'models')



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
    # setEnvironment('GZ_SIM_RESOURCE_PATH',os.path.join(get_package_share_directory('aws-robomaker-small-warehouse-world'),'models/'))
    # setEnvironment('GZ_SIM_RESOURCE_PATH',get_package_share_directory('agv_description'))
    use_sim_time=LaunchConfiguration('use_sim_time',default='true')
    urdf_path=os.path.join(FindPackageShare('agv_description').find('agv_description'),'urdf','agv.urdf.xacro')
    urdf_package=FindPackageShare('agv_description').find('agv_description')
    # set_env_vars_resources = AppendEnvironmentVariable(
    #     'GZ_SIM_RESOURCE_PATH',
    #     os.path.join(get_package_share_directory('aws-robomaker-small-warehouse-world'),
    #                  'models'))
    
    # os.environ['GZ_SIM_RESOURCE_PATH']=os.path.join(get_package_share_directory('aws-robomaker-small-warehouse-world'),'models')
    world_file_path=os.path.join(FindPackageShare('aws-robomaker-small-warehouse-world').find('aws-robomaker-small-warehouse-world'),'worlds','no_roof_small_warehouse','no_roof_small_warehouse.world')
    # world_file_path='empty.sdf'
    bridge_params = os.path.join(
    get_package_share_directory('aws-robomaker-small-warehouse-world'),
    'config',
    'bridge_param.yaml'
    )
    start_gazebo_ros_bridge_cmd = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '--ros-args',
        '-p',
        f'config_file:={bridge_params}',
    ],
    output='screen',
    )


    #ros2 launch ros_gz_sim gz_sim.launch.py
    start_gazebo_launch=IncludeLaunchDescription(
        PathJoinSubstitution(
            [FindPackageShare('ros_gz_sim'),'launch','gz_sim.launch.py']
        ),
        launch_arguments={'gz_args':[world_file_path,' -r']}.items()

    )
    start_description_launch=IncludeLaunchDescription(
        PathJoinSubstitution(
            [FindPackageShare('agv_description'),'launch','bot_description.launch.py']
        ),
        launch_arguments={'use_sim_time':'true'}.items()

    )

    spawn_urdf_model=Node(
        package='ros_gz_sim',
        executable='create',
        name='create',
        arguments=[
            '-topic','robot_description',
            '-name','aecbot',
            '-z','2',
        ],
        output='screen',
    )
    
    

    return LaunchDescription([
        # AppendEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value=os.path.join(get_package_share_directory('agv_description'),'meshes','OTAv07_meshes')),
        start_description_launch,
        SetEnvironmentVariable(name='GZ_SIM_RESOURCE_PATH', value='/home/arz-1013/tbot_ws/install/aws-robomaker-small-warehouse-world/share/aws-robomaker-small-warehouse-world/models'),
        SetEnvironmentVariable( name='GZ_SIM_RESOURCE_PATH',value=os.path.join(get_package_share_directory('aws-robomaker-small-warehouse-world'),'models') + os.pathsep + os.path.dirname(get_package_share_directory('agv_description'))),
        start_gazebo_launch,
        start_gazebo_ros_bridge_cmd,
        spawn_urdf_model,
        LogInfo(msg='--------------------------------'),
        LogInfo(msg='--------------------------------'),
        LogInfo(msg=EnvironmentVariable('GZ_SIM_RESOURCE_PATH')),
        LogInfo(msg='--------------------------------'),
        LogInfo(msg='--------------------------------'),
    ])

