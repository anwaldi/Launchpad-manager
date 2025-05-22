import mido
import tkinter as tk
from tkinter import messagebox, Menu, Toplevel, Label
import threading

app = tk.Tk()
app.title("LaunchpadManager")
app.geometry("600x600")

buttons = []
selected_device_name = None  # Merkt sich das aktuell gewählte Gerät
device_menu = None
listener_thread = None
stop_listener = threading.Event()


# --- GUI: 8x8 Button-Grid ---
for row in range(8):
    row_buttons = []
    for col in range(8):
        def on_button_click(r=row, c=col):
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


# --- MIDI Listener Thread ---
def midi_listener(device_name):
    try:
        with mido.open_input(device_name) as inport:
            for msg in inport:
                if stop_listener.is_set():
                    break
                if msg.type == 'note_on':
                    note = msg.note
                    velocity = msg.velocity
                    if 0 <= note <= 63:
                        row = note // 8
                        col = note % 8
                        color = 'yellow' if velocity > 0 else 'lightgrey'
                        app.after(0, update_button_color, row, col, color)
    except IOError:
        app.after(0, lambda: messagebox.showerror("Fehler", f"Kann Gerät nicht öffnen: {device_name}"))


def start_midi_listener(device_name):
    global listener_thread, stop_listener
    stop_midi_listener()  # Stoppe vorherigen Listener
    stop_listener.clear()
    listener_thread = threading.Thread(target=midi_listener, args=(device_name,), daemon=True)
    listener_thread.start()


def stop_midi_listener():
    global stop_listener
    stop_listener.set()


# --- Menü: MIDI Devices ---
def select_midi_device(device_name):
    global selected_device_name
    selected_device_name = device_name
    update_device_menu()
    start_midi_listener(device_name)


def refresh_midi_devices():
    midi_devices = mido.get_input_names()
    device_menu.delete(0, 'end')
    for device in midi_devices:
        device_menu.add_radiobutton(label=device, variable=tk.StringVar(value=selected_device_name),
                                    value=device, command=lambda d=device: select_midi_device(d))


def update_device_menu():
    refresh_midi_devices()


# --- Menü Setup ---
menubar = Menu(app)
setup_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Setup", menu=setup_menu)

device_menu = Menu(setup_menu, tearoff=0)
setup_menu.add_cascade(label="MIDI Devices", menu=device_menu)


def on_setup_open():
    update_device_menu()


setup_menu.bind("<<MenuSelect>>", lambda e: on_setup_open())

app.config(menu=menubar)

# App Start: Automatisch erstes Launchpad auswählen (optional)
def auto_select_first_launchpad():
    global selected_device_name
    devices = mido.get_input_names()
    for device in devices:
        if "Launchpad" in device:
            selected_device_name = device
            start_midi_listener(device)
            break

auto_select_first_launchpad()

# Start GUI
app.mainloop()

# Bei Beenden sicher stoppen
stop_midi_listener()
