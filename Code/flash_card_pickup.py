#!/usr/bin/env python3
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes, LightCube
#from google.cloud import speech_v1
# from google.cloud.speech_v1 import enums
# from scipy.io.wavfile import write
# from math import sin, cos
from scipy.io.wavfile import write
import sounddevice as sd
# import numpy as np
import asyncio
import cozmo
import math
import time
import io
# import random
import json
import Robot
import os
from ibm_watson import SpeechToTextV1
# from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


faces = {}
flashCards = {}
CUID = {'Circles2':CustomObjectMarkers.Circles2,'Diamonds2':CustomObjectMarkers.Diamonds2}
CUOT = {'Circles2':CustomObjectTypes.CustomType00,'Diamonds2':CustomObjectTypes.CustomType01}
card_2_cube = {}
cubes = {}
cards_found = 0
cubes_found = 0
authenticator = IAMAuthenticator('48GS4zzm90tFOB7GnsVHfoWhBY7WHrIr0D8D9HjVDoGf')
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)
speech_to_text.set_service_url('https://api.us-south.speech-to-text.watson.cloud.ibm.com/')

'''
	Used to document where flashcards are in the environment
'''
def handle_object_appeared(evt, **kw):
	global flashCards, cards_found, cubes, cubes_found
	# This will be called whenever an EvtObjectAppeared is dispatched -
	# whenever an Object comes into view.
	if isinstance(evt.obj, CustomObject):
		cards_found += 1
		# flashCards[str(evt.obj.object_type)].pose = evt.obj.pose
		oldFc = flashCards[str(evt.obj.object_type)]
		fc = Flashcard(str(evt.obj.object_type), evt.obj.pose, oldFc.questions, oldFc.answers)
		flashCards[str(evt.obj.object_type)] = fc
		print("custom at: ",  evt.obj.pose)

	elif isinstance(evt.obj, LightCube):
		cubes_found += 1
		cubes[evt.obj] = evt.obj.pose

