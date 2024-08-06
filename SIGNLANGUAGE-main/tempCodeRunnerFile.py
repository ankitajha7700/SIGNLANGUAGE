

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')
import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import numpy as np
import pickle
from PIL import Image, ImageTk
from googletrans import Translator
import pyttsx3
from gtts import gTTS
import pygame
import os

# Load model
with open('./model.p', 'rb') as model_file:
    model_dict = pickle.load(model_file)
model = model_dict['model']

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Labels dictionary
labels_dict = {0: 'Hello', 1: 'Welcome', 2: 'Thank You', 3: 'How Are You', 4: 'My name is', 5: 'A', 6: 'N', 7: 'I', 8: 'S'}

# Initialize Translator
translator = Translator()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sign Language Recognition")
        self.configure(bg='lightblue')
        
        self.languages = {
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Arabic": "ar",
            "Assamese": "as",
            "Belarusian": "be",
            "Bengali": "bn",
            "Chinese (Simplified)": "zh-cn",
            "Chinese (Traditional)": "zh-tw",
            "Dutch": "nl",
            "Hindi": "hi",
            "Italian": "it",
            "Japanese": "ja",
            "Korean": "ko",
            "Portuguese": "pt",
            "Russian": "ru",
            "Turkish": "tr",
            "Urdu": "ur"
        }
        self.language_names = list(self.languages.keys())
        self.selected_language = tk.StringVar()

        self.video_frame = ttk.Frame(self, borderwidth=2, relief="groove")
        self.video_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=10)

        self.prediction_label = tk.Label(self, text="", font=("Helvetica", 20), bg='lightblue')
        self.prediction_label.pack(side=tk.TOP, pady=2)

        self.word_label = tk.Label(self, text="Current Word: ", font=("Helvetica", 20), bg='lightblue')
        self.word_label.pack(side=tk.TOP, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        text_to_video_button = ttk.Button(button_frame, text="Text-to-Video", command=self.show_text_to_video_page)
        text_to_video_button.pack(side=tk.LEFT, padx=5)

        self.speak_button = tk.Button(button_frame, text="Speak", command=self.speak_word, width=12)
        self.speak_button.pack(side=tk.LEFT, padx=5)

        self.speak_translated_button = tk.Button(button_frame, text="Speak Translated", command=self.speak_translated_word, width=12)
        self.speak_translated_button.pack(side=tk.LEFT, padx=5)

        self.space_button = tk.Button(button_frame, text="Space", command=self.add_space, width=12)
        self.space_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_word, width=12)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.submit_button = tk.Button(button_frame, text="Submit", command=self.submit_word, width=12)
        self.submit_button.pack(side=tk.LEFT, padx=5)

        self.add_text_button = tk.Button(button_frame, text="Add Text", command=self.add_text, width=12)
        self.add_text_button.pack(side=tk.LEFT, padx=5)

        self.translate_button = tk.Button(button_frame, text="Translate", command=self.translate_word, width=12)
        self.translate_button.pack(side=tk.LEFT, padx=5)

        self.language_dropdown = ttk.Combobox(self, values=self.language_names, textvariable=self.selected_language, font=("Helvetica", 10))
        self.language_dropdown.set("Select Language")
        self.language_dropdown.pack(side=tk.BOTTOM, pady=5)




        self.text_entry = tk.Entry(self, font=("Helvetica", 20))
        self.text_entry.pack(side=tk.BOTTOM, pady=5)

        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            raise RuntimeError("Error: Could not start video capture.")

        self.running = True
        self.predicted_character = ""
        self.current_word = ""
        self.translated_word = ""

        self.update_frame()

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                H, W, _ = frame.shape
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)

                data_aux = []
                x_ = []
                y_ = []

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp_hands.HAND_CONNECTIONS,
                            mp_drawing_styles.get_default_hand_landmarks_style(),
                            mp_drawing_styles.get_default_hand_connections_style()
                        )

                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            data_aux.append(x)
                            data_aux.append(y)
                            x_.append(x)
                            y_.append(y)

                    if len(results.multi_hand_landmarks) == 1:
                        data_aux.extend([0] * 42)

                    if len(data_aux) == 84:
                        x1 = int(min(x_) * W) - 10
                        y1 = int(min(y_) * H) - 10
                        x2 = int(max(x_) * W) + 10
                        y2 = int(max(y_) * H) + 10

                        prediction = model.predict([np.asarray(data_aux)])
                        prediction_label = int(prediction[0])
                        self.predicted_character = labels_dict.get(prediction_label, "Not Recognized")

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                        cv2.putText(frame, self.predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

                        self.prediction_label.config(text=f"Predicted Character: {self.predicted_character}")

                    else:
                        self.prediction_label.config(text="Feature size mismatch")

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            self.video_label.after(10, self.update_frame)

    def display_gif(self, text, window, text_entry_var, gif_frame):
        gif_frame.pack_forget()  # Clear the gif_frame
        gif_frame.pack(fill=tk.BOTH, expand=True)
        words = text.split()
        for word in words:
            if word in labels_dict.values():
                gif_label = ttk.Label(gif_frame)
                gif_path = f"./gif/{word}.png"
                gif_image = Image.open(gif_path)
                gif_photo = ImageTk.PhotoImage(gif_image)
                gif_label.config(image=gif_photo)
                gif_label.image = gif_photo
                gif_label.pack(side=tk.LEFT, padx=5)
            else:
                self.display_gif.config(text="Not present in the datasets")
                pass
        clear_button = ttk.Button(window, text="Clear", command=lambda: self.clear_text_and_gif(text_entry_var, gif_frame))
        clear_button.pack(side=tk.BOTTOM, pady=5)    

    def show_text_to_video_page(self):

        
        text_to_video_window = tk.Toplevel(self)
        text_to_video_window.title("Text to Video")
        text_to_video_window.geometry("600x400")
        text_entry_frame = ttk.Frame(text_to_video_window, padding="10")
        text_entry_frame.pack(fill=tk.BOTH, expand=True)
        text_entry_label = ttk.Label(text_entry_frame, text="Enter text:")
        text_entry_label.pack(side=tk.TOP, pady=5)
        text_entry_var = tk.StringVar()
        text_entry = ttk.Entry(text_entry_frame, textvariable=text_entry_var, width=50)
        text_entry.pack(side=tk.TOP, pady=5)
        submit_button_frame = ttk.Frame(text_to_video_window, padding="10")
        submit_button_frame.pack(fill=tk.BOTH, expand=True)
        submit_button = ttk.Button(submit_button_frame, text="Submit", command=lambda: self.display_gif(text_entry_var.get(), text_to_video_window, text_entry_var,gif_frame=))  # Pass text_entry_var and gif_frame as arguments
        submit_button.pack(side=tk.TOP, pady=5)
        

   
   

    def clear_text_and_gif(self, text_var, gif_frame):
        text_var.set("")
        for child in gif_frame.winfo_children():
            child.destroy()

    def speak_word(self):
        try:
            if self.current_word.strip():
                engine = pyttsx3.init()
                engine.say(self.current_word)
                engine.runAndWait()
            else:
                print("Error: No word to speak.")
        except Exception as e:
            print(f"Error in speak_word: {e}")

    def add_space(self):
        self.current_word += " "
        self.word_label.config(text=f"Current Word: {self.current_word}")

    def clear_word(self):
        self.current_word = ""
        self.word_label.config(text="Current Word: ")

    def submit_word(self):
        word = self.text_entry.get().strip()
        if word:
            self.current_word = word
            self.word_label.config(text=f"Current Word: {self.current_word}")
        else:
            print("Error: Word is empty.")

    def add_text(self):
        if self.predicted_character != "Not Recognized":
            self.current_word += self.predicted_character
        self.word_label.config(text=f"Current Word: {self.current_word}")

    def translate_word(self):
        if self.current_word and self.selected_language.get() != "Select Language":
            target_language = self.languages.get(self.selected_language.get())
            if not target_language:
                self.word_label.config(text="Invalid Language Selected")
                return

            try:
                translated = translator.translate(self.current_word, dest=target_language)
                if translated:
                    self.translated_word = translated.text
                    self.word_label.config(text=f"Translated Word: {self.translated_word}")
                else:
                    self.word_label.config(text="Translation Failed")
            except Exception as e:
                self.word_label.config(text=f"Translation Error: {e}")

    def speak_translated_word(self):
        try:
            if self.translated_word.strip():
                target_language = self.languages.get(self.selected_language.get())
                if not target_language:
                    print("Error: Invalid language selected.")
                    return

                tts = gTTS(text=self.translated_word, lang=target_language)
                filename = "temp.mp3"
                tts.save(filename)

                pygame.mixer.init()
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
                pygame.mixer.quit()

                os.remove(filename)
            else:
                print("Error: No translated word to speak.")
        except Exception as e:
            print(f"Error in speak_translated_word: {e}")

if __name__ == "__main__":
    try:
        pygame.init()
        app = App()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")





