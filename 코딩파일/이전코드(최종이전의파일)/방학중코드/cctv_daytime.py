from flask import Flask, render_template, Response
from PIL import ImageFont, ImageDraw, Image
import datetime
from picamera2 import Picamera2
import numpy as np
import cv2

app = Flask(__name__)

# Picamera2 객체 생성
piCam = Picamera2()

# 미리보기 설정: 크기 640x480
piCam.preview_configuration.main.size = (640, 480)
piCam.preview_configuration.main.format = "RGB888"
piCam.preview_configuration.align()

# 카메라 시작
piCam.start()

font = ImageFont.truetype('fonts/SCDream6.otf', 20)

def gen_frames():  
    while True:
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
        frame = piCam.capture_array()  # 현재 프레임을 캡처

        frame = Image.fromarray(frame)
        draw = ImageDraw.Draw(frame)
        draw.text(xy=(10, 15), text="스마트어항 " + nowDatetime, font=font, fill=(255, 255, 255))
        frame = np.array(frame)
        
        ref, buffer = cv2.imencode('.jpg', frame)            
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # 그림파일들을 쌓아두고 호출을 기다림

@app.route('/')
def index():
    return render_template('index4#2.html')  # index4#2.html 템플릿을 렌더링하여 웹 페이지 반환

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8091")
    # 웹 사이트를 호스팅하여 접속자에게 보여주기 위해 Flask 애플리케이션 실행
    # 호스트는 라즈베리 파이의 내부 IP, 포트는 임의로 설정
    # 내부 IP와 포트를 포트 포워딩하면 외부에서도 접속 가능
