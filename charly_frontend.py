import tkinter as tk
from tkinter import scrolledtext, Button, filedialog
from charly_backend import *

class CharlyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Charly AI")
        self.root.geometry("600x400")

        # GUI components setup (same as original)
        self.conversation_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled")
        self.input_field = tk.Entry(root)
        self.media_buttons_frame = tk.Frame(root)
        self.data_science_frame = tk.Frame(root)

        # Component layout and configuration
        # ... [Keep all GUI layout code from original] ...

        # Initial message
        self.display_message("Charly: Hello Sir! How can I assist you today?")
        speak("Hello Sir! How can I assist you today?")
        logging.info("Session started.")

    def display_message(self, message):
        self.conversation_area.config(state="normal")
        self.conversation_area.insert(tk.END, message + "\n")
        self.conversation_area.config(state="disabled")
        self.conversation_area.yview(tk.END)

    def process_input(self, event=None):
        user_input = self.input_field.get().strip()
        self.input_field.delete(0, tk.END)

        if user_input.lower() in ["exit", "quit", "bye"]:
            self.shutdown()
            return

        logging.info(f"User: {user_input}")
        response = handle_command(user_input) or chatbot(
            user_input, max_length=100, num_return_sequences=1, truncation=True
        )[0]['generated_text']
        
        self.display_message(f"Charly: {response}")
        speak(response)
        logging.info(f"Charly: {response}")

    def shutdown(self):
        self.display_message("Charly: Goodbye Sir! Thank you for using me.")
        speak("Goodbye Sir! Thank you for using me.")
        logging.info("Session ended.")
        self.root.quit()

    # Media control methods
    def play_media(self):
        if playlist:
            self.process_input(f"play media {playlist[current_track]}")
        else:
            self.display_message("Charly: Playlist is empty, Sir.")

    # ... [Keep other media control methods from original] ...

    # Data science methods
    def load_dataset(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            self.process_input(f"load dataset {file_path}")

    # ... [Keep other data science methods from original] ...

def main():
    root = tk.Tk()
    app = CharlyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()