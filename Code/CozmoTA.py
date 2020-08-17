import cozmo
import json
import os
import sys
from GUI import GUI
from Robot import RobotTA
import mysql.connector as mysql
import flash_card_pickup as fcp
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes, LightCube
from cozmo.util import degrees, Angle, Pose, distance_mm, speed_mmps
import threading


db = None
gui = None
cozmo_ta = None

''' 
    need something in the main thread for GUI to close nicely
     kinda silly but whatcha gunna do
     UPDATE - DOES NOT FIX hmmm
'''
class HomeBase:

    def __init__(self, gui, robot):
        self.gui = gui
        self.robot = robot
        self.num_cards = 0

    def shut_gui_down(self):
        self.gui.root.destroy()



'''
    Gets the connection to the database open for use
    with attendance
'''
def database_connect():

    global db
    path = os.path.join(os.getcwd(), "../Resources/db_credentials.json")
    with open(path, 'r') as f:
        credentials = json.load(f)
        db = mysql.connect(
            host=credentials["host"],
            user=credentials["user"],
            passwd=credentials["passwd"],
            db=credentials["db"]
        )
    print("CozmoTA connected to database: ", db)


# def cozmoTA(robot):
def cozmoTA(robot: cozmo.robot.Robot):


    global db

    # 5/24
    global gui

    # holds student records
    database_connect()

    # encapsulate OG Cozmo
    cozmo_ta = RobotTA(robot, db)

    # initiates UI
    gui = GUI(cozmo_ta)
    # cozmo_ta.gui = gui

    # hb = HomeBase(gui, robot)
    # gui.main_object = hb

    gui.start()
    # if we are here, gui has shut down


cozmo.run_program(cozmoTA, use_viewer=True)

# if __name__ == "__main__":
#     cozmoTA(None)