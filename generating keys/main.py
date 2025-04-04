import tkinter as tk
from tkinter import filedialog, messagebox
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
import hashlib
import os


class KeyGenApp:
    def __init__(self, master):
        self.master = master
        master.title("Generator Kluczy RSA")
        master.geometry("400x250")

        self.label = tk.Label(master, text="Wprowadź PIN:")
        self.label.pack(pady=5)

        self.pin_entry = tk.Entry(master, show="*", width=30)
        self.pin_entry.pack(pady=5)

        self.label_n = tk.Label(master, text="Wprowadź nazwe pliku do zapisu:")
        self.label_n.pack(pady=5)

        self.name_entry = tk.Entry(master, width=30)
        self.name_entry.pack(pady=5)

        self.generate_button = tk.Button(master, text="Wygeneruj i Zapisz Klucze", command=self.generate_keys)
        self.generate_button.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

    def generate_keys(self):
        pin = self.pin_entry.get()
        name = self.name_entry.get()
        if not pin:
            messagebox.showerror("Błąd", "PIN nie może być pusty.")
            return

        if not name:
            messagebox.showerror("Błąd", "Nazwa nie może być pusta.")
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

            # Wybór folderu do zapisu
            #folder_selected = filedialog.askdirectory(title="Wybierz folder (np. pendrive)")
            #if not folder_selected:
            #    return

            with open(os.path.join("D:\\", name + "_private_key.enc"), "wb") as f:
                f.write(iv + encrypted_private_key)

            with open(os.path.join("C:\\key", name + "_public_key.pem"), "wb") as f:
                f.write(public_key)

            self.status_label.config(text="✅ Klucze zapisane poprawnie!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd: {str(e)}")
            self.status_label.config(text="❌ Wystąpił błąd.")


if __name__ == "__main__":
    root = tk.Tk()
    app = KeyGenApp(root)
    root.mainloop()
