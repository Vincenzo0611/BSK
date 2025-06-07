import os
import tkinter as tk
import hashlib
from Crypto.Cipher import AES
from tkinter import filedialog
from Crypto.Util.Padding import unpad, pad
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from PyPDF2 import PdfReader, PdfWriter
import psutil

encryption = None

class MainApp:
    def __init__(self, master):
        self.path = ""
        self.master = master
        master.title("Główna aplikacja")
        master.geometry("400x310")

        self.usbs = self.get_usbs()

        if not self.usbs:
            self.usbs = ["Brak USB"]

        self.usb_var = tk.StringVar()
        self.usb_var.set(self.usbs[0])

        self.usb_key_status = self.is_usb_key()

        self.usb_key_status_text = tk.StringVar()
        if (self.usb_key_status):
            self.usb_key_status_text.set("✅ Wykryto klucz prywatny")
            self.private_key = self.get_usb_key()
        else:
            self.usb_key_status_text.set("❌ Nie wykryto klucza prywatnego na USB")

        self.list_usbs = tk.OptionMenu(master, self.usb_var, *self.usbs)
        self.list_usbs.pack(pady=10)

        self.usb_key_status_label = tk.Label(master, textvariable=self.usb_key_status_text)
        self.usb_key_status_label.pack(pady=5)

        self.choose_pdf_button = tk.Button(master, text="Wybierz plik PDF", command=self.choosePdfFile)
        self.choose_pdf_button.pack(pady=10)

        self.pathLabel= tk.Label(master, text="Wybrany plik: ")
        self.pathLabel.pack(pady=5)

        self.label = tk.Label(master, text="Wprowadź PIN:")
        self.label.pack(pady=5)

        self.pin_entry = tk.Entry(master, show="*", width=30)
        self.pin_entry.pack(pady=5)

        self.generate_button = tk.Button(master, text="Podpisz PDF", command=self.sign_pdf)
        self.generate_button.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)

        self.last_usb_state = self.usbs
        self.master.after(2000, self.usb_refresh)
        self.master.after(2000, self.usb_key_check)

    def decrypt_private_key(self):
        try:
            iv = self.private_key[:16]
            cipher_text = self.private_key[16:]
            hashed_pin = hashlib.sha256(self.pin_entry.get().encode()).digest()
            cipher = AES.new(hashed_pin, AES.MODE_CBC, iv)
            decrypted_private_key = RSA.import_key(unpad(cipher.decrypt(cipher_text), AES.block_size))
            return decrypted_private_key
        except Exception as e:
            tk.messagebox.showerror("Błąd", "Wprowadzono nieprawidłowy PIN")
            self.status_label.config(text="❌ Wystąpił błąd podczas deszyfrowania klucza prywatnego.")
    
    def hash_pdf(self):
        try:
            with open(self.path, "rb") as f:
                data = f.read()
            hash = SHA256.new(data)
            return hash
        except Exception as e:
            self.status_label.config(text="❌ Wystąpił błąd podczas hashowania pdfa")

    def sign_pdf(self):
        if self.path == "":
            tk.messagebox.showerror("Błąd", "Wybierz plik")
            self.status_label.config(text="❌ Niewybrano pliku pdf do podpisu")
            return
        self.status_label.config(text="⏳ PDF jest aktualnie podpisywany")
        hash = self.hash_pdf()
        decrypted_key = self.decrypt_private_key()
        try:
            signature = pkcs1_15.new(decrypted_key).sign(hash)
            signature_hex = signature.hex()
            reader = PdfReader(self.path)
            pdf_writer = PdfWriter()
            pdf_writer.append(self.path)
            metadata = reader.metadata
            metadata.update({
                "/Podpisano przez": "Użytkownik A",
                "/Podpis": signature_hex
            })
            pdf_writer.add_metadata(metadata)
            with open(self.path, "wb") as f:
                pdf_writer.write(f)
            self.status_label.config(text="✅ PDF został podpisany poprawnie")
        except Exception as e:
            print(e)
            self.status_label.config(text="❌ Wystąpił błąd podczas podpisywania pdfa")

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
            self.usb_key_status = self.is_usb_key()

            if (self.usb_key_status):
                self.usb_key_status_text.set("✅ Wykryto klucz prywatny")
            else:
                self.usb_key_status_text.set("❌ Nie wykryto klucza prywatnego na USB")

        self.master.after(2000, self.usb_refresh)

    def get_usb_key(self):
        usb_path = self.usb_var.get() + "private_key.enc"
        with open(usb_path, "rb") as f:
            key = f.read()
        return key

    def is_usb_key(self):
        usb_path = self.usb_var.get() + "private_key.enc"
        return os.path.isfile(usb_path)

    def usb_key_check(self):
        self.usb_key_status = self.is_usb_key()

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

