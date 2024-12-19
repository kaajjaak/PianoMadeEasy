import pygame.midi
import random
import time
import os
from colorama import Fore, Style
from collections import defaultdict, deque


# Clear screen function (cross-platform)
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# C Major scale notes in MIDI (C4 to B4)
C_MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71]  # MIDI note numbers for C4 to B4
NOTE_NAMES = {60: "C4", 62: "D4", 64: "E4", 65: "F4", 67: "G4", 69: "A4", 71: "B4"}


class NoteTracker:
    def __init__(self):
        self.correct_counts = defaultdict(int)
        self.incorrect_counts = defaultdict(int)
        self.last_ten = deque(maxlen=10)  # Track last 10 attempts
        self.total_notes = 0

    def update(self, note, correct):
        if correct:
            self.correct_counts[note] += 1
            self.last_ten.append(True)
        else:
            self.incorrect_counts[note] += 1
            self.last_ten.append(False)
        self.total_notes += 1

    def get_weight(self, note):
        correct = self.correct_counts[note]
        incorrect = self.incorrect_counts[note]
        total = correct + incorrect + 1  # Add 1 to avoid division by zero

        # Notes with more mistakes get higher weights
        weight = (incorrect + 1) / total
        return max(0.1, weight)  # Ensure minimum weight of 0.1

    def show_progress(self):
        if len(self.last_ten) == 10:
            correct = sum(1 for x in self.last_ten if x)
            print(f"\n=== Last 10 Notes Statistics ===")
            print(Fore.GREEN + f"Correct: {correct}" + Style.RESET_ALL)
            print(Fore.RED + f"Wrong: {10 - correct}" + Style.RESET_ALL)
            print(f"Accuracy: {(correct/10)*100:.1f}%")
            print("===============================")
            time.sleep(3)


def start_screen(midi_input):
    """
    Display the start screen and ensure the piano is connected.
    """
    clear_screen()
    print("🎹 Welcome to the C Major Scale Trainer! 🎹\n")
    print("Please play any note on your piano to confirm the connection...")

    while True:
        if midi_input.poll():
            midi_event = midi_input.read(1)
            note = midi_event[0][0][1]
            print(f"✅ Piano connected! Detected note: {NOTE_NAMES.get(note, 'Unknown')} (MIDI {note})")
            time.sleep(2)
            break


def play_note(midi_output, note):
    """
    Play a MIDI note using the connected piano.
    """
    midi_output.note_on(note, velocity=127)
    time.sleep(1)
    midi_output.note_off(note, velocity=127)
    time.sleep(0.1)


def clear_input_buffer(midi_input):
    """
    Clear any pending MIDI input events.
    """
    while midi_input.poll():
        midi_input.read(1)


def choose_next_note(tracker, previous_note=None):
    """
    Choose the next note based on weights from the tracker.
    Avoid repeating the same note twice in a row.
    """
    weights = [tracker.get_weight(note) for note in C_MAJOR_SCALE]

    # Reduce weight of the previous note to avoid repetition
    if previous_note is not None:
        idx = C_MAJOR_SCALE.index(previous_note)
        weights[idx] *= 0.3

    total = sum(weights)
    weights = [w / total for w in weights]

    return random.choices(C_MAJOR_SCALE, weights=weights, k=1)[0]


def main():
    pygame.midi.init()

    try:
        device_count = pygame.midi.get_count()
        if device_count == 0:
            print("No MIDI devices found. Please connect your piano and try again.")
            return

        print("\nAvailable MIDI devices:")
        for i in range(device_count):
            info = pygame.midi.get_device_info(i)
            print(f"{i}: {info[1].decode()} ({'Input' if info[2] else 'Output'})")

        input_id = int(input("\nEnter the ID of your MIDI Input device (keyboard): "))
        output_id = int(input("Enter the ID of your MIDI Output device (to play notes): "))

        midi_input = pygame.midi.Input(input_id)
        midi_output = pygame.midi.Output(output_id)
        tracker = NoteTracker()

        start_screen(midi_input)

        previous_note = None
        while True:
            clear_screen()

            # Show progress every 10 notes
            if tracker.total_notes > 0 and tracker.total_notes % 10 == 0:
                tracker.show_progress()
                clear_screen()

            target_note = choose_next_note(tracker, previous_note)
            previous_note = target_note

            clear_input_buffer(midi_input)
            print("🎵 Playing...")
            play_note(midi_output, target_note)
            clear_input_buffer(midi_input)

            waiting_for_input = True
            while waiting_for_input:
                if midi_input.poll():
                    midi_event = midi_input.read(1)
                    played_note = midi_event[0][0][1]
                    velocity = midi_event[0][0][2]

                    if midi_event[0][0][0] == 0x90 and velocity > 0:
                        clear_screen()
                        if played_note == target_note:
                            print(Fore.GREEN + "✅ Correct!" + Style.RESET_ALL)
                            tracker.update(target_note, True)
                            waiting_for_input = False
                        else:
                            print(Fore.RED + "❌ Wrong!" + Style.RESET_ALL)
                            tracker.update(target_note, False)
                            time.sleep(1.5)
                            print("\n🎵 Playing again...")
                            play_note(midi_output, target_note)
                            clear_input_buffer(midi_input)

                time.sleep(0.1)

            time.sleep(2)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        pygame.midi.quit()


if __name__ == "__main__":
    main()
