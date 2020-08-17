from tkinter import *
from tkinter import ttk
import mysql.connector



BUTTON_WIDTH = 50
BUTTON_HEIGHT = 5
ENTRY_WIDTH = 50

def tutor_students(*args):
    try:
        print("tutoring")
    except ValueError:
        pass

def take_attendance(*args):
    try:
        # v = float(student.get())
        # meters.set(420*v)

        # check database

        # wait for

        print("Attendance Taken")
    except ValueError:
        pass

root = Tk()
root.title("CozmoTA")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

student = StringVar()
meters = StringVar()

student_lookup = ttk.Entry(mainframe, width=ENTRY_WIDTH, textvariable=student)
student_lookup.grid(column=2, row=2, sticky=(W, E))

ttk.Label(mainframe, textvariable=meters).grid(column=2, row=1, sticky=(W, E))
Button(mainframe, bg="#43b3d9", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text="Take Attendance", command=take_attendance).grid(column=1, row=1, sticky=W)
Button(mainframe, bg="#e0e046", width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text="Tutoring Session", command=tutor_students).grid(column=1, row=2, sticky=W)
ttk.Label(mainframe, text="student").grid(column=2, row=3, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

student_lookup.focus()
root.bind('<Return>', take_attendance)

root.mainloop()


