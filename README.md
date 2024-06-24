# Plant Hydration Telegram Bot

A Telegram bot designed to automate plant hydration management based on soil moisture levels. This bot allows users to set watering schedules, manually water plants, generate weekly reports, and receive notifications when watering is triggered.

## Features

- **Set and View Watering Schedule:**
  - `/setSchedule HH:MM` - Set a watering schedule in 24-hour format.
  - `/schedule` - View the current watering schedule.

- **Manual Watering Control:**
  - `/waternow` - Manually water the plants immediately.

- **Weekly Report:**
  - `/report` - Generates a weekly report of moisture levels and watering patterns in CSV format.

- **Notification on Moisture-Based Watering:**
  - Sends a message when the soil moisture sensor triggers watering.

- **Help Command:**
  - `/help` - Displays a list of available commands and their usage.

## Installation
### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Viserion-7/Irrigation_Bot.git
   cd Irrigation_Bot
   ```

2. Install dependencies:
   ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r req.txt
    ```

3. Create a .env file in the root directory:

    ```bash
    API_TOKEN=telegram_bot_api_token
    ```

4. Run the bot:

    ```bash
    python3 bot.py
    ```

## Usage

1. Start the Bot:
    - Send `/start` or `/hello` to initialize the bot.

2. Set a Watering Schedule:
    - Use `/setSchedule HH:MM`to set a watering schedule for your plants.

3. Manually Water Plants:
    - Trigger manual watering with `/waternow`.

4. View Current Schedule:
    - Check the current watering schedule using `/schedule`.

5. Generate Weekly Report:
    - Receive a weekly report of moisture levels and watering events with `/report`.

6. Help:
    - Get help and see available commands with `/help`.
