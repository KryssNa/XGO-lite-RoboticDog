import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time 
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import signal
from xgolib import XGO
import cv2
import os
import spidev as SPI
import xgoscreen.LCD_2inch as LCD_2inch
from PIL import Image, ImageDraw, ImageFont
from key import Button
import threading
import pyaudio
import wave
import numpy as np
from scipy import fftpack
import speech_recognition as sr

quitmark = 0
button = Button()

def action(num):
    global quitmark
    while quitmark == 0:
        time.sleep(0.01)
        if button.press_b():
            quitmark = 1

check_button = threading.Thread(target=action, args=(0,))
check_button.start()

STATUS_FIRST_FRAME = 0  
STATUS_CONTINUE_FRAME = 1  
STATUS_LAST_FRAME = 2
xunfei = ''  

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }

        url = url + '?' + urlencode(v)
        return url

def on_message(ws, message):
    global xunfei
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:
            data = json.loads(message)["data"]["result"]["ws"]
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            result = json.dumps(data, ensure_ascii=False)
            tx = ''
            for r in data:
                tx += r['cw'][0]['w']
            xunfei += tx
    except Exception as e:
        print("receive msg, but parse exception:", e)

def on_error(ws, error):
    print("### error:", error)

def on_close(ws, t, x):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        frameSize = 8000  
        intervel = 0.04  
        status = STATUS_FIRST_FRAME  

        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                if not buf:
                    status = STATUS_LAST_FRAME

                if status == STATUS_FIRST_FRAME:
                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())

def start_audio(time=3, save_file="test.wav"):
    global quitmark
    start_threshold = 30000
    end_threshold = 8000
    endlast = 10     
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = time 
    WAVE_OUTPUT_FILENAME = save_file  

    p = pyaudio.PyAudio()   
    print("recording...")
    lcd_rect(30, 40, 320, 90, splash_theme_color, -1)
    draw.rectangle((20, 30, 300, 100), splash_theme_color, 'white', width=3)
    lcd_draw_string(draw, 35, 48, "Ready for Recording", color=(255, 0, 0), scale=font3, mono_space=False)
    display.ShowImage(splash)
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    start_luyin = False
    break_luyin = False
    data_list = [0] * endlast
    while not break_luyin:
        if quitmark == 1:
            print('main quit')
            break
        data = stream.read(CHUNK)
        rt_data = np.frombuffer(data, dtype=np.int16)
        fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
        fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
        vol = sum(fft_data) // len(fft_data)
        data_list.pop(0)
        data_list.append(vol)
        if vol > start_threshold:
            print('start recording')
            start_luyin = True
        if start_luyin :
            kkk = lambda x: float(x) < start_threshold
            if all([kkk(i) for i in data_list]):
                break_luyin = True
                frames = frames[:-5]
        if start_luyin:
            frames.append(data)
    
    print('auto end')

    if quitmark == 0:
        lcd_rect(30, 40, 320, 90, splash_theme_color, -1)
        draw.rectangle((20, 30, 300, 100), splash_theme_color, 'white', width=3)
        lcd_draw_string(draw, 35, 48, "RECORDING DONE!", color=(255, 0, 0), scale=font3, mono_space=False)
        display.ShowImage(splash)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')  
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

# ... (unchanged)

def lcd_draw_string(splash, x, y, text, color=(255, 255, 255), font_size=1, scale=1, mono_space=False, auto_wrap=True, background_color=(0, 0, 0)):
    splash.text((x, y), text, fill=color, font=scale) 

def lcd_rect(x, y, w, h, color, thickness):
    draw.rectangle([(x, y), (w, h)], fill=color, width=thickness)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

while 1:
    if button.press_b():
        break

    command = recognize_speech()

    if command:
        print(f"Voice command: {command}")
        if "sheru" in command:
            dog.action(13)  # Assuming action code 13 is for shaking hands
            time.sleep(3)
        else:
            start_audio()
            if quitmark == 0:
                xunfei = ''
                wsParam = Ws_Param(APPID='7582fa81', APISecret='NzIyYzFkY2NiMzBiMTY1ZjUwYTg4MTFm',
                                APIKey='924c1939fdffc06651a49289e2fc17f4',
                                AudioFile='test.wav')
                websocket.enableTrace(False)
                wsUrl = wsParam.create_url()
                ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
                ws.on_open = on_open
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                action(xunfei)
            if quitmark == 1:
                print('main quit')
                break
