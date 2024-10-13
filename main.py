import sys
import speech_recognition as sr
import pygame
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer
from ui_form import Ui_MainWindow
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from speech_recognition import WaitTimeoutError

# elevenlabs santa claus voice id
voice_id = "Gqe8GJJLg3haJkTwYj2L"

# api keys open ai/elevenlabs
open_ai = OpenAI(api_key="ADD API KEY")
elevenlabs = ElevenLabs(api_key="ADD API KEY")  # Replace with your ElevenLabs API key

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.setFixedSize(800, 600)
        self.ui.setupUi(self)
        self.setWindowTitle("Talk to Santa")
        self.ui.pushButton.toggled.connect(self.talk_button_toggled)
        self.connected = False

    # Toggle button that changes image and calls the method
    def talk_button_toggled(self, checked):
        if checked:
            self.ui.background.setPixmap(QPixmap("images/santa_start.png"))
            self.button_sound()
            self.connect()
        else:
            self.ui.background.setPixmap(QPixmap("images/santa_stop.png"))
            self.ui.pushButton.setChecked(False)

    # Establish a connection by setting a flag and starting the listening process
    def connect(self):
        self.connected = True
        QTimer.singleShot(10, self.start_listening)

    # Disconnect the current session and update the UI image
    def disconnect(self):
        self.connected = False
        self.ui.background.setPixmap(QPixmap(":/images/santa_stop.png"))
        self.ui.pushButton.setChecked(False)
        self.disconnect_sound()

    # Start listening for audio input from the microphone
    def start_listening(self):
        recognizer = sr.Recognizer()

        if self.connected:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source, duration=1)

                try:
                    audio = recognizer.listen(source, timeout=4)
                    text = recognizer.recognize_google(audio)
                    self.signal_sound()
                    self.question(text)
                except sr.UnknownValueError:
                    print("Could not understand audio.")
                    self.disconnect()
                except WaitTimeoutError:
                    print("Listening timed out; no phrase detected.")
                    self.disconnect()  # Disconnect or take appropriate action
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    self.disconnect()
            QTimer.singleShot(10, self.start_listening)

    # Process the text generated by speech recognition using OpenAI's GPT-3.5 model
    def question(self, user):
        print("OpenAI processing...")
        try:
            response = open_ai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Santa Claus, the jolly and magical figure loved by children. "
                                   "Answer children's questions with warmth, kindness, "
                                   "and a sprinkle of holiday magic. "
                                   "Keep your responses short and sweet, under 30 words."
                    },
                    {
                        "role": "user",
                        "content": f"{user}"
                    }
                ],
                timeout=5
            )
            print("Open AI complete")
            self.talk(response.choices[0].message.content)
        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            self.disconnect()

    # Generate audio using ElevenLabs text-to-speech AI generator
    def talk(self, user):
        print("ElevenLabs processing...")
        audio_stream = elevenlabs.generate(
            text=f"{user}",
            stream=True,
            voice=voice_id
        )
        self.connected_sound()
        play(audio_stream)
        print("ElevenLabs complete")

    def button_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load("audio/button_push.mp3")
        pygame.mixer.music.play()
    # Play a sound to indicate a connection has been established
    def signal_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load("audio/signal.mp3")
        pygame.mixer.music.play()

    # Play a sound to indicate a successful connection
    def connected_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load("audio/connected.mp3")
        pygame.mixer.music.play()

    # Play a sound to indicate a disconnection has occurred
    def disconnect_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load("audio/disconnect.mp3")
        pygame.mixer.music.play()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
