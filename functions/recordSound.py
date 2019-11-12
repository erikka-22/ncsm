import wave
from datetime import datetime


def getNowtime():
    nowtime = datetime.now().strftime('%s')
    return nowtime


def recordSound(ch, rate, sound):
    file_name = getNowtime() + ".wav"
    with wave.open(file_name, 'wb') as wav:
        wav.setnchannels(ch)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b''.join(sound))
