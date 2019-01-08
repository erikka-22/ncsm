#-*- coding: utf-8 -*-
import pyaudio, time, audioop, math, sys, argparse, json
from gcloud.credentials import get_credentials
from google.cloud.speech.v1beta1 import cloud_speech_pb2
from google.rpc import code_pb2
from grpc.beta import implementations
from datetime import datetime
import pandas as pd
import numpy as np

class stdout:
    BOLD = "\033[1m"
    END = "\033[0m"
    CLEAR = "\033[2K"

def bold(string):
    return stdout.BOLD + string + stdout.END

def printr(string):
    sys.stdout.write("\r" + stdout.CLEAR)
    sys.stdout.write(string)
    sys.stdout.flush()

frames = []
silent_frames = []
is_recording = False
should_finish_stream = False

class Result:
    def __init__(self):
        self.transcription = ""
        self.confidence = ""
        self.is_final = False

recognition_result = Result()

#変換結果を文字列として持つ変数
str_transcription = ""

#認識結果保存ファイルの場所を指定

nowtime = datetime.now().strftime('%s')
rectxt = '/Users/iwasakierika/Documents/Processing/keyboard/data/rec_result'+nowtime+'.json'

#認識結果を保存するファイルを新規作成
def make_txtfile():
    global result
    result = []
    with open(rectxt, mode='w') as outfile:
        json.dump(result, outfile)

#認識結果を書き込む指示
def write_txt():
    with open(rectxt, mode='w') as outfile:
        json.dump(result, outfile, ensure_ascii=False)

def make_list():
    df = pd.read_csv('/Users/iwasakierika/Documents/Processing/keyboard_v2/data/question.csv', encoding='utf-8', header=None)
    list = df.values.tolist()
    # tag_list = flatten(tag_list)
    return list

def make_q_len():
    global list_length
    questions = make_list()
    list_length = (len(questions))

def make_nexttime():
    period = 5
    next_t = elapsed_time + period
    return next_t

def make_elapsed_time():
    global elapsed_time
    elapsed_time = time.time() - start()
    return elapsed_time

def start():
    start_time = time.time()
    return start_time
    
def make_numq(arg_nq):
    q_length = list_length
    if make_elapsed_time() > make_nexttime():
        arg_nq += 1
        if arg_nq > q_length + 1:
            arg_nq = 0
        make_nexttime()
    # print (elapsed_time)
    return arg_nq

# class Numres:
#     count = -1
    
#     def __init__(self):
#         Numres.count +=1        
    

def make_channel(host, port):
    ssl_channel = implementations.ssl_channel_credentials(None, None, None)
    creds = get_credentials().create_scoped(args.speech_scope)
    auth_header = ("authorization", "Bearer " + creds.get_access_token().access_token)
    auth_plugin = implementations.metadata_call_credentials(lambda _, func: func([auth_header], None), name="google_creds")
    composite_channel = implementations.composite_channel_credentials(ssl_channel, auth_plugin)
    return implementations.secure_channel(host, port, composite_channel)

def listen_loop(recognize_stream):
    global should_finish_stream
    global recognition_result

    for resp in recognize_stream:
        if resp.error.code != code_pb2.OK:
            raise RuntimeError(resp.error.message)

        for result in resp.results:
            for alt in result.alternatives:
                recognition_result.transcription = alt.transcript
                recognition_result.confidence = alt.confidence
                recognition_result.stability = result.stability
                printr(" ".join((alt.transcript, "    ", "stability: ", str(int(result.stability * 100)), "%")))

            if result.is_final:
                recognition_result.is_final = True
                should_finish_stream = True
                return

