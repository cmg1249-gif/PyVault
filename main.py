from tkinter import *
from tkinter import messagebox
import time
import pyperclip
from cryptography.fernet import InvalidToken
import encryption
import secrets
import string
import threading

VERSION = "1.4.0"
DEFAULT_EMAIL = "@gmail.com"


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
# Password Generator Project
def generate_password():
	pw_entry.delete(0, END)

	password_letters: list = [letter for letter in string.ascii_letters]
	password_symbols: list = [letter for letter in string.punctuation]
	password_numbers: list = [letter for letter in string.digits]
	new_pw: list = (
		[secrets.choice(password_letters) for _ in range(7)]
		+ [secrets.choice(password_symbols) for _ in range(2)]
		+ [secrets.choice(password_numbers) for _ in range(4)]
	)

	def clear_clipboard(delay_seconds, pw_text):
		"""Clears the clipboard"""
		# Wait for default time of 10 seconds
		time.sleep(delay_seconds)
		if pyperclip.paste() == pw_text:
			pyperclip.copy('')

	def secure_copy(text, delay_seconds=10):
		"""Copy text securely to the clipboard, then uses clear_clipboard() it after 10 seconds"""
		pyperclip.copy(text)

		# Opening another thread to clear the clipboard
		t = threading.Thread(target=clear_clipboard, args=(delay_seconds, pyperclip.paste()))
		t.daemon = True
		t.start()

	def secure_shuffle(items: list) -> None:
		"""Shuffle a list in place using cryptographically secure random order.(I found this on the internet, I did not figure this one out on my own :)"""
		for i in range(len(items) - 1, 0, -1):
			j = secrets.randbelow(i + 1)
			items[i], items[j] = items[j], items[i]

	secure_shuffle(new_pw)
	new_pw = "".join(new_pw)
	pw_entry.insert(0, new_pw)
	secure_copy(new_pw)

# ---------------------------- SAVE PASSWORD ------------------------------- #
def save():
	website = web_entry.get()
	username = e_u_entry.get()
	password = pw_entry.get()
	new_data = {website: {
		"email": username,
		"password": password,

	}

	}
	if len(website) == 0 or len(password) == 0:
		messagebox.showerror("Oops!", "Please enter all fields")
	else:
		try:
			# Read Old Data
			data = encryption.load_data()
		except FileNotFoundError:
			encryption.save_data(new_data)
			messagebox.showinfo("WARNING", "Do not delete your key's in your OS's key manager. Your data will be lost!")
		except InvalidToken:
			delete_y_n = messagebox.askyesno(title="Vault Can't Be Unlocked",
			                                 message="Key's do not match. Delete vault and start fresh? THIS ERASES ALL SAVED PASSWORDS!")
			if delete_y_n:
				encryption.delete_vault()
		else:
			# Updating Old Data with New Data
			data.update(new_data)
			encryption.save_data(data)
		finally:
			web_entry.delete(0, END)
			pw_entry.delete(0, END)
# ---------------------------- Delete Account Data ---------------------------------------- #
def delete(account):
	data = encryption.load_data()
	data.pop(account, None)
	encryption.save_data(data)

# ---------------------------- Find Password --------------------------#
def find_password():
	website = web_entry.get()
	try:
		data = encryption.load_data()
	except FileNotFoundError:
		messagebox.showinfo("Oops!", "File info not found!")
	except InvalidToken:
		delete_y_n = messagebox.askyesno(title="Vault Can't Be Unlocked",
		                                 message="Keys do not match. Delete vault and start fresh? THIS ERASES ALL SAVED PASSWORDS!")
		if delete_y_n:
			encryption.delete_vault()

	else:
		try:
			site = data[website]
			email = site["email"]
			password = site["password"]
			messagebox.showinfo(title=f"Data Found for {website}!", message=f"Email :{email}\nPassword : {password}")
		except KeyError:
			messagebox.showinfo(title="Oops", message="Account info not found!")

#---------------------- All accounts --------------------------#
def find_all_accounts():
	try:
		data = encryption.load_data()
	except FileNotFoundError:
		messagebox.showinfo("Oops!", "File info not found!")
	except InvalidToken:
		delete_y_n = messagebox.askyesno(title="Vault Can't Be Unlocked",
		                                 message="Keys do not match. Delete vault and start fresh? THIS ERASES ALL SAVED PASSWORDS!")
		if delete_y_n:
			encryption.delete_vault()
	else:
		try:
			sites_and_user_name = [f"{website} - {details['email']}" for website, details in data.items()]
			websites = list(data.keys())

			# Creating Popup Window
			popup = Toplevel()
			popup.title("All Accounts")
			popup.minsize()
			# Text Box
			text_box = Listbox(popup, bg="white", fg="black", height=15, width=50)
			for row in sites_and_user_name:
				text_box.insert(END, row)

			text_box.grid(row=0, column=0)

			def delete_selected():
				selection = text_box.curselection()
				if selection:
					index = selection[0]
					account = websites[index]
					y_or_n =messagebox.askyesno(title="Delete Selected Account?",message=f"Do you want to delete this account? {account}?", parent=popup)
					if y_or_n:
						delete(account)
						text_box.delete(index)
						websites.pop(index)
			delete_button = Button(popup, text="Delete Selected Account", bg="white", fg="black", command=delete_selected)
			delete_button.grid(row=0, column=1)
		except KeyError:
			messagebox.showinfo(title="Oops", message="Email entry corrupted")

# ---------------------------- UI SETUP ----------------------------- #
# Encrypt json data if its there and remove json file
encryption.migrate()
# Window Creation
window = Tk()
window.title(f"PyVault: Password Manager v{VERSION}")
window.minsize(300, 300)
window.config(bg="white", padx=50, pady=50)

# Lock Canvas Creation
canvas = Canvas(width=200, height=200, bg="white", highlightthickness=0)
lock_img = PhotoImage(file="logo_final_200.png")
canvas.create_image(100, 100, image=lock_img)
canvas.grid(row=0, column=1)

# Label Creation
website_label = Label(text="Website:", bg="white", fg="black")
website_label.grid(row=1, column=0)

e_u_label = Label(text="Email/Username:", bg="white", fg="black")
e_u_label.grid(row=2, column=0)

password_label = Label(text="Password:", bg="white", fg="black")
password_label.grid(row=3, column=0)

# Entry Creation
web_entry = Entry(width=35, bg="white", fg="black")
web_entry.grid(row=1, column=1, sticky=EW)

e_u_entry = Entry(width=35, bg="white", fg="black")
e_u_entry.grid(row=2, column=1, columnspan=2, sticky=EW)
e_u_entry.insert(0, DEFAULT_EMAIL)

pw_entry = Entry(width=21, bg="white", fg="black")
pw_entry.grid(row=3, column=1, sticky=EW)

# Button Creation

generate_button = Button(text="Generate Password", bg="white", fg="black", command=generate_password)
generate_button.grid(row=3, column=2)

add_button = Button(width=36, text="Add", bg="white", fg="black", command=save)
add_button.grid(row=4, column=1, columnspan=2, sticky=EW)

search_button = Button(text="Search", bg="white", fg="black", command=find_password)
search_button.grid(row=1, column=2, sticky=EW)

all_accounts_button = Button(width=16, text="All Accounts", bg="white", fg="black", command=find_all_accounts)
all_accounts_button.grid(row=5, column=1, columnspan=2,sticky=EW)

window.mainloop()
