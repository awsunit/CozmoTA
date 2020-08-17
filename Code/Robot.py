# defines a Robot class for use in GUI call backs
# encapsulates Cozmo
import GUI
import random
import flash_card_pickup
import asyncio
import cozmo
import os
import json
from xlrd import open_workbook
from xlutils.copy import copy
from datetime import date



'''
    kinda ugly but we need them
'''
LABEL_STUDENT_ROW = 6
LABEL_STUDENT_COL = 0
LABEL_STUDENTNAME_COL = LABEL_STUDENT_COL
LABEL_STUDENTNAME_ROW = LABEL_STUDENT_ROW + 2
LABEL_COURSE_ROW = 1
LABEL_COURSE_COL = 0
LABEL_DATE_ROW = 4
LABEL_DATE_COL = 1

'''
    Our encapsulating class
    Holds references to cozmo and GUI for callbacks
'''
class RobotTA():

    def __init__(self, robot, db):

        # Cozmo.Robot instance
        self.robot = robot
        # opened database to query -> !close
        self.db = db
        # callback
        self.gui = None
        self.course = None
        self.RUNNING_PROGRAM = False


    '''
        Creates a Tutor object and gets the ball rolling
    '''
    def tutor(self):
        print("Robot tutoring")
        program = flash_card_pickup.Tutor(self)
        program.start()

    '''
        Uses local methods to run attendance program
        could be busted out to another file
    '''
    def take_attendance(self):
        print("CozmoTA taking attendance")

        # get's our excel sheet writer and reader ready
        fname = "../Teacher_Resources/{0}.xls".format(self.course)
        path = os.path.join(os.getcwd(), fname)

        # used to read and write to excel file
        rb = open_workbook(path)
        r_sheet = rb.sheet_by_index(0) # read copy
        wb = copy(rb) # cant read, only write
        w_sheet = wb.get_sheet(0)
        date_col = self.set_attendence_date(r_sheet,  w_sheet)

        self.await_students(r_sheet, w_sheet, date_col, wb, path)

    '''
        Waits for faces to appear until told to quit
        Logs attending students, alerts teacher to intruders
    '''
    def await_students(self, r_sheet, w_sheet, date_col, wb, path):
        # most of the following is just a rip from Cozmo src, blessings
        # Move lift down and tilt the head up
        self.robot.move_lift(-3)
        self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

        face_to_follow = None
        cursor = self.db.cursor()

        while self.keep_running():

            turn_action = None
            if face_to_follow:
                print("hi")

            if not (face_to_follow and face_to_follow.is_visible):
                # find a visible face, timeout if nothing found after a short while
                try:
                    face_to_follow = self.robot.world.wait_for_observed_face(timeout=5)

                    # get name and query database
                    student_name = str(face_to_follow.name)
                    print("Cozmo TA seen: ", student_name)
                    statement = "SELECT name FROM {0} WHERE name = \"{1}\"".format(self.course, student_name)
                    cursor.execute(statement)
                    row = cursor.fetchone()

                    if row is None:
                        self.robot.say_text("My apologies, but I'm not sure you are in this class {0};".format(student_name)).wait_for_completed()
                    else:
                        self.robot.say_text("Hello {0}".format(student_name)).wait_for_completed()
                        # grab a list of animation triggers
                        all_animation_triggers = self.robot.anim_triggers

                        # randomly shuffle the animations
                        random.shuffle(all_animation_triggers)
                        chosen = all_animation_triggers[0]
                        self.robot.play_anim_trigger(chosen).wait_for_completed()

                        self.mark_student_present(r_sheet, w_sheet, student_name, date_col)
                        self.robot.move_lift(-3)
                        self.robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

                    face_to_follow = None

                except asyncio.TimeoutError:
                    print("Didn't find a face")

        if turn_action:
            # Complete the turn action if one was in progress
            turn_action.wait_for_completed()

        # update excel
        wb.save(path)
        print("robot done taking attendance ")

    '''
        checks a variable inside a file -> a fix for multithreading object weirdness
    '''
    def keep_running(self):
        path = os.path.join(os.getcwd(), "../Resources/execution_details.json")
        with open(path, 'r') as f:
            data = json.load(f)
            if data["running"] == "false":
                return False
            else:
                return True

    '''
        updates the attendance file
    '''
    def mark_student_present(self, r_sheet, w_sheet, student_name, date_col):
        col = LABEL_STUDENTNAME_COL
        row = LABEL_STUDENTNAME_ROW

        while True:
            print("trying row, col: ({0}, {1})".format(row, col))
            data = r_sheet.cell(row, col).value
            if data.lower() == student_name.lower():
                w_sheet.write(row, date_col, "")
                break
            row += 1

        print("Marked {0} present".format(student_name))


    '''
        set the date, return the column of date for later use
    '''
    def set_attendence_date(self, r_sheet, w_sheet):
        today = date.today()
        # find empty date location
        col = LABEL_DATE_COL + 1
        row = LABEL_DATE_ROW

        for c in range(col - 1, 31 + col):
            data = str(r_sheet.cell(row, c,).value)
            if data == "":
                w_sheet.col(c).width = 256 * 13
                w_sheet.write(row, c, str(today.isoformat()))
                return c










