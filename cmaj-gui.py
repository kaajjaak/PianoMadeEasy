import tkinter as tk
import pygame
import random
import numpy


class NoteGame:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2)

        self.notes = {
            'C4': 261.63,
            'D4': 293.66,
            'E4': 329.63,
            'F4': 349.23,
            'G4': 392.00,
            'A4': 440.00,
            'B4': 493.88
        }

        self.root = tk.Tk()
        self.root.title("Note Recognition Game")
        self.root.geometry("400x300")

        self.feedback_label = tk.Label(self.root, text="Listen to the note and select the correct one",
                                       font=("Arial", 12))
        self.feedback_label.pack(pady=20)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(pady=20)

        for note in self.notes.keys():
            btn = tk.Button(self.button_frame, text=note, width=5,
                            command=lambda n=note: self.check_answer(n))
            btn.pack(side=tk.LEFT, padx=5)

        self.play_button = tk.Button(self.root, text="Play Note Again", command=self.play_current_note)
        self.play_button.pack(pady=20)

        self.current_note = None
        self.generate_new_note()

    def generate_new_note(self):
        self.current_note = random.choice(list(self.notes.keys()))
        self.play_current_note()

    def play_current_note(self):
        frequency = self.notes[self.current_note]
        duration = 1.0
        sample_rate = 44100
        t = numpy.linspace(0, duration, int(sample_rate * duration))
        wave = numpy.sin(2 * numpy.pi * frequency * t)

        # Convert to 16-bit integers and create a stereo array
        audio_data = (wave * 32767).astype(numpy.int16)
        stereo_data = numpy.column_stack((audio_data, audio_data))

        pygame.sndarray.make_sound(stereo_data).play()

    def check_answer(self, selected_note):
        if selected_note == self.current_note:
            self.feedback_label.config(text="Correct!", fg="green")
            self.root.after(1000, self.reset_game)
        else:
            self.feedback_label.config(text="Try again!", fg="red")
            self.root.after(1000, self.play_current_note)

    def reset_game(self):
        self.feedback_label.config(text="Listen to the note and select the correct one", fg="black")
        self.generate_new_note()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    game = NoteGame()
    game.run()
