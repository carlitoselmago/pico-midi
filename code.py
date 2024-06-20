import time
import usb_midi
import board
import analogio
import adafruit_midi
from adafruit_midi.note_on import NoteOn

# Initialize MIDI output
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1])

# Analog input setup for the piezo sensor (connected to GP26 / ADC0)
piezo = analogio.AnalogIn(board.A0)
piezo2 = analogio.AnalogIn(board.A1)

octave = 4
midi_channel = 1  # 0-15
midi_channel2 = 2
last_velocity = 0
last_velocity2 = 0
velocity_threshold = 5

def map_value(x, in_min, in_max, out_min, out_max):
    """
    Re-maps a number from one range to another.
    """
    mapped_value = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return max(min(mapped_value, out_max), out_min)

# Variables for debouncing
debounce_delay = 0.05  # 50ms debounce delay
last_hit_time = 0
last_hit_time2 = 0

while True:
    # Read the analog value from the piezo sensor
    analog_value = piezo.value
    midi_velocity = int(map_value(analog_value, 6000, 0, 0, 127))
    
    analog_value2 = piezo2.value
    midi_velocity2 = int(map_value(analog_value2, 6000, 0, 0, 127))
    #print("analog",analog_value,"midi_velocity",midi_velocity)
    # Check if the current time minus the last hit time is greater than the debounce delay
    current_time = time.monotonic()
    if midi_velocity > last_velocity and (midi_velocity - last_velocity) > velocity_threshold:
        if current_time - last_hit_time > debounce_delay:
            note_on = NoteOn((12 * octave), midi_velocity)
            midi.send(note_on, channel=midi_channel)

            # Send a NoteOn with velocity 0 to stop the note
            note_off = NoteOn((12 * octave), 0)
            midi.send(note_off, channel=midi_channel)
            print("SENT NOTE", midi_velocity)

            last_hit_time = current_time

    last_velocity = midi_velocity
    
    if midi_velocity2 > last_velocity2 and (midi_velocity2 - last_velocity2) > velocity_threshold:
        if current_time - last_hit_time2 > debounce_delay:
            note_on = NoteOn((12 * octave), midi_velocity2)
            midi.send(note_on, channel=midi_channel2)

            # Send a NoteOn with velocity 0 to stop the note
            note_off = NoteOn((12 * octave), 0)
            midi.send(note_off, channel=midi_channel2)
            print("SENT NOTE", midi_velocity2)

            last_hit_time = current_time

    last_velocity2 = midi_velocity2
    # Add a short delay to avoid excessive CPU usage
    time.sleep(0.01)