def request_stream():
    recognition_config = cloud_speech_pb2.RecognitionConfig(
        encoding=args.audio_encoding,
        sample_rate=args.sampling_rate,
        language_code=args.lang_code,
        max_alternatives=1,
    )
    streaming_config = cloud_speech_pb2.StreamingRecognitionConfig(
        config=recognition_config,
        interim_results=True,
        single_utterance=True
    )

    yield cloud_speech_pb2.StreamingRecognizeRequest(streaming_config=streaming_config)

    while True:
        time.sleep(args.frame_seconds / 4)

        if should_finish_stream:
            return

        if len(frames) > 0:
            yield cloud_speech_pb2.StreamingRecognizeRequest(audio_content=frames.pop(0))

def pyaudio_callback(in_data, frame_count, time_info, status):
    # in_data = b"".join(in_data)
    assert isinstance(in_data, bytes)
    frames.append(in_data)
    return (None, pyaudio.paContinue)

def run_recognition_loop():
    global frames
    global silent_frames
    global is_recording
    global should_finish_stream

    if len(silent_frames) > 4:
        silent_frames = silent_frames[-4:]

    while not is_recording:
        time.sleep(args.frame_seconds // 4)

        if len(frames) > 4:
            for frame_index in range(4):
                data = frames[frame_index]
                rms = audioop.rms(data, 2)
                decibel = 20 * math.log10(rms) if rms > 0 else 0
                if decibel < args.silent_decibel:
                    silent_frames += frames[0:frame_index+1]
                    del frames[0:frame_index + 1]
                    return

            is_recording = True
            frames = silent_frames + frames
            silent_frames = []

    with cloud_speech_pb2.beta_create_Speech_stub(make_channel(args.host, args.ssl_port)) as service:
        try:
            listen_loop(service.StreamingRecognize(request_stream(), args.deadline_seconds))
            printr(" ".join((bold(recognition_result.transcription), "    ", "confidence: ", str(int(recognition_result.confidence * 100)), "%")))
            print()
            
            #２次元配列resultに入力結果を格納していく。num_resは配列の番号？順番？で、num_qは質問の番号
            # result[Numres.count].append(recognition_result.transcription, nq)
            result.append([recognition_result.transcription, nq])
            # print(Numres.count)
            print(result)

        except Exception as e:
            print(str(e))

def main():
    global is_recording
    global should_finish_stream
    global nq

    make_txtfile()
    make_q_len()

    start()
    nq = 0
    nq = make_numq(nq)

    pa = pyaudio.PyAudio()
    # devices = []
    for device_index in range(pa.get_device_count()):
        metadata = pa.get_device_info_by_index(device_index)
        print(device_index, metadata["name"])
    stream = pa.open(format=pa.get_format_from_width(2),
                    channels=1,
                    rate=args.sampling_rate,
                    input_device_index=args.device_index,
                    input=True,
                    output=False,
                    frames_per_buffer=int(args.sampling_rate * args.frame_seconds),
                    stream_callback=pyaudio_callback)

    stream.start_stream()

    while True:
        # make_numq()
        is_recording = False
        should_finish_stream = False
        run_recognition_loop()
        write_txt()
        #recognition_result.transcriptionはそのまま使える 

    stream.stop_stream()
    
    stream.close()

    pa.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sampling-rate", "-rate", type=int, default=16000)
    parser.add_argument("--device-index", "-device", type=int, default=0)
    parser.add_argument("--lang-code", "-lang", type=str, default="ja-JP")
    parser.add_argument("--audio-encoding", "-encode", type=str, default="LINEAR16")
    parser.add_argument("--frame-seconds", "-fsec", type=float, default=0.1, help="1フレームあたりの時間（秒）. デフォルトは100ミリ秒")
    parser.add_argument("--deadline-seconds", "-dsec", type=int, default=60*3+5)
    parser.add_argument("--silent-decibel", "-decibel", type=int, default=40)
    parser.add_argument("--speech-scope", "-scope", type=str, default="https://www.googleapis.com/auth/cloud-platform")
    parser.add_argument("--ssl-port", "-port", type=int, default=443)
    parser.add_argument("--host", "-host", type=str, default="speech.googleapis.com")
    args = parser.parse_args()
    
main()
# numres = -1
# for i in range(5):
#     numres = make_numres(numres)
#     print(numres)