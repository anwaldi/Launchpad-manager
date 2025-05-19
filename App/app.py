import mido
import tkinter as tk
from tkinter import messagebox, Menu, Toplevel, Label
import threading

app = tk.Tk()
app.title("LaunchpadManager")
app.geometry("600x600")

buttons = []

for row in range(8):
    row_buttons = []
    for col in range(8):
        def on_button_click(r=row, c=col):
            # Neues Fenster öffnen, wenn Button gedrückt wird
            win = Toplevel(app)
            win.title(f"Button {r},{c} Info")
            win.geometry("200x100")
            Label(win, text=f"Du hast Button ({r},{c}) gedrückt").pack(pady=20)

        btn = tk.Button(app, width=6, height=3, bg='lightgrey', command=on_button_click)
        btn.grid(row=row, column=col, padx=2, pady=2)
        row_buttons.append(btn)
    buttons.append(row_buttons)

def update_button_color(row, col, color):
    buttons[row][col].config(bg=color)

def midi_listener():
    input_name = next((n for n in mido.get_input_names() if "Launchpad" in n), None)
    if not input_name:
        app.after(0, lambda: messagebox.showerror("Eroor", "No MIDI Device found!"))
        return

    with mido.open_input(input_name) as inport:
        for msg in inport:
            if msg.type == 'note_on':
                note = msg.note
                velocity = msg.velocity
                if 0 <= note <= 63:
                    row = note // 8
                    col = note % 8
                    color = 'green' if velocity > 0 else 'grey'
                    app.after(0, update_button_color, row, col, color)

def refresh_midi_devices():
    midi_devices = mido.get_input_names()
    device_menu.delete(0, 'end')
    for device in midi_devices:
        device_menu.add_command(label=device)

menubar = Menu(app)
setup_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Setup", menu=setup_menu)

device_menu = Menu(setup_menu, tearoff=0)
setup_menu.add_cascade(label="MIDI Devices", menu=device_menu)

# Beim Öffnen des Dropdown-Menüs die aktuellen MIDI-Devices laden
def on_setup_open():
    refresh_midi_devices()

setup_menu.bind("<<MenuSelect>>", lambda e: on_setup_open())

app.config(menu=menubar)

threading.Thread(target=midi_listener, daemon=True).start()

app.mainloop()