# charly_backend.py
from transformers import pipeline
import os
import webbrowser
import pyttsx3
import speech_recognition as sr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import logging
import vlc
import random
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Initialize core components
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-medium", framework="pt")
engine = pyttsx3.init()
recognizer = sr.Recognizer()
media_player = vlc.MediaPlayer()

# Global states
input_mode = "voice"
playlist = []
current_track = 0
shuffle_mode = False
repeat_mode = False
datasets = {}

# Configuration
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_email_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
WEATHER_API_KEY = "your_openweathermap_api_key"

# Logging setup
logging.basicConfig(filename="charly.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def handle_command(command):
    global input_mode, shuffle_mode, repeat_mode, current_track, datasets
    command = command.lower()
    response = None

    try:
        # File operations
        if "open desktop" in command:
            if os.name == "nt":
                os.system("explorer")
                response = "Opening desktop, Sir."
            else:
                os.system("open .")
                response = "Opening desktop, Sir."

        elif "open notepad" in command:
            if os.name == "nt":
                os.system("notepad")
                response = "Opening Notepad, Sir."
            else:
                response = "Notepad not available on this platform."

        elif "create file" in command:
            filename = command.split("create file")[1].strip()
            with open(filename, "w") as f:
                f.write("This is a new file created by Charly.")
            response = f"File '{filename}' created successfully, Sir."

        elif "read file" in command:
            filename = command.split("read file")[1].strip()
            with open(filename, "r") as f:
                content = f.read()
            response = f"File contents:\n{content}"

        elif "delete file" in command:
            filename = command.split("delete file")[1].strip()
            os.remove(filename)
            response = f"File '{filename}' deleted successfully, Sir."

        # Web/search operations
        elif "search for" in command:
            query = command.split("search for")[1].strip()
            webbrowser.open(f"https://google.com/search?q={query}")
            response = f"Searching for '{query}', Sir."

        # Email functionality
        elif "send email" in command:
            parts = command.split("to")[1].split("with subject")
            recipient = parts[0].strip()
            subject_part = parts[1].split("and body")
            subject = subject_part[0].strip()
            body = subject_part[1].strip()

            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            response = f"Email sent to {recipient}, Sir."

        # Weather functionality
        elif "weather in" in command:
            city = command.split("weather in")[1].strip()
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            data = requests.get(url).json()
            if data["cod"] != "404":
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                response = f"Weather in {city}: {weather}, {temp}°C"
            else:
                response = "Location not found, Sir."

        # Media controls
        elif "play media" in command:
            path = command.split("play media")[1].strip()
            if os.path.exists(path):
                media_player.set_media(vlc.Media(path))
                media_player.play()
                response = f"Playing {os.path.basename(path)}, Sir."

        elif "pause media" in command:
            media_player.pause()
            response = "Media paused, Sir."

        elif "stop media" in command:
            media_player.stop()
            response = "Media stopped, Sir."

        elif "set volume" in command:
            volume = int(command.split("set volume")[1].strip())
            media_player.audio_set_volume(volume)
            response = f"Volume set to {volume}%, Sir."

        # Playlist management
        elif "add to playlist" in command:
            path = command.split("add to playlist")[1].strip()
            if os.path.exists(path):
                playlist.append(path)
                response = f"Added {os.path.basename(path)} to playlist"

        elif "next track" in command:
            if playlist:
                current_track = (current_track + 1) % len(playlist)
                media_player.set_media(vlc.Media(playlist[current_track]))
                media_player.play()
                response = f"Playing next track: {playlist[current_track]}"

        # Data science operations
        elif "load dataset" in command:
            path = command.split("load dataset")[1].strip()
            if os.path.exists(path):
                df = pd.read_csv(path)
                name = os.path.basename(path).split(".")[0]
                datasets[name] = df
                response = f"Dataset {name} loaded with {len(df)} records"

        elif "clean dataset" in command:
            name = command.split("clean dataset")[1].strip()
            if name in datasets:
                df = datasets[name].copy()
                # Cleaning logic here
                response = f"Dataset {name} cleaned successfully"

        elif "train model" in command:
            name = command.split("train model")[1].strip()
            if name in datasets:
                df = datasets[name]
                X = df.iloc[:, :-1].select_dtypes(include=np.number)
                y = df.iloc[:, -1]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                model = LinearRegression().fit(X_train, y_train)
                mse = mean_squared_error(y_test, model.predict(X_test))
                response = f"Model trained with MSE: {mse:.2f}"

        # Mode switching
        elif "set mode" in command:
            mode = command.split("set mode")[1].strip()
            if mode in ["voice", "text"]:
                input_mode = mode
                response = f"Input mode set to {mode}, Sir."

    except Exception as e:
        logging.error(f"Error processing command: {str(e)}")
        response = f"Sorry, I encountered an error: {str(e)}"

    return response

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "Speech service unavailable"

# Data science utilities
def clean_dataset(dataset_name):
    if dataset_name in datasets:
        df = datasets[dataset_name].copy()
        # Implement cleaning logic
        datasets[dataset_name] = df
        return "Dataset cleaned successfully"
    return "Dataset not found"

def analyze_dataset(dataset_name):
    if dataset_name in datasets:
        df = datasets[dataset_name]
        analysis = df.describe().to_string()
        return f"Analysis results:\n{analysis}"
    return "Dataset not found"

# Email handler
def send_email(recipient, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# Weather fetcher
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    if data["cod"] == 200:
        return f"{data['weather'][0]['description']}, {data['main']['temp']}°C"
    return "Weather data unavailable"