# coding: utf-8
from __future__ import division

import os
import re
import sys
import pyaudio
import websocket
import threading
import time
import wave


from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from six.moves import queue
from datetime import datetime
# websocketのやり取りのために用いられるモジュール
try:
    import thread
except ImportError:
    import _thread as thread


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
CHANNEL = 1


# 認識結果保存ファイルの場所を指定
rectext = '/Users/erika/aftertaste/data/test.txt'

# 認識結果を保存するリスト
to_pcg = []
stock = []
charBuff = queue.Queue()

can_speechrec_flag = False
message_from_processing = ""
icon_name = ""


def getNowtime():
    nowtime = datetime.now().strftime('%s')
    return nowtime


# 認識結果を書き込む指示
def writeText():
    global to_pcg
    global icon_name

    writing = '，'.join(to_pcg)
    if os.path.isfile(rectext):
        with open(rectext, mode='a') as outfile:
            outfile.write(writing)

    else:
        with open(rectext, mode='w') as outfile:
            outfile.write(writing)


def recordSound(ch, rate, sound):
    file_name = getNowtime() + ".wav"
    with wave.open(file_name, 'wb') as wav:
        wav.setnchannels(ch)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b''.join(sound))


def divideText(showChar):
    for char in showChar:
        charBuff.put(char)


def sendCharacter():
    while not charBuff.empty():
        c = charBuff.get()
        print(c)
        ws.send(c)
        time.sleep(8)


def schedule(interval, wait=True):
    base_time = time.time()
    next_time = 0
    while True:
        t = threading.Thread(target=sendCharacter)
        t.start()
        if wait:
            t.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)
        if charBuff.empty() is True:
            break


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        print("exit")
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        global message_from_processing
        global can_speechrec_flag
        global stock
        while not self.closed:
            if message_from_processing == "end":
                can_speechrec_flag = False
                print("end")
                # self.close = True
                break
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            stock.append(chunk)
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    stock.append(chunk)
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    num_chars_printed = 0

    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

            recognizedText = transcript + overwrite_chars

            # 最終認識結果をリストに追加
            to_pcg.append(recognizedText)

            divideText(recognizedText)

            schedule(0.25, False)

            num_chars_printed = 0


def speechRecognition():
    print("hello")
    language_code = 'ja-JP'  # a BCP-47 language tag
    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=False,
        single_utterance=False)

    with MicrophoneStream(RATE, CHUNK) as stream:

        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


def main():
    global can_speechrec_flag
    global message_from_processing
    global to_pcg
    global stock
    global icon_name

    while True:
        if can_speechrec_flag is True:
            speechRecognition()
            recordSound(CHANNEL, RATE, stock)
        else:
            if message_from_processing == "connected":
                to_pcg = []
                stock = []
                can_speechrec_flag = True
            elif message_from_processing == "done":
                print("write")
                writeText()
                message_from_processing = ""
            elif message_from_processing == "":
                can_speechrec_flag = False
            else:
                icon_name = message_from_processing


def on_message(ws, message):
    global message_from_processing
    message_from_processing = message

# websocketの通信がエラー状態の時


def on_error(ws, error):
    print(error)

# websocketの通信が閉じた時


def on_close(ws):
    print("### closed ###")

# websocketの通信中の時


def on_open(ws):

    def run(*args):
        main()
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == '__main__':
    # speechRecognition()

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:5000",
                                on_error=on_error,
                                on_close=on_close,
                                on_message=on_message)

    ws.on_open = on_open

    ws.run_forever()
    # execution()
