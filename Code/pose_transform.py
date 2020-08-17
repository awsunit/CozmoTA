#!/usr/bin/env python3

'''
This is starter code for Lab 7 on Coordinate Frame transforms.

'''

import asyncio
import cozmo
import numpy
from cozmo.objects import CustomObjectTypes, CustomObjectMarkers
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps
import math
from math import sin, cos
import numpy as np
import time
import sys

def get_relative_pose(object_pose, reference_frame_pose):
	# ####
	# TODO: Implement computation of the relative frame using numpy.
	# Try to derive the equations yourself and verify by looking at
	# the books or slides before implementing.
	# ####

	ox, oy, oz = object_pose.position.x_y_z
	orad = object_pose.rotation.angle_z.radians

	rx, ry, rz = reference_frame_pose.position.x_y_z
	rrad = reference_frame_pose.rotation.angle_z.radians

	# rotational/translational matrix of cozmo's coord system
	rc = [cos(rrad), -sin(rrad), rx, sin(rrad), cos(rrad), ry, 0, 0, 1]

	r_matrix = np.array(rc).reshape(3,3)
	r_matrix_inv = np.linalg.inv(r_matrix)

	# world coordinates of object
	ac = np.array([ox , oy, 1])

	# (a.M.b)^-1 * P.a = P.b
	nx, ny, _ = r_matrix_inv.dot(ac)

	# relative angle of object to Cozmo
	n_angle = (orad - rrad) #% (np.pi)

	p = Pose(nx, ny, oz, angle_z=Angle(radians=n_angle))
	return p


def find_relative_cube_pose(robot: cozmo.robot.Robot):
	'''Looks for a cube while sitting still, prints the pose of the detected cube
	in world coordinate frame and relative to the robot coordinate frame.'''

	robot.move_lift(-3)
	print("skipped")
	robot.set_head_angle(degrees(0)).wait_for_completed()
	cube = None

	while True:
		try:
			cube = robot.world.wait_for_observed_light_cube(timeout=30)
			if cube:
				print("Robot pose: %s" % robot.pose)
				print("Cube pose: %s" % cube.pose)
				rp = get_relative_pose(cube.pose, robot.pose)
				print("Cube pose in the robot coordinate frame: %s" % rp)
				time.sleep(2)

		except asyncio.TimeoutError:
			print("Didn't find a cube")



def move_relative_to_cube(robot: cozmo.robot.Robot):
	'''Looks for a cube while sitting still, when a cube is detected it 
	moves the robot to a given pose relative to the detected cube pose.'''

	# cozmo_turn_in_place(robot, 360, 90)
	robot.move_lift(-3)
	robot.set_head_angle(degrees(0)).wait_for_completed()
	cube = None
	# cust = robot.world.define_custom_wall(CustomObjectTypes.CustomType00,
	# 									  CustomObjectMarkers.Diamonds2,
	# 									  50.8 , 76.2,
	# 									  25.4, 25.4, True)

	while cube is None:
		try:
			#cube = robot.world.wait_for_observed_light_cube(timeout=30)
			cube = robot.world.wait_for(cozmo.objects.EvtObjectAppeared)
			if cube:
				print("Found a cube: %s" % cube.pose)

		except asyncio.TimeoutError:
			print("Didn't find a cube")

	desired_pose_relative_to_cube = Pose(0, 100, 0, angle_z=degrees(90))

	# ####
	# TODO: Make the robot move to the given desired_pose_relative_to_cube,
	# which you will need to tune based on the action you perform on the cube.
	# Use the get_relative_pose function your implemented to determine the
	# desired robot pose relative to the robot's current pose and then use
	# navigation functions below to move it there. Once the robot reaches the
	# desired relative pose, it should perform an action on the cube using its
	# forklift and/or base movement.
	# ####


	rp = get_relative_pose(cube.pose, robot.pose)
	x, y, _ = rp.position.x_y_z
	cube_angle = rp.rotation.angle_z.radians

	# gets cozmo ~ into lower left corner of cube
	fix_orientation(robot, x, y, cube_angle)

	# cube relative to robot != robot relative to cube
	# moves robot into desired_pose_relative_to_cube
	# dock_with_cube(robot, cube)

	perform_manuever(robot, cube)


