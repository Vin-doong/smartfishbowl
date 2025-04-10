import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
from http.server import baseHTTPRequesthandler, httpServer

	elif Request == 'saryo':
		GPIO.output(16, 1)
		GPIO.output(20, 0)
		time.sleep(5)
		GPIO.output(16, 0)
		GPIO.output(20, 0)
		state = 'feed'
		
