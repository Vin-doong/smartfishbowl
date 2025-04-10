import RPi.GPIO as GPIO
import time

# GPIO 핀 번호 설정 (센서와 연결된 핀 번호에 맞게 변경해주세요)
sensor_pin = 18

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensor_pin, GPIO.IN)

def read_turbidity():
    # 탁도 센서 값 읽기 (0 또는 1로 반환됩니다)
    return GPIO.input(sensor_pin)

def main():
    try:
        setup()
        while True:
            turbidity_value = read_turbidity()
            print("Turbidity: ", turbidity_value)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by the user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
