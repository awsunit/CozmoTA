from tkinter import *
from tkinter import ttk
import os
import json
import threading
import time
import cozmo

'''
    The object representing our tkinter GUI
'''
class GUI():

    # feel free to mess around with these
    BUTTON_WIDTH = 50
    BUTTON_HEIGHT = 5
    BUTTON_SUBMIT_WIDTH = 25
    BUTTON_SUBMIT_HEIGHT = 3
    ENTRY_WIDTH = 50
    BUTTON_ATTENDANCE_STR = "Take Attendance"
    BUTTON_ATTENDANCE_ROW = 1
    BUTTON_ATTENDANCE_COL = 1
    BUTTON_TUTOR_STR = "Tutor Session"
    BUTTON_TUTOR_ROW = 2
    BUTTON_TUTOR_COL = 1
    BUTTON_EXIT_ROW = 3
    BUTTON_EXIT_COL = 1
    RB_DEFAULT = "unset"
    LABEL_FLASH_NEW_ROW = 1
    LABEL_FLASH_NEW_COL = 3



    '''
        This method is nasty, but separating it into methods just moved the peas somewhere else
    '''
    def __init__(self, robot):

        # parent window
        root = Tk()
        root.title("CozmoTA")

        # CHANGE ME -> close GUI when threading figured out
        root.bind('<Return>', self.take_attendance)

        mainframe = Frame(root, bg='#17120b')

        # add flash card window
        mf2 = Frame(root, bg='#2a76b8')
        mf2.grid(column=1, row=0, sticky=(N,W,E,S))

        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)


        # these strings are used to change button's displayed text
        button_attendance_str = StringVar(mainframe)
        button_attendance_str.set(GUI.BUTTON_ATTENDANCE_STR)
        button_tutor_str = StringVar(mainframe)
        button_tutor_str.set(GUI.BUTTON_TUTOR_STR)
        button_strings = {"attendance":button_attendance_str, "tutor":button_tutor_str }

        # buttons to issue commands
        self.button_attendance = Button(mainframe, bg="#43b3d9", width=GUI.BUTTON_WIDTH, height=GUI.BUTTON_HEIGHT, textvariable=button_strings["attendance"], command=self.take_attendance)
        self.button_attendance.grid(column=GUI.BUTTON_ATTENDANCE_COL, row=GUI.BUTTON_ATTENDANCE_ROW, sticky=W)
        self.button_tutor = Button(mainframe, bg="#e0e046", width=GUI.BUTTON_WIDTH, height=GUI.BUTTON_HEIGHT, textvariable=button_strings["tutor"], command=self.tutor_students)
        self.button_tutor.grid(column=GUI.BUTTON_TUTOR_COL, row=GUI.BUTTON_TUTOR_ROW, sticky=W)
        self.button_exit = Button(mainframe, bg="#fc3003", width=GUI.BUTTON_WIDTH, height=GUI.BUTTON_HEIGHT, text="EXIT", command=self.quit)
        self.button_exit.grid(column=GUI.BUTTON_EXIT_COL, row=GUI.BUTTON_EXIT_ROW, sticky=W)

        # radio buttons to select class
        self.rb_val = StringVar(root)
        self.rb_val.set(GUI.RB_DEFAULT)
        self.setup_radiobuttons(mainframe)

        # buttons to add a flash card
        self.label_flash_new = Label(mf2, text="Create New Flashcard")
        self.label_flash_new.grid(row=GUI.LABEL_FLASH_NEW_ROW, column=GUI.LABEL_FLASH_NEW_COL + 1, sticky=E)
        # question
        self.label_flash_question = Label(mf2, text="Question")
        self.label_flash_question.grid(row=GUI.LABEL_FLASH_NEW_ROW + 1, column=GUI.LABEL_FLASH_NEW_COL, sticky=E)
        self.entry_question = Entry(mf2, width=GUI.BUTTON_SUBMIT_WIDTH)
        self.entry_question.grid(row=GUI.LABEL_FLASH_NEW_ROW + 1, column=GUI.LABEL_FLASH_NEW_COL + 1, sticky=E)
        # answer
        self.label_flash_answer = Label(mf2, text="Answer")
        self.label_flash_answer.grid(row=GUI.LABEL_FLASH_NEW_ROW + 2, column=GUI.LABEL_FLASH_NEW_COL, sticky=E)
        self.entry_answer = Entry(mf2, width=GUI.BUTTON_SUBMIT_WIDTH)
        self.entry_answer.grid(row=GUI.LABEL_FLASH_NEW_ROW + 2, column=GUI.LABEL_FLASH_NEW_COL + 1, sticky=E)
        # # identifier
        self.label_flash_id = Label(mf2, text="Object ID")
        self.label_flash_id.grid(row=GUI.LABEL_FLASH_NEW_ROW + 3, column=GUI.LABEL_FLASH_NEW_COL, sticky=E)
        self.entry_id = Entry(mf2, width=GUI.BUTTON_SUBMIT_WIDTH)
        self.entry_id.grid(row=GUI.LABEL_FLASH_NEW_ROW + 3, column=GUI.LABEL_FLASH_NEW_COL + 1, sticky=E)
        # button to seal the deal
        self.button_addcard = Button(mf2, bg='#32a852', width=GUI.BUTTON_SUBMIT_WIDTH - 5, height=GUI.BUTTON_SUBMIT_HEIGHT, text="Add FlashCard", command=self.add_flashcard)
        self.button_addcard.grid(column=GUI.LABEL_FLASH_NEW_COL + 1, row=GUI.LABEL_FLASH_NEW_ROW + 4, sticky=W)

        # style
        for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
        for child in mf2.winfo_children(): child.grid_configure(padx=5, pady=5)

        # class members
        self.root = root
        self.mainframe = mainframe
        self.robot = robot
        self.button_strings = button_strings
        self.course = None
        self.RUNNING_PROGRAM = False

        print("GUI done initializing")


    '''
        displays GUI
    '''
    def start(self):
        self.root.mainloop()

    '''
        Called when quit is pressed -> currently being naughty
    '''
    def quit(self):
        # anything else to do?
        # self.root.destroy()
        if self.RUNNING_PROGRAM:
            print("currently running a program")
            return

        print("exit via the window X, this currently throws an exception")
        self.main_object.shut_gui_down()
        return

    '''
        Called when add flash card button pressed
    '''
    def add_flashcard(self):
        course_data = {}
        path = os.path.join(os.getcwd(), "../Flashcards/Lesson1.json")
        print("path: ", path)
        with open(path, 'r') as course_file:
            course_data = json.load(course_file)
        course_list = course_data['Flashcards']

        # # append fields
        question = self.entry_question.get()
        answer = self.entry_answer.get()
        id = self.entry_id.get()
        print(question, answer, id)

        if question == "" or answer == "" or id == "":
            self.robot.robot.say_text("Please enter all fields").wait_for_completed()
            return

        card = {"cardID":id, "questions":[question], "answers":[answer]}
        course_list.append(card)

        with open(path, 'w+') as course_file:
            json.dump(course_data, course_file, indent=4)

        print("added card")

    '''
        Tutor button pressed
        currently doesn't require a specific class
    '''
    def tutor_students(self, *args):
        try:

            if self.RUNNING_PROGRAM:
                print("currently running a program")
                return

            self.RUNNING_PROGRAM = True
            self.update_execution_file("running", "true")

            # reassign button's text and command
            self.change_button("tutor", "Stop Tutoring", self.button_tutor, self.stop_tutor_students)

            self.start_CozmoTA_program(self.robot.tutor)

        except ValueError:
            pass


    '''
        Attendance button pressed
    '''
    def take_attendance(self, *args):
        try:
            if self.RUNNING_PROGRAM:
                print("currently running a program")
                return

            if not self.inputs_ok():
                # put in thread or is glitchy UI a good visual indicator too?
                self.robot.robot.say_text("Please select a class").wait_for_completed()
                return

            print("GUI starting attendance process ")
            self.RUNNING_PROGRAM = True
            self.robot.course = self.rb_val.get()

            # flag used for stopping CozmoTA
            self.update_execution_file("running", "true")

            # reassign the button's text and command
            self.change_button("attendance", "Stop Taking Attendance", self.button_attendance, self.stop_attendance)

            self.start_CozmoTA_program(self.robot.take_attendance)

        except ValueError:
            pass

    '''
        Gets a thread running the specified program (keeps GUI stable)
    '''
    def start_CozmoTA_program(self, program):
        t = threading.Thread(target=program)
        t.start()

    '''
        called when the currently running program is halted by user
    '''
    def stop_running_CozmoTA(self, index, default_text, button, command):

        self.update_execution_file("running", "false")

        # revert to OG text and command
        self.button_strings[index].set(default_text)
        button.configure(textvariable=self.button_strings[index], command=command)

        # give time for file writes to succeed
        self.root.config(cursor="wait")
        self.root.update()
        time.sleep(5)
        self.root.config(cursor="")

        self.RUNNING_PROGRAM = False
        print("done running the program :", index)


    '''
        The following are methods used when a teacher wants to stop the running program
        Initiated by clicking the button which originally initialized program
    '''
    def stop_tutor_students(self):
        # reset student answer and remove additional input box
        self.update_execution_file("student_answer", "")
        # self.mfa.grid_forget()
        self.stop_running_CozmoTA("tutor", GUI.BUTTON_TUTOR_STR, self.button_tutor, self.tutor_students)

    def stop_attendance(self):
        self.stop_running_CozmoTA("attendance", GUI.BUTTON_ATTENDANCE_STR, self.button_attendance, self.take_attendance)


    '''
        updates a flag for our thread
        used because Tkinter is terrible w/ threads but needs them for stability
        could also use a bounded buffer, meh
    '''
    def update_execution_file(self, field, value):

        path = os.path.join(os.getcwd(), "../Resources/execution_details.json")

        data= {}
        with open(path, 'r') as f:
            data = json.load(f)
        print("cur running: ", data["running"])
        data[field] = value

        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

        # print("updated execution file")

    '''
        sets up the buttons used for selecting classes
    '''
    def setup_radiobuttons(self, mainframe):

        path = os.path.join(os.getcwd(), "../Resources/courses.json")
        course_data = {}
        # get the classes from json file
        with open(path, 'r') as cf:
            course_data = json.load(cf)
        course_list = course_data["courses"]

        v = 1
        for course in course_list:
            Radiobutton(mainframe, text=course, variable=self.rb_val, value=course).grid(column=2, row=v, sticky=W)
            v += 1

    '''
        changes a button's text and the command associated with it
    '''
    def change_button(self, button_strings_i, button_text, button, new_command):
        self.button_strings[button_strings_i].set(button_text)
        button.configure(textvariable=self.button_strings[button_strings_i], command=new_command)

    '''
        ensures that teacher has selected a class for the program 
    '''
    def inputs_ok(self):
        return self.rb_val.get() != GUI.RB_DEFAULT

    '''
        Currently unused?
    '''
    def set_course(self):
        self.course = self.rb_val.get()

    def dir_up(self, folder):
        os.chdir("..")
        os.chdir(os.path.join(os.getcwd(), folder))

    '''
        Depreciated 
    '''
    def submit_answer(self):
        answer = str(self.entry_student_answer.get())
        if answer == "":
            self.robot.robot.say_text("Please insert an answer")
            return
        self.update_execution_file("student_answer", answer)


    '''
        Begin Properties
    '''
    @property
    def robot(self):
        return self._robot

    @robot.setter
    def robot(self, robot):
        print("set robot")
        self._robot = robot

    @property
    def main_object(self):
        return self._main_object

    @main_object.setter
    def main_object(self, main_o):
        print("changing baby")
        self._main_object = main_o
