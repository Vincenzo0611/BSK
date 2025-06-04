import os
import tkinter as tk
from tkinter import filedialog

import psutil

encryption = None

class MainApp:
    def __init__(self, master):
        self.path = ""
        self.master = master
        master.title("Główna aplikacja")
        master.geometry("400x250")

        self.usbs = self.get_usbs()

        if not self.usbs:
            self.usbs = ["Brak USB"]

        self.usb_var = tk.StringVar()
        self.usb_var.set(self.usbs[0])

        self.usb_key_status = self.usb_get_key()

        self.usb_key_status_text = tk.StringVar()
        if (self.usb_key_status):
            self.usb_key_status_text.set("✅ Wykryto klucz prywatny")
        else:
            self.usb_key_status_text.set("❌ Nie wykryto klucza prywatnego na USB")

        self.list_usbs = tk.OptionMenu(master, self.usb_var, *self.usbs)
        self.list_usbs.pack(pady=10)

        self.usb_key_status_label = tk.Label(master, textvariable=self.usb_key_status_text)
        self.usb_key_status_label.pack(pady=5)

        self.generate_button = tk.Button(master, text="Wybierz plik PDF", command=self.choosePdfFile)
        self.generate_button.pack(pady=10)

        self.pathLabel= tk.Label(master, text="Wybrany plik: ")
        self.pathLabel.pack(pady=5)

        self.last_usb_state = self.usbs
        self.master.after(2000, self.usb_refresh)
        self.master.after(2000, self.usb_key_check)

    def choosePdfFile(self):
        self.path = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=[("Pliki PDF", "*.pdf")])
        self.pathLabel.config(text="Wybrany plik: " + self.path)
    def get_usbs(self):
        result = []
        partitions = psutil.disk_partitions()
        for p in partitions:
            if "removable" in p.opts:
                result.append(p.device)
        return result

    def usb_refresh(self):
        current = self.get_usbs()

        if not current:
            current = ["Brak USB"]

        if current != self.last_usb_state:
            self.usbs = current
            self.last_usb_state = current
            self.usb_var.set(self.usbs[0])

            menu = self.list_usbs["menu"]
            menu.delete(0, "end")
            for u in self.usbs:
                menu.add_command(label=u, command=lambda value=u: self.usb_var.set(value))
            self.usb_key_status = self.usb_get_key()

            if (self.usb_key_status):
                self.usb_key_status_text.set("✅ Wykryto klucz prywatny")
            else:
                self.usb_key_status_text.set("❌ Nie wykryto klucza prywatnego na USB")

        self.master.after(2000, self.usb_refresh)

    def usb_get_key(self):
        usb_path = self.usb_var.get() + "private_key.enc"
        return os.path.isfile(usb_path)

    def usb_key_check(self):
        self.usb_key_status = self.usb_get_key()

        if (self.usb_key_status):
            self.usb_key_status_text.set("✅ Wykryto klucz prywatny")
        else:
            self.usb_key_status_text.set("❌ Nie wykryto klucza prywatnego na USB")
        self.master.after(2000, self.usb_key_check)

def choose_encrypt():
    global encryption
    encryption = True
    start.destroy()


def choose_decrypt():
    global encryption
    encryption = False
    start.destroy()

if __name__ == "__main__":
    start = tk.Tk()
    start.title("Wybierz akcje")
    start.geometry("400x250")

    generate_button = tk.Button(start, text="Szyfruj", command=choose_encrypt)
    generate_button.pack(pady=10)

    generate_button = tk.Button(start, text="Deszyfruj", command=choose_decrypt)
    generate_button.pack(pady=10)

    start.mainloop()

    if encryption is not None:
        root = tk.Tk()
        if(encryption):
            app = MainApp(root)
            root.mainloop()
        else:
            root = tk.Tk()
            app = SecondApp(root)
        root.mainloop()