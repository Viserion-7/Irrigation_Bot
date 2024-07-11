import telebot
import os
import json
import csv
import datetime
import re
import RPi.GPIO as GPIO
import time
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Global variables to store schedule and data
schedule_file = 'schedule.txt'
moisture_data_file = 'moisture_data.json'
chat_id = None

# GPIO setup
MOISTURE_SENSOR_PIN = 14
PUMP_PIN = 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.output(PUMP_PIN, GPIO.LOW)

try:
    with open(schedule_file, 'r') as f:
        schedule = json.load(f)
except FileNotFoundError:
    schedule = None

# Load initial moisture data from file
try:
    with open(moisture_data_file, 'r') as f:
        moisture_data = json.load(f)
except FileNotFoundError:
    moisture_data = []

# Function to manually water plants
def water_now():
    pump_on()
    log_watering_event(manual=True)
    time.sleep(1)
    pump_off()

# Function to validate the time format
def is_valid_time_format(time_str):
    time_format = re.compile(r'^([01]\d|2[0-3]):([0-5]\d)$')
    return bool(time_format.match(time_str))

# Function to set a watering schedule
def set_schedule(time):
    global schedule
    schedule = time
    with open(schedule_file, 'w') as f:
        json.dump(schedule, f)
    bot.send_message(chat_id, f"Watering schedule set to {time}")

# Function to view the current watering schedule
def view_schedule():
    if schedule:
        bot.send_message(chat_id, f"Current watering schedule: {schedule}")
    else:
        bot.send_message(chat_id, "No watering schedule set.")

# Function to log watering events
def log_watering_event(manual=False):
    event = {
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
        "manual": manual,
        "moisture_level": get_current_moisture_level()
    }
    moisture_data.append(event)
    with open(moisture_data_file, 'w') as f:
        json.dump(moisture_data, f)

# Function to get current moisture level
def get_current_moisture_level():
    return GPIO.input(MOISTURE_SENSOR_PIN)  # Returns 0 if wet, 1 if dry

# Function to turn on the pump
def pump_on(delay=1):
    print("Pumping")
    GPIO.output(PUMP_PIN, GPIO.LOW)
    time.sleep(delay)
    GPIO.output(PUMP_PIN, GPIO.HIGH)
    with open("last_watered.txt", "w") as f:
        f.write("Last watered {}".format(datetime.datetime.now()))

# Function to turn off the pump
def pump_off(delay=1):
    print("Pump off")
    GPIO.output(PUMP_PIN, GPIO.LOW)
    time.sleep(delay)

# Function to generate weekly report and save as CSV
def generate_weekly_report():
    now = datetime.datetime.now()
    one_week_ago = now - datetime.timedelta(days=7)
    report_data = [entry for entry in moisture_data if datetime.datetime.strptime(entry["timestamp"], '%Y-%m-%d %H:%M') > one_week_ago]

    csv_file = 'weekly_report.csv'
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Manual', 'Moisture Level'])
        for entry in report_data:
            writer.writerow([entry['timestamp'], entry['manual'], entry['moisture_level']])

    bot.send_message(chat_id, "Here is the weekly moisture and watering report.")
    bot.send_document(chat_id, open(csv_file, 'rb'))

# Thread function to check schedule and run pump
def schedule_checker():
    while True:
        if schedule:
            now = datetime.datetime.now()
            schedule_time = datetime.datetime.strptime(schedule, '%H:%M').time()
            current_time = now.time()

            if current_time >= schedule_time and current_time <= (datetime.datetime.combine(now, schedule_time) + datetime.timedelta(minutes=2)).time():
                print("Scheduled watering")
                bot.send_message(chat_id, f"Watering as per schedule at {schedule_time}")
                water_now()
                time.sleep(60)

        time.sleep(30)  # Check every 30 seconds

moisture_status = ""

def moisture_check():
    moisture_level = get_current_moisture_level()
    global moisture_status

    if moisture_level == 0:
        moisture_status = "wet"
        pump_off()
    else:
        moisture_status = "dry"
        water_now()

check_frequency = 0

# Function to check moisture periodically
def periodic_moisture_check():
    while True:
        print("Auto-checking moisture level.")
        moisture_check()
        time.sleep(check_frequency)

# Start the schedule checking thread
schedule_thread = threading.Thread(target=schedule_checker)
schedule_thread.daemon = True
schedule_thread.start()

# Start the periodic moisture checking thread
moisture_check_thread = threading.Thread(target=periodic_moisture_check)
moisture_check_thread.daemon = True
moisture_check_thread.start()

# Bot command handlers
@bot.message_handler(commands=['start', 'hello'])
def greet(message):
    print("Command Read: /start or hello")
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, 'Hello! I am your Plant Hydration Bot. Type /help to see what I can do.')

@bot.message_handler(commands=['help'])
def help_command(message):
    print("Command Read: /help")
    help_text = (
        "/start or /hello - Greet the bot\n"
        "/waternow - Manually water the plants\n"
        "/setSchedule HH:MM - Set a watering schedule (24-hour format)\n"
        "/schedule - View the current watering schedule\n"
        "/report - Generate and receive the weekly moisture and watering report\n"
        "/checkMoisture - Check the current moisture level\n"
        "/help - Show this help message"
    )
    bot.send_message(chat_id, help_text)

@bot.message_handler(commands=['waternow'])
def handle_water_now(message):
    print("Command Read: /waternow")
    water_now()

@bot.message_handler(commands=['setMoistureCheckFrequency'])
def handle_set_moisture_check_frequency(message):
    print("Command Read: /setMoistureCheckFrequency")
    try:
        global check_frequency
        check_frequency = int(message.text.split('/setMoistureCheckFrequency ')[1])
        bot.send_message(chat_id, f"Moisture check frequency set to {check_frequency} seconds.")
    except IndexError:
        bot.send_message(chat_id, "Please provide a frequency in seconds. Usage: /setMoistureCheckFrequency <frequency in seconds>")

@bot.message_handler(commands=['setSchedule'])
def handle_set_schedule(message):
    print("Command Read: /setSchedule")
    try:
        time = message.text.split('/setSchedule ')[1]
        if is_valid_time_format(time):
            set_schedule(time)
        else:
            bot.send_message(chat_id, "Please provide a valid time in HH:MM format (24 Hr).")
    except IndexError:
        bot.send_message(chat_id, "Please provide a time for the schedule. Usage: /setSchedule HH:MM")

@bot.message_handler(commands=['schedule'])
def handle_view_schedule(message):
    print("Command Read: /schedule")
    view_schedule()

@bot.message_handler(commands=['report'])
def handle_generate_report(message):
    print("Command Read: /report")
    generate_weekly_report()

@bot.message_handler(commands=['checkMoisture'])
def handle_check_moisture(message):
    print("Command Read: /checkMoisture")
    global moisture_status
    moisture_check()
    log_watering_event(manual=False)
    bot.send_message(chat_id, f"The current moisture level is {moisture_status}. Pump turned {'off' if moisture_status == 'wet' else 'on'}.")

@bot.message_handler(func=lambda message: True)
def handle_default(message):
    print("Command Read: /bullshit")
    bot.reply_to(message, 'I did not understand that command. Type /help to see what I can do.')

try:
    bot.infinity_polling()
finally:
    GPIO.cleanup()