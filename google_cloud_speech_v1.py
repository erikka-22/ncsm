from __future__ import division

import re
import sys
import pyaudio
import json
import websocket

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

# ファイル名に用いる
nowtime = datetime.now().strftime('%s')

# 認識結果保存ファイルの場所を指定
rectxt = '/Users/erika/Research_Processing/ncsm-processing/keyboard/data/websocket.json'

# 最終認識結果(is_final:true)を保存するリスト
to_pcg = []

# 認識結果を保存するファイルを新規作成


def make_txtfile():
    with open(rectxt, mode='w') as outfile:
        json.dump(to_pcg, outfile)

# 認識結果を書き込む指示


def write_txt():
    with open(rectxt, mode='w') as outfile:
        json.dump(to_pcg, outfile, ensure_ascii=False)


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
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
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
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    """Iterates through server responses and prints them.
    The responses passed is a generator that will block until a response
    is provided by the server.
    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.
    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """

    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        print(transcript)

        # 最終認識結果をリストに追加
        to_pcg.append(transcript)

        # 認識結果をwebsocketサーバに送信
        # ws.send(transcript)

        # Exit recognition if any of the transcribed phrases could be
        # one of our keywords.
        if re.search(r'\b(exit|quit)\b', transcript, re.I):
            print('Exiting..')
            break


def execution():
    print("hello")
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'ja-JP'  # a BCP-47 language tag
    make_txtfile()

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=False)
    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)

# websocketの通信がエラー状態の時


def on_error(ws, error):
    print(error)

# websocketの通信が閉じた時


def on_close(ws):
    print("### closed ###")

# websocketの通信中の時


def on_open(ws):
    def run(*args):
        execution()()
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


execution()

if __name__ == '__main__':

    # websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("ws://127.0.0.1:5000",
    #                             on_error=on_error,
    #                             on_close=on_close)
    # ws.on_open = on_open

    # ws.run_forever()
    execution()