'''
    The main object which drives the tutoring program
'''
class Tutor:
	
	def __init__(self, cozmoTA):
		global CUID
		global CUOT
		global flashCards
		global card_2_cube
		global authenticator
		global speech_to_text
		# This will hold a map of ObjectType -> Pose, will be updated in handle_object_appeared
		self.flashCards = flashCards
		# This will hold a map of Face(faces that are seen) -> Pose, will be updated in handle_face_appeared
		self.faces = {}
		# Hardcoded Maps
		# Custom Object Identifier
		self.CUID = CUID
		# Custom Object Type
		self.CUOT = CUOT
		# tracks locations -> hack
		# self.card_to_cube = card_2_cube
		self.num_cards = 0

		# used for audio
		self.sample_rate = 44100
		self.response_file = 'student_response.wav'
		self.language = "en-US"

		self.cozmoTA = cozmoTA

	'''
		Discovers environment then begins Q&A session
	'''
	def start(self):
		global cubes
		# get our cards
		self.define_flash_cards()

		# event handler
		self.cozmoTA.robot.add_event_handler(cozmo.objects.EvtObjectAppeared, handle_object_appeared)

		# get positions of flashcards

		self.find_cards()


		# faces found in next stage dynamically

		# remove handler to prevent odd behavior
		self.cozmoTA.robot.remove_event_handler(cozmo.objects.EvtObjectAppeared, handle_object_appeared)

		# start the round robin process
		self.tutor()

	'''
		Goes through the flash cards and ask questions, evaluating responses
	'''
	def tutor(self):

		for fc in self.flashCards:
			# teacher able to stop program with button click
			if self.cozmoTA.keep_running():

				card = self.flashCards[fc]

				# allowing for the possibility that CozmoTA didn't see one of the cards
				if card.pose is not None:
					# want to get a face
					face = self.get_next_student()

					self.pickup_card(card)

					self.go_to_student(face)

					self.quiz(face, card)

					self.reset(face)

	'''
		CozmoTA spins around until all cards are found
	'''
	def find_cards(self):
		global cards_found

		while cards_found < self.num_cards:
			for card in self.flashCards.values():
				self.cozmoTA.robot.move_lift(-3)
				self.cozmoTA.robot.set_head_angle(degrees(5)).wait_for_completed()
				# card = self.flashCards[f]
				if card.pose is None:
					cozmo_turn_in_place(self.cozmoTA.robot, 360, 22)

	'''
		Depreciated 
	'''
	def find_cubes(self):
		global cubes_found
		while cubes_found < self.num_cards:
			cozmo_turn_in_place(self.cozmoTA.robot, 360, 22)

	'''
		Depreciated 
	'''
	def associate_cards(self):
		global cubes, card_2_cube
		# get all cubes
		for c in cubes:
			for flash in self.flashCards.values():
				if abs(flash.pose.position.x - cubes[c].position.x) < 50:
					card_2_cube[flash] = c



	'''
		Loops through the flashcard file
		converts json objects to python
	'''
	def define_flash_cards(self):
		#
		path = os.path.join(os.getcwd(), "../Flashcards/Lesson1.json")
		file = open(path, "r")
		jsonInput = file.read()
		jsonFc = json.loads(jsonInput)
		self.num_cards = len(jsonFc["Flashcards"])
		for card in jsonFc["Flashcards"]:
			# False for unique to allow tracking
			self.cozmoTA.robot.world.define_custom_cube(self.CUOT[card["cardId"]], self.CUID[card["cardId"]], 44.5, 25.4, 25.4, False)
			fc = Flashcard(card["cardId"], None, card["questions"], card["answers"])
			self.flashCards[str(self.CUOT[card["cardId"]])] = fc

		file.close()

	'''
		Attempts to grab flashcard
	'''
	def pickup_card(self, cube):
		print("attempting the pickup")
		# either of the following should have worked, threading issues maybe
		# self.cozmoTA.gui.call_back(cube)

		# Loaay's navigation works the best so going with that
		#self.cozmoTA.robot.go_to_object(cube, 100)
		#cube = self.cozmoTA.robot.world.wait_until_observe_num_objects(1, timeout=5)
		#cube = self.cozmoTA.robot.world.wait_until_observe_num_objects(1, timeout=5)
		cubePose = cube.pose
		desired_pose_relative_to_cube = Pose(100, 0, 0, angle_z=degrees(0))

		#Go to Flash Card
		final_pose = self.get_relative_pose(cubePose, self.cozmoTA.robot.pose)
		self.turn_towards(final_pose)
		newPose = self.cozmoTA.robot.world.wait_until_observe_num_objects(num=1)
		#self.cozmoTA.robot.go_to_pose(self.get_relative_pose(cube.pose, self.cozmoTA.robot.pose), relative_to_robot=True).wait_for_completed()
		#self.cozmoTA.robot.pickup_object(cube, use_pre_dock_pose=False, num_retries=3).wait_for_completed()
		final_pose = self.get_relative_pose(newPose[0].pose, self.cozmoTA.robot.pose)
		angl = final_pose.rotation.angle_z
		rel_pos = desired_pose_relative_to_cube.position
		x2 = (rel_pos.x * math.cos(angl.radians)) - (rel_pos.y * math.sin(angl.radians))
		y2 = (rel_pos.x * math.sin(angl.radians)) + (rel_pos.y * math.cos(angl.radians))
		cozmo_go_to_pose(self.cozmoTA.robot, final_pose.position.x + x2 , final_pose.position.y + y2, final_pose.rotation.angle_z.degrees - desired_pose_relative_to_cube.rotation.angle_z.degrees)

		
		#finalObject = self.cozmoTA.robot.world.wait_for_observed_light_cube(timeout=15)
		cozmo_drive_straight(self.cozmoTA.robot, 100, 45)

		self.cozmoTA.robot.move_lift(8)

	'''
		Turns CozmoTA back to student to ask question
	'''
	def turn_towards(self, pose):
		self.cozmoTA.robot.set_head_angle(degrees(5)).wait_for_completed()
		if pose.position.x > 0:
			if pose.position.y > 0:
				#Q2
				cozmo_turn_in_place(self.cozmoTA.robot, 45, 30)
			else:
				#Q4
				cozmo_turn_in_place(self.cozmoTA.robot, -45, 30)
		else:
			if pose.position.y > 0:
				#Q1
				cozmo_turn_in_place(self.cozmoTA.robot, 135, 30)
			else:
				#Q3
				cozmo_turn_in_place(self.cozmoTA.robot, -135, 30)


	'''
		used with navigation
	'''
	def get_relative_pose(self, object_pose, reference_frame_pose):

		new_ob = object_pose
		ref_pos = Pose(-1*reference_frame_pose.position.x,-1*reference_frame_pose.position.y,-1*reference_frame_pose.position.z,
					   angle_z = degrees(-1*reference_frame_pose.rotation.angle_z.degrees), origin_id = reference_frame_pose.origin_id)
		final_pose = ref_pos.define_pose_relative_this(new_ob)
		return final_pose

	'''
		self-explanatory
	'''
	def get_next_student(self):

		face = None
		robot = self.cozmoTA.robot
		# look_around = robot.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)

		while True:
			# find a visible face, timeout if nothing found after a short while
			robot.move_lift(-3)
			robot.set_head_angle(degrees(15)).wait_for_completed()

			if face:
				return face
			try:
				face = robot.world.wait_for_observed_face(timeout=5)
			# face = robot.world.wait_for_observed_face()#timeout=10)
				# if face:
				# 	# look_around.stop()
				# 	return face
				# else:
				# 	cozmo_turn_in_place(robot, 30, 30)
			except asyncio.TimeoutError:
				print("Didn't find a face - turning")
				cozmo_turn_in_place(robot, 30, 30)

	'''
		Asks student the card's question and evaluates response
	'''
	def quiz(self, face, card):
		name = face.name
		questions = card.questions

		# ask q
		self.cozmoTA.robot.say_text("Hey {0} {1}".format(name, questions[0])).wait_for_completed()

		answer = self.get_answer()

		if self.check_answer(card.answers, answer):
			self.cozmoTA.robot.say_text("You got that correct".format(face.name), in_parallel=True)
		else:
			self.cozmoTA.robot.say_text("I'm sorry but that is the wrong answer".format(face.name), in_parallel=True)


	'''
		Determines validity of supplied answer
	'''
	def check_answer(self, card_answers, student_answer):
		#print("checking answer")
		response = None
		path = os.path.join(os.getcwd(), self.response_file)
		with open(path, 'rb') as audio_file:
				speech_recognition_results = speech_to_text.recognize(
					audio=audio_file,
					content_type='audio/wav').get_result()
				print(json.dumps(speech_recognition_results, indent=2))
				response = speech_recognition_results
		
		std_answer = response["results"][0]["alternatives"][0]["transcript"]
		print(std_answer)
		for answer in card_answers:
			if answer in std_answer:
				return True
		return False

	'''
		Records student response
	'''
	def get_answer(self):
		print("getting answer from student")
		fs = self.sample_rate
		sec = 3
		print("start")
		answer = sd.rec(int(sec*fs), samplerate=fs, channels=2)
		sd.wait()
		print("end")
		path = os.path.join(os.getcwd(), self.response_file)
		write(path, fs, answer)


	def go_to_student(self, face):
		print("going to student")
		turn_action = self.cozmoTA.robot.turn_towards_face(face)
		turn_action.wait_for_completed()


	def reset(self, face):
		print("reseting to check for next student")
		time.sleep(8) # wait for speech to complete
		self.cozmoTA.robot.go_to_pose(Pose(0, 0, 0, angle_z=degrees(0)), relative_to_robot=False).wait_for_completed()
		turn_action = self.cozmoTA.robot.turn_towards_face(face)
		turn_action.wait_for_completed()
		cozmo_turn_in_place(self.cozmoTA.robot, 90, 45)



class Flashcard:
	def __init__(self, marker, pose, questions, answers, pickupable=None, id=None):
		self.marker = marker
		self.pose = pose
		self.questions = questions
		self.answers = answers
		######################
		self.pickupable = pickupable
		self.object_id = id


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

def r(robot: cozmo.robot.Robot):
	cozmoo = Robot.RobotTA(robot, None)
	tutor = Tutor(cozmoo)
	tutor.define_flash_cards()
	tutor.cozmoTA.robot.add_event_handler(cozmo.objects.EvtObjectAppeared, handle_object_appeared)

	while True:
		tutor.find_cards()

if __name__ == '__main__':
	# cozmo.run_program(move_relative_to_cube)
	cozmo.run_program(r)

