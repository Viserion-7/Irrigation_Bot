import RPi.GPIO as GPIO
import time

# Set up GPIO
channel = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

def soil_callback(channel):
    if GPIO.input(channel):
        return "Soil is dry"
    else:
        return "Soil is wet"

def setup_soil_sensor(callback):
    GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
    GPIO.add_event_callback(channel, callback)

# To avoid running code during import
if __name__ == "__main__":
    setup_soil_sensor(soil_callback)
    while True:
        time.sleep(1)
