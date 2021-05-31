from sensor_msgs.msg import PointCloud2
from sensor_msgs.msg import LaserScan

from sensor_msgs import point_cloud2
import rospy
import pcl.pcl_visualization
import pcl
import numpy

# visual=[]
def callback_pointcloud(data):
    # point_pub = rospy.Publisher('/pointcloud_list', Float32, queue_size=10)
    dat = point_cloud2.read_points(data, field_names=("x", "y", "z", "intensity"), skip_nans=True)
    print(type(dat))
    pc_list = []
    for d in dat:
        pc_list.append([d[0], d[1], d[2], 100])

    # print(" x: {:.3f},  y: {:.3f}, z: {:.3f}".format(d[0], d[1], d[2]))
    # point_pub.publish(pc_list)

    pcl_data = pcl.PointCloud_PointXYZRGB()
    pcl_data.from_list(pc_list)
    '''
    p = pcl.PointCloud()
    p.from_list(pc_list)
    seg = p.make_segmenter()
    seg.set_model_type(pcl.SACMODEL_PLANE)
    seg.set_method_type(pcl.SAC_RANSAC)
    indices, model = seg.segment()
    '''

    # seg =pcl_data.make_segmenter()
    visual.ShowColorCloud(pcl_data)
    # visual.ShowMonochromeCloud(pcl_data)
    # flag = True
    # while flag:


# flag != visual.WasStopped()


def pointcloudshow():
    # rospy.init_node('point_list', anonymous=True)
    global visual
    visual = pcl.pcl_visualization.CloudViewing()
    rospy.Subscriber('/rslidar_points', PointCloud2, callback_pointcloud, queue_size=2)
    # rospy.spin()

