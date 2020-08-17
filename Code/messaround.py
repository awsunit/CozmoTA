# import mysql.connector as mysql
import os
path = os.path.join(os.getcwd(), '../Resources/speech.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
import json
# import xlwt
import io
# from xlwt import Workbook
# from tkinter import *
# from PIL import ImageTk, Image
import GUI
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import sounddevice as sd
from scipy.io.wavfile import write
import pyaudio
import speech_recognition as sr
import subprocess
import shutil
import wave
import base64
import audio

initial_path = path = os.path.join(os.getcwd(), 'student_response.wav')
converted_path = os.path.join(os.getcwd(), 'student_response_1.raw')


def check_answer(answer, client):
    global converted_path, initial_path

    print("checking answer")
    # path = os.path.join(os.getcwd(), 'student_response.flac')

    encoding = enums.RecognitionConfig.AudioEncoding.FLAC
    config = {
        "encoding": encoding,
        "sample_rate_hertz": 16000,
        "language_code": "en-US",
    }
    # config = {
    #     # "enableAutomaticPunctuation": True,
    #     "encoding": "LINEAR16",
    #     "languageCode": "en-US",
    #     "model": "default"
    # }
    with io.open(initial_path, "rb") as audio_file:
        content = audio_file.read()
    audio = {"content": content}

    response = client.recognize(config, audio)
    for result in response.results:
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))


def get_answer():
    global initial_path
    # FORMAT = pyaudio.paInt16
    #
    # CHANNELS = 1
    # RATE = 44100
    # CHUNK = int(RATE / 10)
    # RECORD_SECONDS = 5
    #
    # audio = pyaudio.PyAudio()
    #
    # # start Recording
    # stream = audio.open(format=FORMAT, channels=CHANNELS,
    #                     rate=RATE, input=True,
    #                     frames_per_buffer=CHUNK)
    # print ("recording...")
    # frames = []
    #
    # for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    #     data = stream.read(CHUNK)
    #     frames.append(data)
    # print ("finished recording")
    #
    #
    # # stop Recording
    # stream.stop_stream()
    # stream.close()
    # audio.terminate()
    #
    #
    #
    # file = open(path, "wb")
    # file.write(b''.join(frames))
    # file.close()


    fs = 16000
    sec = 3
    print("start")
    answer = sd.rec(int(sec*fs), samplerate=fs, channels=1)
    sd.wait()
    # path = os.path.join(os.getcwd(), 'student_response.wav')
    write(initial_path, fs, answer)
    print("here")
    # path = 'student_response.flac'
    # new_path =  "student_response_1.flac"#os.path.join(os.getcwd(), 'student_response_1.wav')
    # command = ['sox', path, '-c', '1', new_path]
    # subprocess.Popen(command, shell=True)
    # print("done converting")


# get_answer()
# client = speech_v1.SpeechClient()
# check_answer(None, client)



# print("getting answer from student")
#
# path = os.path.join(os.getcwd(), "../Resources/execution_details.json")
# with open(path, 'r') as f:
#     print("trying get answer")
#     data = json.load(f)
#     answer = data["student_answer"]
#     print("our answer is: ", answer)







# w = wave.open("student_response_1.wav", "r")
# for i in range():
#     f = w.readframes(1)
#     print(f)

# IMPORTANT - PICTURE FOR COZMO TA ------------------------------------------------------------------------
# CANVAS_WIDTH = 300
# CANVAS_HEIGHT = 160
#
# root = Tk()
# canvas = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
# path = os.path.join(os.getcwd(), "../Resources/czbg.png")
# background = ImageTk.PhotoImage(Image.open(path))
#
# canvas.create_image(0, 0, anchor=NW, image=background)
# # canvas.pack()
#
# root.mainloop()


# gui = GUI.GUI(None)
# gui.start()

## practicing w/ excel
# wb = Workbook()
#
# sheet1 = wb.add_sheet('Firsties')
#
# sheet1.write(1, 0, 'TODDDDDD')
#
# wb.save('example.xls')
#
# print("done")



# path = os.path.join(os.getcwd(), "../Resources/courses.json")
# with open(path, 'r') as course_file:
#     course_data = json.load(course_file)
#     for c in course_data:
#         print(c, course_data[c])

# # get into resources directory to access database credentials
# oldpath = os.getcwd()
# os.chdir("..")
# os.chdir(os.path.join(os.getcwd(), "Resources"))
# # get our course file open here
# course_data= {}
# path = os.path.join(os.getcwd(), "courses.json")
# print("path: ", path)
# with open(path, 'r') as course_file:
#     course_data = json.load(course_file)
# course_list = course_data['courses']
#
# host = None
# user = None
# passwd = None
# with open(os.path.join(os.getcwd(), "db_credentials.json"), 'r') as f:
#     credentials = json.load(f)
#     host = credentials["host"]
#     user = credentials["user"]
#     passwd = credentials["passwd"]
# db = mysql.connect(
#     host=host,
#     user=user,
#     passwd=passwd,
#     db="Classes"
# )
#
# cursor = db.cursor()
#
# cursor.execute("SHOW TABLES")
#
# tables = cursor.fetchall()
#
# for t in tables:
#     print(t)
#
# statement = "SELECT * FROM first"#'SELECT * FROM {0};'.format('first')
#
# cursor.execute(statement)
#
# records = cursor.fetchall()
#
# for r in records:
#     print(r)