class SecondApp:
    def __init__(self, master):
        self.path = ""
        self.key_path = ""
        self.master = master
        master.title("Główna aplikacja")
        master.geometry("400x310")
        self.choose_pdf_button = tk.Button(master, text="Wybierz plik PDF", command=self.choosePdfFile)
        self.choose_pdf_button.pack(pady=10)

        self.pathLabel= tk.Label(master, text="Wybrany plik: ")
        self.pathLabel.pack(pady=5)

        self.choose_key_button = tk.Button(master, text="Wybierz klucz publiczny", command=self.choose_public_key)
        self.choose_key_button.pack(pady=10)

        self.pathLabelKey= tk.Label(master, text="Wybrany klucz publiczny: ")
        self.pathLabelKey.pack(pady=5)

        self.generate_button = tk.Button(master, text="Zweryfikuj podpis PDFa", command=self.verify_pdf)
        self.generate_button.pack(pady=10)

        self.status_label = tk.Label(master, text="")
        self.status_label.pack(pady=10)
    
    def choosePdfFile(self):
        self.path = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=[("Pliki PDF", "*.pdf")])
        self.pathLabel.config(text="Wybrany plik: " + self.path)

    def choose_public_key(self):
        self.key_path = filedialog.askopenfilename(title="Wybierz plik PDF", filetypes=[("Klucze publiczne", "*.pem")])
        self.pathLabelKey.config(text="Wybrany klucz: " + self.key_path)

    def hash_pdf(self):
        try:
            with open(self.path, "rb") as f:
                data = f.read()
            hash = SHA256.new(data)
            return hash
        except Exception as e:
            self.status_label.config(text="❌ Wystąpił błąd podczas hashowania pdfa")

    def get_signature(self):
        try:
            pdf_reader = PdfReader(self.path)
            metadata = pdf_reader.metadata
            if "/Podpis" not in metadata:
                self.status_label.config(text="❌ PDF nie jest podpisany")
                return
            return bytes.fromhex(metadata["/Podpis"])
        except Exception as e:
            self.status_label.config(text="❌ Wystąpił błąd podczas pobierania podpisu z pdfa")
    
    def get_public_key(self):
        try:
            with open(self.key_path, "rb") as f:
                return RSA.import_key(f.read())
        except Exception as e:
            self.status_label.config(text="❌ Wystąpił problem z kluczem publicznym")
    
    def verify_pdf(self):
        if self.path == "" or self.key_path == "":
            tk.messagebox.showerror("Błąd", "Wybierz plik PDF oraz klucz publiczny")
            self.status_label.config(text="❌ Niewybrano pliku pdf lub klucza")
            return
        signature = self.get_signature()
        hash = self.hash_pdf()
        key = self.get_public_key()
        try:
            pkcs1_15.new(key).verify(hash, signature)
            self.status_label.config(text="✅ Podpis jest prawidłowy")
        except Exception as e:
            self.status_label.config(text="❌ Podpis jest nieprawidłowy")

if __name__ == "__main__":
    start = tk.Tk()
    start.title("Wybierz akcje")
    start.geometry("400x250")

    generate_button = tk.Button(start, text="Podpisz", command=choose_encrypt)
    generate_button.pack(pady=10)

    generate_button = tk.Button(start, text="Weryfikuj", command=choose_decrypt)
    generate_button.pack(pady=10)

    start.mainloop()

    if encryption is not None:
        root = tk.Tk()
        if(encryption):
            app = MainApp(root)
            root.mainloop()
        else:
            app = SecondApp(root)
        root.mainloop()