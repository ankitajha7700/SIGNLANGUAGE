# main_gui.py
import tkinter as tk
from tkinter import ttk
import subprocess

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main GUI with Embedded Script Output")

        # Create a frame for embedding script output
        self.output_frame = ttk.Frame(self)
        self.output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a text widget to display the script output
        self.text_widget = tk.Text(self.output_frame, wrap=tk.WORD,height=10)
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Run the script and capture its output
        self.display_script_output()

    def display_script_output(self):
        # Run the output script and capture its output
        result = subprocess.run(["python", "./signlangugage.py"], capture_output=True, text=True)
        
        # Insert the output into the text widget
        self.text_widget.insert(tk.END, result.stdout)
        self.text_widget.insert(tk.END, result.stderr)

if __name__ == "__main__":
    app = App()
    app.mainloop()
