#!/usr/bin/env python
from __future__ import print_function
import rospy
from std_msgs.msg import String
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
from sensor_msgs.msg import Joy

import sys
import json
from math import sqrt
from collections import deque

import time


if not rospy.has_param("~max_list_append"):
        rospy.logwarn('The parameter max_list_append dont exists')
max_append = rospy.set_param("~max_list_append",10000) 
max_append = 10000
if not (max_append > 0):
        rospy.logwarn('The parameter max_list_append not is correct')
        sys.exit()


class path_marker:
        def __init__(self):
                self.path = Path() #creamos el mensaje path de tipo path 
                self.msg = Odometry()
                self.pub = rospy.Publisher('/path', Path, queue_size=1)
                rospy.Subscriber('/pf/pose/odom', Odometry, self.callback) 



        def callback(self,data):
                global xAnt
                global yAnt
                global cont
                xAnt=0.0
                yAnt=0.0
                cont=0

        #Is created the pose msg, its necessary do it each time because Python manages objects by reference, 
                #and does not make deep copies unless explicitly asked to do so.
                pose = PoseStamped()    

        #Set a atributes of the msg
                pose.header.frame_id = "map"
                pose.pose.position.x = float(data.pose.pose.position.x)
                pose.pose.position.y = float(data.pose.pose.position.y)
                pose.pose.orientation.x = float(data.pose.pose.orientation.x)
                pose.pose.orientation.y = float(data.pose.pose.orientation.y)
                pose.pose.orientation.z = float(data.pose.pose.orientation.z)
                pose.pose.orientation.w = float(data.pose.pose.orientation.w)

        #To avoid repeating the values, it is found that the received values are differents
                if (xAnt != pose.pose.position.x and yAnt != pose.pose.position.y):
                        #Set a atributes of the msg
                        pose.header.seq = self.path.header.seq + 1
                        self.path.header.frame_id="map"
                        self.path.header.stamp=rospy.Time.now()
                        pose.header.stamp = self.path.header.stamp
                        self.path.poses.append(pose)
                        #Published the msg

                cont=cont+1

                rospy.loginfo("Valor del contador: %i" % cont)
                if cont>max_append:
                                self.path.poses.pop(0)

                self.pub.publish(self.path)

        #Save the last position
                xAnt=pose.pose.orientation.x
                yAnt=pose.pose.position.y
                return self.path

if  __name__ == '__main__':
        #Variable initialization
        # global xAnt
        # global yAnt
        # global cont
        # xAnt=0.0
        # yAnt=0.0
        # cont=0

        #Node and msg initialization
        rospy.init_node('show_path')
        node = path_marker()
        rospy.spin()



        # #Subscription to the topic
        # rate = rospy.Rate(30) # 30hz
        # while not rospy.is_shutdown():
        #     msg = rospy.Subscriber('/pf/pose/odom', Odometry, callback) 
        #     rate.sleep()
        #     rospy.spin()

 