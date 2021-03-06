#!/usr/bin/python 

'''
----------------------------
Author: Avishai Sintov
        Rutgers University
Date: October 2018
----------------------------
'''


import rospy
import numpy as np 
from std_msgs.msg import Float64, Float32MultiArray
from gazebo_msgs.msg import LinkStates
from rosgraph_msgs.msg import Clock
import PyKDL

windowSize = 10

class my_joint_state_publisher():

    joint_angles = None#, dtype=np.float32)
    joint_angles_prev = None
    joint_vels = None
    order = np.array([0,0,0,0,0,0,0,0,0])
    msg = Float32MultiArray()
    Gtype = None
    current_time = 0.0
    prev_time = 0.0
    win = np.array([])

    def __init__(self):
        rospy.init_node('my_joint_state_publisher', anonymous=True)

        if rospy.has_param('~gripper/gripper_type'):
            self.Gtype = rospy.get_param('~gripper/gripper_type')

        if self.Gtype == 'reflex' or self.Gtype == 'model_O':
            self.joint_angles = [0.,0.,0.,0.,0.,0.,0.,0.]
            self.joint_angles_prev = [0.,0.,0.,0.,0.,0.,0.,0.]
            self.joint_vels = [0.,0.,0.,0.,0.,0.,0.,0.]
        else:
            self.joint_angles = [0.,0.,0.,0.]
            self.joint_angles_prev = [0.,0.,0.,0.]
            self.joint_vels = [0.,0.,0.,0.]

        rospy.Subscriber('/gazebo/link_states', LinkStates, self.linkStatesCallback)
        rospy.Subscriber('/clock', Clock, self.ClockCallback)
        joint_states_pub = rospy.Publisher('/hand/my_joint_states', Float32MultiArray, queue_size=10)
        joint_vel_pub = rospy.Publisher('/hand/my_joint_velocities', Float32MultiArray, queue_size=10)

        rate = rospy.Rate(100)
        while not rospy.is_shutdown():
            # self.UpdateVelocities() # Update is now done in linkStatesCallback(.)

            self.msg.data = self.joint_angles
            joint_states_pub.publish(self.msg)

            self.msg.data = self.joint_vels
            joint_vel_pub.publish(self.msg)            

            # rospy.spin()
            rate.sleep()

    def linkStatesCallback(self, msg):

        self.getNameOrder(msg.name)

        q_world = PyKDL.Rotation.Quaternion(msg.pose[0].orientation.x, msg.pose[0].orientation.y, msg.pose[0].orientation.z, msg.pose[0].orientation.w)
        q_base = PyKDL.Rotation.Quaternion(msg.pose[self.order[0]].orientation.x, msg.pose[self.order[0]].orientation.y, msg.pose[self.order[0]].orientation.z, msg.pose[self.order[0]].orientation.w)
        if self.Gtype == 'reflex' or self.Gtype == 'model_O':
            q_1_1 = PyKDL.Rotation.Quaternion(msg.pose[self.order[1]].orientation.x, msg.pose[self.order[1]].orientation.y, msg.pose[self.order[1]].orientation.z, msg.pose[self.order[1]].orientation.w)
            q_1_2 = PyKDL.Rotation.Quaternion(msg.pose[self.order[2]].orientation.x, msg.pose[self.order[2]].orientation.y, msg.pose[self.order[2]].orientation.z, msg.pose[self.order[2]].orientation.w)
            q_1_3 = PyKDL.Rotation.Quaternion(msg.pose[self.order[3]].orientation.x, msg.pose[self.order[3]].orientation.y, msg.pose[self.order[3]].orientation.z, msg.pose[self.order[3]].orientation.w)
            q_2_1 = PyKDL.Rotation.Quaternion(msg.pose[self.order[4]].orientation.x, msg.pose[self.order[4]].orientation.y, msg.pose[self.order[4]].orientation.z, msg.pose[self.order[4]].orientation.w)
            q_2_2 = PyKDL.Rotation.Quaternion(msg.pose[self.order[5]].orientation.x, msg.pose[self.order[5]].orientation.y, msg.pose[self.order[5]].orientation.z, msg.pose[self.order[5]].orientation.w)
            q_2_3 = PyKDL.Rotation.Quaternion(msg.pose[self.order[6]].orientation.x, msg.pose[self.order[6]].orientation.y, msg.pose[self.order[6]].orientation.z, msg.pose[self.order[6]].orientation.w)
            q_3_2 = PyKDL.Rotation.Quaternion(msg.pose[self.order[7]].orientation.x, msg.pose[self.order[7]].orientation.y, msg.pose[self.order[7]].orientation.z, msg.pose[self.order[7]].orientation.w)
            q_3_3 = PyKDL.Rotation.Quaternion(msg.pose[self.order[8]].orientation.x, msg.pose[self.order[8]].orientation.y, msg.pose[self.order[8]].orientation.z, msg.pose[self.order[8]].orientation.w)
            # Velocity should be added here
        else:
            q_1_1 = PyKDL.Rotation.Quaternion(msg.pose[self.order[1]].orientation.x, msg.pose[self.order[1]].orientation.y, msg.pose[self.order[1]].orientation.z, msg.pose[self.order[1]].orientation.w)
            q_1_2 = PyKDL.Rotation.Quaternion(msg.pose[self.order[2]].orientation.x, msg.pose[self.order[2]].orientation.y, msg.pose[self.order[2]].orientation.z, msg.pose[self.order[2]].orientation.w)
            q_2_1 = PyKDL.Rotation.Quaternion(msg.pose[self.order[4]].orientation.x, msg.pose[self.order[4]].orientation.y, msg.pose[self.order[4]].orientation.z, msg.pose[self.order[4]].orientation.w)
            q_2_2 = PyKDL.Rotation.Quaternion(msg.pose[self.order[5]].orientation.x, msg.pose[self.order[5]].orientation.y, msg.pose[self.order[5]].orientation.z, msg.pose[self.order[5]].orientation.w)
            dq_1_1 = msg.twist[self.order[1]].angular.z
            dq_1_2 = msg.twist[self.order[2]].angular.z
            dq_2_1 = msg.twist[self.order[4]].angular.z
            dq_2_2 = msg.twist[self.order[5]].angular.z
        
        if self.Gtype == 'reflex':
            # self.joint_angles = [f1_1,f1_2,f1_3,f2_1,f2_2,f2_3,f3_2,f3_3]
            self.joint_angles[0] = (q_1_1.Inverse()*q_base).GetEulerZYX()[0]
            a = q_1_1.UnitZ()*q_1_2.UnitX()
            if a[1] > 0:
                self.joint_angles[1] = np.pi/2-np.arccos(PyKDL.dot(q_1_1.UnitZ(), q_1_2.UnitX()))+0.2807829
            else:
                self.joint_angles[1] = np.pi/2+np.arccos(PyKDL.dot(q_1_1.UnitZ(), q_1_2.UnitX()))+0.2807829
            self.joint_angles[2] = (q_1_3.Inverse()*q_1_2).GetEulerZYX()[1]  
            self.joint_angles[3] = (q_2_1.Inverse()*q_base).GetEulerZYX()[0]
            a = q_2_1.UnitZ()*q_2_2.UnitX() 
            if a[1] > 0:
                self.joint_angles[4] = np.pi/2-np.arccos(PyKDL.dot(q_2_1.UnitZ(), q_2_2.UnitX()))+0.2807829
            else:
                self.joint_angles[4] = np.pi/2+np.arccos(PyKDL.dot(q_2_1.UnitZ(), q_2_2.UnitX()))+0.2807829
            self.joint_angles[5] = (q_2_3.Inverse()*q_2_2).GetEulerZYX()[1] 
            a = q_base.UnitZ()*q_3_2.UnitX()
            if a[1] < 0:
                self.joint_angles[6] = np.pi/2-np.arccos(PyKDL.dot(q_base.UnitZ(), q_3_2.UnitX()))+0.2807829
            else:
                self.joint_angles[6] = np.pi/2+np.arccos(PyKDL.dot(q_base.UnitZ(), q_3_2.UnitX()))+0.2807829
            self.joint_angles[7] = (q_3_3.Inverse()*q_3_2).GetEulerZYX()[1]

        if self.Gtype == 'model_O':
            # self.joint_angles = [f1_1,f1_2,f1_3,f2_1,f2_2,f2_3,f3_2,f3_3]
            self.joint_angles[0] = np.mod(np.pi-(q_1_1.Inverse()*q_base).GetEulerZYX()[2], np.pi)
            self.joint_angles[1] = -(q_1_2.Inverse()*q_1_1).GetEulerZYX()[0]
            self.joint_angles[2] = -(q_1_3.Inverse()*q_1_2).GetEulerZYX()[0]
            self.joint_angles[3] = np.pi+(q_2_1.Inverse()*q_base).GetEulerZYX()[2] # Changes sign based on the rotation of the base - not currently important
            self.joint_angles[4] = -(q_2_2.Inverse()*q_2_1).GetEulerZYX()[0]
            self.joint_angles[5] = -(q_2_3.Inverse()*q_2_2).GetEulerZYX()[0] 
            self.joint_angles[6] = -(q_3_2.Inverse()*q_base).GetEulerZYX()[0]
            self.joint_angles[7] = -(q_3_3.Inverse()*q_3_2).GetEulerZYX()[0]

        if self.Gtype == 'model_T42':
            a = (q_1_1.Inverse()*q_base).GetEulerZYX()
            if a[0] < 0:
                self.joint_angles[0] = -a[1]
            else:
                self.joint_angles[0] = np.pi+a[1]
            self.joint_angles[1] = -(q_1_2.Inverse()*q_1_1).GetEulerZYX()[2]
            a = (q_2_1.Inverse()*q_base).GetEulerZYX()
            if a[0] < 0:
                self.joint_angles[2] = -a[1]
            else:
                self.joint_angles[2] = np.pi+a[1]
            self.joint_angles[3] = -(q_2_2.Inverse()*q_2_1).GetEulerZYX()[2]

            # Apply mean filter to joint velocities with windowSize
            if self.win.shape[0] < windowSize:
                self.joint_vels = np.array([-dq_1_1, -(dq_1_2 - dq_1_1), dq_2_1, dq_2_2 - dq_2_1]) # Currently finger velocity do not compensate base motion
                self.win = np.append(self.win, self.joint_vels).reshape(-1, 4)
            else:
                v = np.array([-dq_1_1, -(dq_1_2 - dq_1_1), dq_2_1, dq_2_2 - dq_2_1]) # Currently finger velocity do not compensate base motion
                self.win = np.append(self.win, v).reshape(-1, 4)
                self.joint_vels = np.mean(self.win, axis=0)
                self.win = np.delete(self.win, 0, axis=0)  
            self.joint_vels[np.abs(self.joint_vels) <= 0.1e-2] = 0.    

            # print self.joint_vels

    def ClockCallback(self, msg):
        self.current_time = msg.clock.secs + msg.clock.nsecs * 1e-9

    # Computes 1st-order joint velocities - Not used 
    def UpdateVelocities(self):

        dV = np.array(self.joint_angles) - np.array(self.joint_angles_prev)
        dT = self.current_time - self.prev_time

        self.joint_vels = np.true_divide(dV, dT if dT>0 else 1-3)
        self.joint_vels[np.abs(self.joint_vels) < 1e-2] = 0 # Suppress numerical errors that may cause vibrations

        self.joint_angles_prev = np.copy(self.joint_angles)
        self.prev_time = np.copy(self.current_time)


    def getNameOrder(self, names):

        for i, name in enumerate(names):
            str = name[-10:]
            # print(i,str)
            if str == ':base_link':
                self.order[0] = i
                continue
            if str == 'finger_1_1':
                self.order[1] = i
                continue
            if str == 'finger_1_2':
                self.order[2] = i
                continue
            if str == 'finger_1_3':
                self.order[3] = i
                continue
            if str == 'finger_2_1':
                self.order[4] = i
                continue
            if str == 'finger_2_2':
                self.order[5] = i
                continue
            if str == 'finger_2_3':
                self.order[6] = i
                continue
            if str == 'finger_3_2':
                self.order[7] = i
                continue
            if str == 'finger_3_3':
                self.order[8] = i
                continue



if __name__ == '__main__':

    try:
        my_joint_state_publisher()
    except rospy.ROSInterruptException:
        pass