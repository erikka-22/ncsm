import google_cloud_speech_v1
import sys

print("waiting your imput")
enter = input()
if enter == "s":
    print("start")
    google_cloud_speech_v1.execution()
