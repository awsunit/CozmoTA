import os
import json
import mysql.connector as mysql

'''
    Don't be scared, it's just a script
    used to initialize database, and create tables for each class
    meant to be run only once
'''


# get into resources directory to access database credentials
oldpath = os.getcwd()
# get our course file open here
course_data= {}
path = os.path.join(os.getcwd(), "../Resources/courses.json")
print("path: ", path)
with open(path, 'r') as course_file:
    course_data = json.load(course_file)
course_list = course_data['courses']

# get all our database info
host = None
user = None
passwd = None
with open(os.path.join(os.getcwd(), "db_credentials.json"), 'r') as f:
    credentials = json.load(f)
    host = credentials["host"]
    user = credentials["user"]
    passwd = credentials["passwd"]

# connect/create DB
DATABASE_NAME = "Classes"
db = mysql.connect(
    host=host,
    user=user,
    passwd=passwd
)
cursor = db.cursor()
statement = "CREATE DATABASE IF NOT EXISTS " + DATABASE_NAME
cursor.execute(statement)

# connect to specific database to make tables for each class
db = mysql.connect(
    host=host,
    user=user,
    passwd=passwd,
    db=DATABASE_NAME
)
cursor = db.cursor()

# get into Class_Rosters directory to make table
os.chdir(os.path.join(os.getcwd(), "../Class_Rosters"))

# Loop inv:
#    for every class file, f, seen:
#        a table, t, with class name has been created and added to db
#        for every student object in f:
#            a table entry has been added to t
for course in os.listdir(os.getcwd()):

    course_name, _ = course.split(".")
    print("creating table for course: ", course_name)

    if course_name not in course_list:
        # create table for class
        statement = "CREATE TABLE IF NOT EXISTS {0} (name VARCHAR(255), dob VARCHAR(10), grade VARCHAR(1))".format(course_name)
        # print(statement)
        cursor.execute(statement)

        # for json file containing courses
        course_list.append(course_name)

        # create entries from objects in file
        with open(course, "r") as f:
            data = json.load(f)
            for student in data:
                print("Adding to table: ", student)
                statement = "INSERT INTO {0} (name, dob, grade) VALUES (%s, %s, %s)".format(course_name)
                values = (student["name"], student["DOB"], student["grade"])
                # print(statement)
                cursor.execute(statement, values)
        db.commit()

# get to resources
path = os.path.join(os.getcwd(), "../Resources/courses.json")
# write courses file
with open(path, 'w+') as course_file:
    json.dump(course_data, course_file, indent=4)

# change back to initial directory
os.chdir(oldpath)

