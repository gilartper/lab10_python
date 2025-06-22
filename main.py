import requests
import pyttsx3
import webbrowser
import os
import pyaudio
from vosk import Model, KaldiRecognizer
engine = pyttsx3.init()
engine.setProperty('rate', 255)

model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)


p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)


def speak(text):
    """Произносит текст"""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


def get_word_info(word, endpoint):
    """Получает информацию о слове с API"""
    try:
        response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        data = response.json()

        if isinstance(data, list):
            if endpoint == "meaning":
                return data[0]['meanings'][0]['definitions'][0]['definition']
            elif endpoint == "example":
                return data[0]['meanings'][0]['definitions'][0].get('example', "No example found")
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None


def save_word(word):
    """Сохраняет слово в файл"""
    with open("saved_words.txt", "a") as f:
        f.write(word + "\n")
    return f"Word '{word}' saved successfully"


def process_command(command):
    """Обрабатывает команды"""
    command = command.lower().strip()

    if command.startswith("find "):
        word = command[5:]
        meaning = get_word_info(word, "meaning")
        if meaning:
            return f"The meaning of '{word}' is: {meaning}"
        return f"Sorry, couldn't find the meaning of '{word}'"

    elif command.startswith("example "):
        word = command[8:]
        example = get_word_info(word, "example")
        if example:
            return f"Example for '{word}': {example}"
        return f"Sorry, couldn't find an example for '{word}'"

    elif command.startswith("save "):
        word = command[5:]
        return save_word(word)

    elif command == "exit":
        speak("Goodbye!")
        exit()

    return "Command not recognized. Please try again."


# Основной цикл
speak("English voice assistant ready. How can I help you?")

while True:
    data = stream.read(4096, exception_on_overflow=False)

    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        command = result[14:-3]

        if command:
            print(f"You said: {command}")
            response = process_command(command)
            speak(response)