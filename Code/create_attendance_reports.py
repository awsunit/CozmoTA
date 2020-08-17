# File to setup attendance files for use with CozmoTA

# ugly but don't be scared, it's just a script

import os
import json
import xlwt
from xlwt import Workbook

'''
    Another script
    initializes excel spread sheets for use with attendance
'''

# excel sheet placement
LABEL_STUDENT_ROW = 6
LABEL_STUDENT_COL = 0
LABEL_STUDENTNAME_COL = LABEL_STUDENT_COL
LABEL_STUDENTNAME_ROW = LABEL_STUDENT_ROW + 2
LABEL_COURSE_ROW = 1
LABEL_COURSE_COL = 0
LABEL_DATE_ROW = 4
LABEL_DATE_COL = 1

# fills out file with absent for default value
# row_end is INCLUSIVE
def fill_out(ex_file, row_start, row_end):
    for day in range(32):
        for row in range(row_start, row_end):
            ex_file.write(row, day + LABEL_COURSE_COL + 2, "ABSENT")



# configures each attendance report file -> these are excel files
def setup_excel_file(wb, fname):
    ef = wb.add_sheet(fname, cell_overwrite_ok=True)

    # style it up
    ef.col(LABEL_STUDENT_COL).width = 256 * 40 # 40 chars wide
    ef.col(LABEL_DATE_COL).width = 256 * 13
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    style.font = font

    date_row = ef.row(LABEL_DATE_ROW)

    # setup file labels
    ef.write(LABEL_COURSE_ROW, LABEL_COURSE_COL, "Course:", style=style)
    ef.write(LABEL_DATE_ROW, LABEL_DATE_COL, "Date:", style=style)
    ef.write(LABEL_STUDENT_ROW, LABEL_STUDENT_COL, "Students", style=style)

    # assign value to Course
    ef.write(LABEL_COURSE_ROW + 1, LABEL_COURSE_COL, fname)

    return ef


path = os.path.join(os.getcwd(), "../Class_Rosters")


for f in os.listdir(path):
    wb = Workbook()
    print("creating attendance reports, loading file: ", f)
    row_for_student_name = LABEL_STUDENTNAME_ROW
    cn, _ = f.split(".")
    print("cn: ", cn)
    excel_file = setup_excel_file(wb, cn)
    fpath = os.path.join(path, f)

    # makes alphabetical ordering ez
    student_body = []
    with open(fpath, 'r') as course_list:
        data = json.load(course_list)
        for student in data:
            print("student: ", student)
            student_body.append(student["name"])

        student_body.sort()
        # write data
        for s in student_body:
            excel_file.write(row_for_student_name, LABEL_STUDENT_COL, s)
            # update location of next write
            row_for_student_name += 1

        # inclusive
        fill_out(excel_file, LABEL_STUDENTNAME_ROW, row_for_student_name)

        # save file
        cn = cn + ".xls"
        wb.save("../Teacher_Resources/{0}".format(cn))
