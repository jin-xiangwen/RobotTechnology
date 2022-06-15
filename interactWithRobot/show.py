import cv2
import wave
from cv2 import VideoCapture 
import requests 
import time
import base64 
from pyaudio import PyAudio, paInt16 
from playsound import playsound
import remi.gui as gui
from remi import start, App
from threading import Timer
import tracker
from detector import Detector
from aip import AipSpeech
from playsound import playsound

framerate = 16000 # 采样率
num_samples = 2000 # 采样点
channels = 1 # 声道
sampwidth = 2 # 采样宽度2bytes
FILEPATH = 'Record.wav'

APP_ID = '26062953'
API_KEY = 'NuMs5QtOaveSoiLksozPCkRL'
SECRET_KEY = 'mRyMtNPVIu0rQoSrZgDLtYHiCU8pGi0F'

 # 获 取 token
def GetToken():
    host="https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=NuMs5QtOaveSoiLksozPCkRL&client_secret=mRyMtNPVIu0rQoSrZgDLtYHiCU8pGi0F"
    res = requests.post(host)
    res_json = res.json()['access_token']
    return res_json

# 存 放 录 音 文 件
def SaveWaveFile(filepath, data):
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b''.join(data))
    wf.close()

# 录 音
def Record():
    pa = PyAudio()
    # 打开一个新的音频stream
    stream = pa.open(format=paInt16, channels=channels,
    rate=framerate, input=True, frames_per_buffer=num_samples)
    my_buf = [] # 存放录音数据
    t = time.time()
    print('正在录音...')
    while time.time() < t + 5: # 设置录音时间（秒）
    # 循环read，每次read 2000frames
        string_audio_data = stream.read(num_samples)
        my_buf.append(string_audio_data)
    print('录音结束.')
    SaveWaveFile(FILEPATH, my_buf)
    stream.close()

def GetAudio(file):
    with open(file, 'rb') as f:
        data = f.read()
    return data

def GetResult(FILEPATH, dev_pid=1537):
    token = GetToken()
    speech_data = GetAudio(FILEPATH)
    FORMAT = 'wav'
    RATE = '16000'
    CHANNEL = 1
    CUID = '*******'
    SPEECH = base64.b64encode(speech_data).decode('utf-8')
    data = {
    'format': FORMAT,
    'rate': RATE,
    'channel': CHANNEL,
    'cuid': CUID,
    'len': len(speech_data),
    'speech': SPEECH,
    'token': token,
    'dev_pid': dev_pid
    }
    url = 'https://vop.baidu.com/server_api' # 短语音识别请求地址
    headers = {'Content-Type': 'application/json'}
    print('正在识别...')
    r = requests.post(url, json=data, headers=headers)
    Result = r.json()
    if 'result' in Result:
        return Result['result'][0]
    else:
        return Result

def Action(result):
    pass

class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)

    def main(self):
        # the margin 0px auto centers the main container
        verticalContainer = gui.Container(width='90%', height='90%',  margin='0px auto', style={'display': 'block', 'overflow': 'hidden'})

        self.img = gui.Image(gui.load_resource('/home/jin/文档/interactWithRobot/cover.jpg'), width='100%', height='100%')
        #self.img.onclick.do(self.revise_image)

        verticalContainer.append([self.img])

        self.stop_flag = False 
        self.counter=0
        # 初始化 yolov5
        self.detector = Detector()
        self.capture = cv2.VideoCapture("/home/jin/文档/interactWithRobot/grasp.mp4")
        self.client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        self.revise_image()
        self.organization()

        return verticalContainer 

    def revise_image(self):
        self.detectimg()
        self.img.set_image(gui.load_resource('/home/jin/文档/interactWithRobot/cover.jpg'))
        if not self.stop_flag:
             Timer(1, self.revise_image).start()
    
    def organization(self):
        if self.counter:
            Record()
            self.orgresult = GetResult(FILEPATH, dev_pid=1537)
            print(self.orgresult)
            if  '瓶' in self.orgresult or '水' in self.orgresult:
                self.speak()
        self.counter+=1
        if not self.stop_flag:
             Timer(1, self.organization).start()
    
    def detectimg(self):
        _, im = self.capture.read()
        if im is None:
            return
        bboxes=self.detector.detect(im)
        if len(bboxes) > 0:
            output_image_frame = tracker.draw_bboxes(im, bboxes, line_thickness=None)
        cv2.imwrite("/home/jin/文档/interactWithRobot/cover.jpg",output_image_frame)

    def speak(self):
        result  = self.client.synthesis('正在尝试抓取'+self.orgresult, 'zh', 1, {'vol': 5,})
        if not isinstance(result, dict):
            with open('audio.mp3', 'wb') as f:
                f.write(result)
        playsound('audio.mp3')
        

    def on_close(self):
        self.stop_flag = True
        super(MyApp, self).on_close()


if __name__ == "__main__":
    start(MyApp, debug=True, address='0.0.0.0', port=8081, start_browser=True, multiple_instance=True)
