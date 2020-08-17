import json
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2
import sounddevice as sd
import os
from scipy.io.wavfile import write


initial_path = path = os.path.join(os.getcwd(), 'student_response.wav')
# fs = 16000
# sec = 3
# print("start")
# answer = sd.rec(int(sec*fs), samplerate=fs, channels=1)
# sd.wait()
# # path = os.path.join(os.getcwd(), 'student_response.wav')
# write(initial_path, fs, answer)
# print("here")

# authenticator = IAMAuthenticator('2oDMXDKDTGr38SNcHB-ZilDc0rrpDm__NMsxLNlEiIeA')
# assistant = AssistantV2(
#     version='2018-09-20',
#     authenticator=authenticator)
# assistant.set_service_url('https://api.us-east.assistant.watson.cloud.ibm.com')


# V1
authenticator = IAMAuthenticator('zTybBvhEOxkhRmE85X2oYHR87i1wtivd4w6E04x8mvCd')
# service = SpeechToTextV1(authenticator=authenticator)
# service.set_service_url('https://api.us-east.assistant.watson.cloud.ibm.com/')
# models = service.list_models().get_result()
# print(json.dumps(models, indent=4))


speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)

speech_to_text.set_service_url('https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/295d3092-600e-425c-b402-99bc73d14ef4')#/instances/61c4baa7-68a5-4047-bb6a-8e3d303ccdfd/v2/assistants/98fe4347-1086-4a56-9864-c987397216be/sessions')

with open(initial_path,
          'rb') as audio_file:
    print("here")
    speech_recognition_results = speech_to_text.recognize(
        audio=audio_file,
        content_type='audio/wav'
    ).get_result()


print(json.dumps(speech_recognition_results, indent=2))