def perform_manuever(robot, cube):
	""" attempts to lift up cube and carry around"""
	# orientate
	orad = cube.pose.rotation.angle_z.degrees
	rrad = robot.pose.rotation.angle_z.degrees
	x, y, _ = robot_relative_cube(robot, cube, 0, 100)
	angle_z = orad - rrad
	cozmo_go_to_pose(robot, x , y , angle_z - 90)


	# attempt to line up with cube
	x, y, _ = robot_relative_cube(robot, cube, 0, -30)
	orad = cube.pose.rotation.angle_z.degrees
	rrad = robot.pose.rotation.angle_z.degrees
	angle_z = orad - rrad
	cozmo_go_to_pose(robot, x , y , angle_z - 90)

	# lift and carry
	robot.move_lift(5)
	cozmo_drive_straight(robot, 20, 10)
	robot.move_lift(-5)
	print("all done")

def dock_with_cube(robot, cube):
	""" cubes axis are same as cozmo - straight ahead is positive x, left is positive y
	    90 degree's relative to cube == cozmo facng + x-axis"""

	orad = cube.pose.rotation.angle_z.radians
	rrad = robot.pose.rotation.angle_z.radians
	angle_z = (orad - rrad)
	x, y, _ = robot_relative_cube(robot, cube, 0, 100)
	cozmo_go_to_pose(robot, x , y , (math.degrees(angle_z)))
	print("robot docking at: %s" % robot.pose)


def robot_relative_cube(robot, cube, dx, dy):
	""" used to calculate robot's position in cube's basis"""
	object_pose = cube.pose
	reference_frame_pose = robot.pose

	ox, oy, oz = object_pose.position.x_y_z
	orad = object_pose.rotation.angle_z.radians

	rx, ry, rz = reference_frame_pose.position.x_y_z
	rrad = reference_frame_pose.rotation.angle_z.radians

	# rotational/translational matrix of cozmo's coord system
	rc = [cos(rrad), -sin(rrad), rx, sin(rrad), cos(rrad), ry, 0, 0, 1]
	r_matrix = np.array(rc).reshape(3,3)
	r_matrix_inv = np.linalg.inv(r_matrix)

	# rotational/translational matrix of cube's coord system
	cc = [cos(orad), -sin(orad), ox, sin(orad), cos(orad), oy, 0, 0, 1]
	c_matrix = np.array(cc).reshape(3,3)

	# desired posed
	ac = np.array([dx , dy, 1])

	#nx, ny, _ = r_matrix_inv.dot(ac)
	return r_matrix_inv.dot(c_matrix).dot(ac)

def fix_orientation(robot, x, y, cube_angle):
	""" Moves cozmo to ~ bottom left corner of cube's reference frame"""
	if abs(cube_angle) < np.pi/4:
		# bottom left facing 'north'
		cozmo_go_to_pose(robot, x - 100, y + 100, 0)
	else:
		# top right facing 'south'
		cozmo_go_to_pose(robot, x + 100, y - 100, 180)



# Wrappers for existing Cozmo navigation functions
def cozmo_go_to_pose(robot, x, y, angle_z):
	"""Moves the robot to a pose relative to its current pose.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		x,y -- Desired position of the robot in millimeters
		angle_z -- Desired rotation of the robot around the vertical axis in degrees
	"""
	robot.go_to_pose(Pose(x, y, 0, angle_z=degrees(angle_z)), relative_to_robot=True).wait_for_completed()


def cozmo_drive_straight(robot, dist, speed):
	"""Drives the robot straight.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		dist -- Desired distance of the movement in millimeters
		speed -- Desired speed of the movement in millimeters per second
	"""
	robot.drive_straight(distance_mm(dist), speed_mmps(speed)).wait_for_completed()

def cozmo_turn_in_place(robot, angle, speed):
	"""Rotates the robot in place.
		Arguments:
		robot -- the Cozmo robot instance passed to the function
		angle -- Desired distance of the movement in degrees
		speed -- Desired speed of the movement in degrees per second
	"""
	robot.turn_in_place(degrees(angle), speed=degrees(speed)).wait_for_completed()


if __name__ == '__main__':

	## For step 2
	# cozmo.run_program(find_relative_cube_pose)

	## For step 3
	cozmo.run_program(move_relative_to_cube)


