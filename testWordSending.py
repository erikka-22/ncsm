import websocket
import time
import threading
try:
    import thread
except ImportError:
    import _thread as thread

num = 10
msg = ""


def worker():
    global msg
    global num

    if msg == "end":
        print("")
        time.sleep(8)
    else:
        print(num)
        ws.send(str(num))
        num += 1
        time.sleep(8)


def schedule(interval, wait=True):
    base_time = time.time()
    next_time = 0
    while True:
        t = threading.Thread(target=worker)
        t.start()
        # print(msg)
        if wait:
            t.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)
# websocketの通信がエラー状態の時


def main():
    schedule(1, False)


def on_message(ws, message):
    global msg
    msg = message
    # print(msg)


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

    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:5000",
                                on_error=on_error,
                                on_close=on_close,
                                on_message=on_message)

    ws.on_open = on_open

    ws.run_forever()
    # execution()
