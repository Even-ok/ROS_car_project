
import os
import signal
from threading import Lock


import rospy
from ackermann_msgs.msg import AckermannDriveStamped

state_lock = Lock()
root = None
#state = [False, False, False, False]


def shutdown():
    root.destroy()
    rospy.signal_shutdown("shutdown")

def publish_button(dir,state):
    with state_lock:

        if  dir == "0": # UP w go forward
            state[0] = True
            state[2] = False
        elif dir == "1": # LEFT a go left
            state[1] = True
            state[3] = False
        elif dir == "2": # DOWN s back
            state[2] = True
            state[0] = False
        elif dir == "3": # RIGHT d go right
            state[3] = True
            state[1] = False

        ack = AckermannDriveStamped()
        if state[0]:
            ack.drive.speed = max_velocity
        elif state[2]:
            ack.drive.speed = -max_velocity

        if state[1]:
            ack.drive.steering_angle = max_steering_angle
            ack.drive.speed = 0.8
        elif state[3]:
            ack.drive.steering_angle = -max_steering_angle
            ack.drive.speed = 0.8

        # if state_pub is not None:
        #     state_pub.publish(ack)

    return ack

def main():
    global state_pub
    global root

    global max_velocity
    global max_steering_angle

    max_velocity = rospy.get_param("~speed", 2.0)
    max_steering_angle = rospy.get_param("~max_steering_angle", 0.34)
    state_pub = rospy.Publisher(
        "/vesc/low_level/ackermann_cmd_mux/input/teleop", AckermannDriveStamped, queue_size=1
    )
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        state = [False, False, False, False]
        dir = input("Please input derection:")

        state_pub = rospy.Publisher(
        "/vesc/low_level/ackermann_cmd_mux/input/teleop", AckermannDriveStamped, queue_size=1
    )
        ack = publish_button(dir,state)
        state_pub.publish(ack)
        rate.sleep()

        # rospy.Timer(rospy.Duration(0.1), publish_button(dir))
    

if __name__ == "__main__":
    rospy.init_node("button_control", disable_signals=True)

    signal.signal(signal.SIGINT, lambda s, f: shutdown())
    main()