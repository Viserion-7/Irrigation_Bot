import RPi.GPIO as GPIO
import time

# Set up GPIO
channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

def callback(channel):
    if GPIO.input(channel):
        print("Soil is dry")
    else:
        print("Soil is wet")

GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300) 
GPIO.add_event_callback(channel, callback)

while True:
    time.sleep(1)