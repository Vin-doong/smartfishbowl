# 스마트 어항 (Smart Fishbowl)

라즈베리파이를 활용한 IoT 기반 스마트 어항 시스템으로, 각종 센서를 통해 어항 환경을 모니터링하고 자동/수동으로 관리할 수 있습니다.

## 개요

집에서 물고기를 키우면서 항상 관리에 대한 어려움이 있습니다. 일상생활을 하면서 종종 물고기 먹이를 주는 것을 잊거나 물갈이 등을 잊어버릴 때가 있습니다. 어항 관리를 좀 더 편하게 하기 위해 스마트 어항이라는 작품을 개발했습니다.

사료 공급, 탁도 조절, 수위 체크 등 물고기를 키울 때 필요한 요소들을 라즈베리파이를 기반으로 자동화했습니다.

## 주요 기능

### 수동 모드
1. **센서값 모니터링**: 수위, 조도, 수온, 탁도, 온습도 센서값 출력
   - 새로고침 버튼 클릭 시 센서값 실시간 업데이트
2. **모터 수동 제어**: 
   - 먹이 공급 모터
   - 물 순환 모터
   - 물 공급 모터
3. **LED 조작**: ON/OFF 버튼으로 LED 제어
4. **CCTV 기능**: 파이카메라를 통한 물고기 실시간 관찰
5. **데이터 디스플레이**: 센서값을 LCD 및 앱에 표시

### 자동 모드
1. **조도 센서 기반 LED 제어**: 일정 조도값에 따라 자동으로 LED ON/OFF
2. **수위 센서 기반 물 공급 제어**: 일정 수위값에 도달 시 물 공급 모터 자동 동작
3. **탁도 센서 기반 물 순환 제어**: 일정 탁도값에 도달 시 물 순환 모터 자동 동작

## 하드웨어 구성요소

- 라즈베리파이 (메인 컨트롤러)
- 모터 드라이버 (L298N)
- 서보 모터 (사료 공급용)
- DC 모터 (물 순환 및 물 공급용)
- 각종 센서:
  - 수위 센서
  - 조도 센서
  - 수온 센서 (DS18B20)
  - 탁도 센서
  - 온습도 센서 (DHT11)
- LCD 디스플레이 (I2C)
- LED 조명
- 파이카메라
- PCF8591 ADC 컨버터 (아날로그 센서 인터페이스)

## 소프트웨어 구성

### 백엔드
- Python 기반 Flask 웹 서버
- GPIO 제어 라이브러리
- 센서 데이터 수집 및 처리 모듈
- 자동 제어 알고리즘

### 프론트엔드
- 모바일 애플리케이션 (MIT App Inventor로 개발)
- HTML/CSS 웹 인터페이스 (CCTV 화면용)

## 설치 및 실행 방법

1. 라즈베리파이에 필요한 라이브러리 설치:
```bash
sudo apt-get update
sudo apt-get install python3-pip
pip3 install flask
pip3 install Adafruit_DHT
pip3 install smbus
pip3 install picamera2
pip3 install opencv-python
pip3 install numpy
pip3 install pillow
```

2. 하드웨어 연결:
   - GPIO 핀 연결은 코드 내 설정 참조 (GPIO 5, 6, 13, 19, 21, 26 등 사용)
   - I2C 연결 (LCD, PCF8591)
   - 1-Wire 설정 (수온 센서용)

3. 코드 실행:
```bash
python3 finalfinalwork.py
```

4. 모바일 앱 설치:
   - App Inventor로 제작된 APK 파일 설치

## 코드 설명

### 메인 코드 (finalfinalwork.py)

메인 코드는 다음과 같은 섹션으로 구성되어 있습니다:

1. **라이브러리 임포트 및 초기화**
   - Flask, GPIO, 센서 라이브러리 등 임포트
   - GPIO 설정 및 PWM 초기화

2. **센서 데이터 수집 함수**
   - 각 센서별 데이터 읽기 함수
   - 온습도 센서를 위한 스레드 설정

3. **카메라 스트리밍 설정**
   - Picamera2 설정 및 프레임 캡처 함수

4. **웹 라우트 설정**
   - 메인 페이지, 자동 모드, 수동 모드, CCTV 등 엔드포인트 정의
   - 센서 데이터 표시 및 모터 제어 로직

### LCD 드라이버 (I2C_LCD_driver.py)

I2C를 통한 LCD 디스플레이 제어를 위한 드라이버 코드입니다.

### HTML 템플릿 (index4#2.html)

CCTV 기능을 위한 웹 인터페이스 HTML 파일입니다.

## 3D 프린팅 설계

프로젝트에는 다음과 같은 3D 프린팅 컴포넌트가 포함되어 있습니다:
- 파이카메라 거치대
- LED 거치대 및 LED 바
- LCD 케이스
- 컨트롤박스
- 먹이공급 케이스
- 물통 등

## 네트워크 통신

- TCP/IP 기반 통신
- 포트포워딩을 통한 외부 접속 지원
- Flask 웹서버를 통한 API 제공

## 앱 인터페이스

모바일 앱은 다음과 같은 기능을 제공합니다:
- 센서값 실시간 모니터링
- 수동 모드에서 각 컴포넌트 제어
- 자동 모드 활성화/비활성화
- CCTV 화면 보기

## 제작자

- 김상현(조장)
- 이순민

## 참고자료

- [VNC 화면설정](https://www.youtube.com/watch?v=LlXx9yVfQ0k)
- [PCF8591 사용법](https://blog.naver.com/tiled12/221791735227)
- [Picamera 작동](https://www.youtube.com/watch?v=kuJpdAf07WQ)
- [라즈베리파이 코드 자동실행](https://eggwhite0.tistory.com/73)
- [GPIO 라이브러리](https://abyz.me.uk/rpi/pigpio/index.html)
- [파이카메라 CCTV활용](https://www.youtube.com/watch?v=Y3IdUiFYhe8)
- [플라스크 예제](https://scribblinganything.tistory.com/400)
- [포트포워딩 설정](https://m.blog.naver.com/dsz08082/221871200736)
