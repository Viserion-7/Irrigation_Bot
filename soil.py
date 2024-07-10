import RPi.GPIO as GPIO
import time

# Set up GPIO
channel = 14
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Add pull-down resistor

def soil_callback(channel):
    if GPIO.input(channel):
        print("Soil is dry")
    else:
        print("Soil is wet")

def setup_soil_sensor(callback):
    try:
        GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)
        GPIO.add_event_callback(channel, callback)
    except RuntimeError as e:
        print(f"Failed to add edge detection: {e}")

# To avoid running code during import
if __name__ == "__main__":
    setup_soil_sensor(soil_callback)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
