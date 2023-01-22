#!/usr/bin/env python
# coding = utf-8
import rospy
from threading import Thread, Event
from flask import Flask, render_template, Response, jsonify, request
import signal, sys
from nav_msgs.msg import Path, Odometry
from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import PoseStamped, PoseArray
from tf.transformations import euler_from_quaternion

import json
import os
import subprocess
import re
import time


x_now = -1.0
y_now = -1.0
is_slam_end = False
is_navigation = False
is_player = False
flag = 1
object_code = -1
class_name = ''
event = Event()

def run_cmd( cmd_str='', echo_print=1):
    # print('hello')
    import subprocess
    devnull = open("/dev/null", "w")
    subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=devnull)
    devnull.close()


def get_name():
    global is_slam_end
    cmd="rosnode list"
    devnull = open("/dev/null", "w")
    ret = subprocess.Popen(cmd,shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=devnull )
    devnull.close()
    m = 0
    k = 0
    flag = True
    for i in iter(ret.stdout.readline,b""):
        data = i.decode().strip()
        if data == '/my_bag':
            flag = False
            break
        # print(data)
    if flag:
        is_slam_end = True


def callback_read_current_position(data):
    global x_now, y_now
    # print('position')
    x = data.pose.pose.position.x
    y = data.pose.pose.position.y
    qx = data.pose.pose.orientation.x
    qy = data.pose.pose.orientation.y
    qz = data.pose.pose.orientation.z
    qw = data.pose.pose.orientation.w

        # Convert the quaternion angle to eular angle
    quaternion = (qx,qy,qz,qw)
    euler = euler_from_quaternion(quaternion)
    yaw = euler[2]

    x_now = x 
    y_now = y



Thread(target=lambda: rospy.init_node('ros_backend', disable_signals=True)).start()
rospy.Subscriber('/pf/pose/odom', Odometry, callback_read_current_position, queue_size=1)
state_pub = rospy.Publisher("/vesc/low_level/ackermann_cmd_mux/input/teleop", AckermannDriveStamped, queue_size=1)


def signal_handler(signal, frame):
    rospy.signal_shutdown("end")
    sys.exit(0)

signal.signal(signal.SIGINT,signal_handler)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'


def get_stop_msg():
    ack = AckermannDriveStamped()
    ack.drive.speed = 0
    ack.drive.speed = 0
    return ack

# cnt=150 --- 3s
def send_stop_msg(cnt):
    global state_pub
    cnt = 0
    all_cnt = cnt
    rate = rospy.Rate(100)
    while cnt < all_cnt:
        state_pub = rospy.Publisher(
        "/vesc/low_level/ackermann_cmd_mux/input/teleop", AckermannDriveStamped, queue_size=1
    )
        ack = get_stop_msg()
        state_pub.publish(ack)
        rate.sleep()
        cnt += 1

def button_move(director):
    global state_pub   
    ack = AckermannDriveStamped()
    if director == 0:
        pass
    if director == 1:
        pass
    if director == 2:
        pass
    if director == 3:
        pass

def stop_navigation():
    if is_navigation:
        send_stop_msg(150)
    
def stop_slam_server():
    run_cmd("rosservice call /my_bag/pause_playback \"data: true\" ")

def start_slam_server():
    print('hello')
    run_cmd("rosservice call /my_bag/pause_playback \"data: false\" ")
    print('hello')

@app.route('/api')
def index():
    # return render_template('index.html')
    return "server start"

@app.route('/position')
def get_position():
    global object_code
    temp = -1
    if object_code != -1:
        temp = object_code
        object_code = -1
    get_name()
    return jsonify({"status": "success", "x": round(x_now,2), "y" :round( y_now,2), "object_code": temp, "class_name" : class_name,
                    "is_slam_end":is_slam_end})

@app.route('/move', methods=['GET','POST'])
def move():
    info = dict()
    info['statue'] = "fail"
    if request.method == 'POST':
        num = int(request.form['direction'])
        for i in range(3):
          publish_cb(num)
          time.sleep(0.1)

        info['statue'] = "success"
        info['direction'] = num
    return jsonify(info)

def publish_cb(num):
    ack = AckermannDriveStamped()
    if num == 2:
      ack.drive.speed = -0.5
    else:
        ack.drive.speed = 0.5
    # left
    if num == 1:
      ack.drive.steering_angle = 0.785
    # right
    elif num ==3:
        ack.drive.steering_angle = -0.785
    if state_pub is not None:
        state_pub.publish(ack)



def signal_handler(signal, frame):
    rospy.signal_shutdown("end")
    sys.exit(0)


signal.signal(signal.SIGINT,signal_handler)

if __name__ == '__main__':
    run_cmd('rosbag play --pause myrosbag.bag  --hz=10 __name:=my_bag')
    app.run( host='0.0.0.0', port=5000, debug=True)
