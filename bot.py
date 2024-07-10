import telebot
import os
import json
import csv
import datetime
import re
import RPi.GPIO as GPIO
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Global variables to store schedule and data
schedule_file = 'schedule.txt'
moisture_data_file = 'moisture_data.json'
chat_id = None

# GPIO setup
MOISTURE_SENSOR_PIN = 21
PUMP_PIN = 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.output(PUMP_PIN, GPIO.HIGH)  # Turn off pump initially

# Load initial schedule from file
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
    bot.send_message(chat_id, "Watering plants manually now!")
    log_watering_event(manual=True)

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
    GPIO.output(PUMP_PIN, GPIO.LOW)
    time.sleep(delay)
    GPIO.output(PUMP_PIN, GPIO.HIGH)
    with open("last_watered.txt", "w") as f:
        f.write("Last watered {}".format(datetime.datetime.now()))

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

# Bot command handlers
@bot.message_handler(commands=['start', 'hello'])
def greet(message):
    global chat_id
    chat_id = message.chat.id
    bot.reply_to(message, 'Hello! I am your Plant Hydration Bot. Type /help to see what I can do.')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "/start or /hello - Greet the bot\n"
        "/waternow - Manually water the plants\n"
        "/setSchedule HH:MM - Set a watering schedule (24-hour format)\n"
        "/schedule - View the current watering schedule\n"
        "/report - Generate and receive the weekly moisture and watering report\n"
        "/help - Show this help message"
    )
    bot.send_message(chat_id, help_text)

@bot.message_handler(commands=['waternow'])
def handle_water_now(message):
    water_now()

@bot.message_handler(commands=['setSchedule'])
def handle_set_schedule(message):
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
    view_schedule()

@bot.message_handler(commands=['report'])
def handle_generate_report(message):
    generate_weekly_report()

@bot.message_handler(func=lambda message: True)
def handle_default(message):
    bot.reply_to(message, 'I did not understand that command. Type /help to see what I can do.')

bot.infinity_polling()
