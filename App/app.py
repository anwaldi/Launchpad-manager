import tkinter as tk
from tkinter import messagebox

def say_hello():
    messagebox.showinfo("Info", "Hallo, Windows!")

app = tk.Tk()
app.title("LaunchpadManager")
app.geometry("1000x500")

button = tk.Button(app, text="Klick mich", command=say_hello)
button.pack(pady=50)

app.mainloop()