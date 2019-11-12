import json
import codecs


def divideText(showChar: str, buffer):
    for char in showChar:
        buffer.put(char)


def append_json_to_file(data: dict, path_file: str) -> bool:
    with open(path_file, 'ab+') as f:
        f.seek(0, 2)
        if f.tell() == 0:
            f.write(json.dumps([data], ensure_ascii=False,
                               indent=3).encode('utf-8'))
        else:
            f.seek(-1, 2)
            f.truncate()
            f.write(' , '.encode())
            f.write(json.dumps(data, ensure_ascii=False, indent=3).encode('utf-8'))
            f.write(']'.encode())
    return f.close()

# 認識結果を書き込む指示


def writeText(text: list, icon_dir: str, icon_name: str, json_file_path: str):
    comment_text = '，'.join(text)
    print(comment_text)
    icon_path = icon_dir + icon_name + ".jpg"
    card = {'pic_name': icon_path, 'comment': comment_text}

    append_json_to_file(card, json_file_path)

    f_saved = codecs.open(json_file_path, "r", 'utf-8')
    contents = f_saved.read()
    print(contents)
    f_saved.close()
