import hashlib
import os
import tkinter as tk

from tkinter import messagebox
import psutil

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


class KeyGenApp:
    def __init__(self, master):
        self.master = master
        master.title("Generator Kluczy RSA")
        master.geometry("400x250")

        self.label = tk.Label(master, text="Wybierz USB")

        self.usbs = self.get_usbs()

        if not self.usbs:
            self.usbs = ["Brak USB"]

        self.usb_var = tk.StringVar()
        self.usb_var.set(self.usbs[0])

        self.list_usbs = tk.OptionMenu(master, self.usb_var, *self.usbs)
        self.list_usbs.pack(pady=10)

        self.label = tk.Label(master, text="Wprowadź PIN:")
        self.label.pack(pady=5)

        self.pin_entry = tk.Entry(master, show="*", width=30)
        self.pin_entry.pack(pady=5)

        self.generate_button = tk.Button(master, text="Wygeneruj i Zapisz Klucze", command=self.generate_keys)
        self.generate_button.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

        self.last_usb_state = self.usbs
        self.master.after(2000, self.usb_refresh)

    def generate_keys(self):
        pin = self.pin_entry.get()
        usb_path = self.usb_var.get()
        if not pin:
            tk.messagebox.showerror("Błąd", "PIN nie może być pusty.")
            return

        self.status_label.config(text="⏳ Trwa generowanie kluczy RSA...")
        self.master.update()
        try:
            # Generowanie kluczy
            key = RSA.generate(4096)
            private_key = key.export_key()
            public_key = key.publickey().export_key()

            # Hashowanie PIN-u
            hashed_pin = hashlib.sha256(pin.encode()).digest()

            # Szyfrowanie klucza prywatnego AES-256
            iv = get_random_bytes(16)
            cipher = AES.new(hashed_pin, AES.MODE_CBC, iv)
            encrypted_private_key = cipher.encrypt(pad(private_key, AES.block_size))


            with open(os.path.join(usb_path, "private_key.enc"), "wb") as f:
                f.write(iv + encrypted_private_key)

            with open(os.path.join("C:\\key", "public_key.pem"), "wb") as f:
                f.write(public_key)

            self.status_label.config(text="✅ Klucze zapisane poprawnie!")
        except Exception as e:
            tk.messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")
            self.status_label.config(text="❌ Wystąpił błąd.")
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
        self.master.after(2000, self.usb_refresh)



if __name__ == "__main__":
    root = tk.Tk()
    app = KeyGenApp(root)
    root.mainloop()
