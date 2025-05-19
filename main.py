import mido
from mido import Message

page = 1  # Startseite

# Seitenumschalter-Tasten (z. B. ganz rechts: Note 89 & 99)
PAGE_NEXT = 89
PAGE_PREV = 99
MAX_PAGE = 2
MIN_PAGE = 1

# Mapping: (Seite, Launchpad Note) → Virtuelle Note für dot2
PAGE_MAP = {
    (1, 11): 60,
    (1, 12): 61,
    (2, 11): 70,
    (2, 12): 71,
}

# MIDI-Eingang (Launchpad)
input_name = next((n for n in mido.get_input_names() if "Launchpad" in n), None)

# MIDI-Ausgang (virtuell z. B. via loopMIDI)
output_name = next((n for n in mido.get_output_names() if "loopMIDI" in n or "virtual" in n), None)

if not input_name or not output_name:
    print("MIDI-Ports nicht gefunden.")
    exit()

with mido.open_input(input_name) as inport, mido.open_output(output_name) as outport:
    print(f"Aktiv: Seite {page}")
    for msg in inport:
        if msg.type == 'note_on' and msg.velocity > 0:
            note = msg.note

            if note == PAGE_NEXT:
                page = min(page + 1, MAX_PAGE)
                print(f"Wechsle zu Seite {page}")
                continue
            elif note == PAGE_PREV:
                page = max(page - 1, MIN_PAGE)
                print(f"Wechsle zu Seite {page}")
                continue

            mapped_note = PAGE_MAP.get((page, note))
            if mapped_note:
                outport.send(Message('note_on', note=mapped_note, velocity=msg.velocity))
                print(f"Seite {page} | Launchpad Note {note} → MIDI {mapped_note}")
