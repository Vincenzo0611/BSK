import tkinter as tk
from tkinter import filedialog

class MainApp:
    def __init__(self, master):
        self.path = ""
        self.master = master
        master.title("Główna aplikacja")
        master.geometry("400x250")

        self.generate_button = tk.Button(master, text="Wybierz plik PDF", command=self.choosePdfFile)
        self.generate_button.pack(pady=10)

        self.pathLabel= tk.Label(master, text="Wybrany plik: ")
        self.pathLabel.pack(pady=5)
    def choosePdfFile(self):
        self.path = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=[("Pliki PDF", "*.pdf")])
        self.pathLabel.config(text="Wybrany plik: " + self.path)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
