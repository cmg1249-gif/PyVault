import time
import pyperclip
import encryption
import secrets
import string
import threading
import pwn_checker
import json
from cryptography.fernet import InvalidToken, Fernet
from requests import RequestException
from tkinter import *
from tkinter import messagebox, simpledialog
from pathlib import Path
from tkinter import filedialog
from encryption import DATA_FILE
MP_LENGTH_REQ = 12
VERSION: str = "2.0.0-beta.1"
DEFAULT_EMAIL: str = "@gmail.com"
LOGO_IMG_PATH = Path(__file__).parent / "logo_final_200.png"
popup = None

# ---------------------------- PASSWORD GENERATOR ------------------------------- #
# Password Generator Project
def generate_password() -> None:
	"""Generates a 13-character password, puts it in the entry, and copies it.

	Uses the secrets module rather than random so the output is suitable for
	real credentials. The clipboard is cleared automatically after 10 seconds.
	"""
	pw_entry.delete(0, END)

	password_letters: list = [letter for letter in string.ascii_letters]
	password_symbols: list = [letter for letter in string.punctuation]
	password_numbers = [letter for letter in string.digits]
	new_pw: list = (
		[secrets.choice(password_letters) for _ in range(7)]
		+ [secrets.choice(password_symbols) for _ in range(2)]
		+ [secrets.choice(password_numbers) for _ in range(4)]
	)

	def clear_clipboard(delay_seconds: int, pw_text: str) -> None:
		"""Waits, then clears the clipboard only if it still holds pw_text.

		The check means anything the user copied in the meantime is left alone.
		"""
		# Wait for default time of 10 seconds
		time.sleep(delay_seconds)
		if pyperclip.paste() == pw_text:
			pyperclip.copy('')

	def secure_copy(text: str, delay_seconds: int = 10) -> None:
		"""Copies text to the clipboard and schedules clear_clipboard() to wipe it."""
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
def save() -> None:
	"""Validates the form, warns on a breached password, then writes to the vault."""
	def search_for_match_wrapper() -> int:
		"""Returns how many times the password appears in known breaches.

		Returns 0 if the breach service cannot be reached, so a network
		problem never blocks saving.
		"""
		try:
			count = pwn_checker.search_for_match_count(password)
			return count
		except RequestException:
			return 0
		
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
		return


	if int(search_for_match_wrapper()) > 0:
		y_or_n = messagebox.askyesno(title="Password Found!", message="Password was found on an online database! Do you wish to use it anyway? Yes/No")
		if not y_or_n:
			return
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
		if website in data:
			y_or_n = messagebox.askyesno(title="Overwrite Warning",message="You already have an account saved for this website! Do you want to overwrite it with this new data?")
			if not y_or_n:
				messagebox.showinfo(title="Alert", message="Nothing Happened\nYour data new data was not saved,Your old data was not overwritten.")
				return
		# Updating Old Data with New Data
		data.update(new_data)
		encryption.save_data(data)
		messagebox.showinfo(title="Success!", message="Successfully saved new account data!")
		if popup is not None:
			on_close()
			find_all_accounts()
	finally:
		web_entry.delete(0, END)
		pw_entry.delete(0, END)
# ---------------------------- Delete Account Data ---------------------------------------- #
def delete(account: str) -> None:
	"""Removes one account from the vault by its website key."""
	data = encryption.load_data()
	data.pop(account, None)
	encryption.save_data(data)

# ---------------------------- Find Password --------------------------#
def find_password() -> None:
	"""Looks up the website in the entry field and shows its stored credentials."""
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
def find_all_accounts() -> None:
	"""Opens the All Accounts window listing every saved website and email.

	Rows show "website - email" only. Double-clicking a row reveals that
	account's password in a dialog; the Search button on the main window
	does the same thing by typed website name.
	"""

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
			# Two parallel structures, both in dict insertion order, so a
			# listbox row number indexes into either one:
			#   sites_and_user_name[i] -> the text the user sees in row i
			#   websites[i]            -> the vault key for row i
			# They MUST be kept in step. delete_selected() does this by
			# popping websites at the same index it deletes the row.
			sites_and_user_name = [f"{website} - {details['email']}" for website, details in data.items()]
			websites = list(data.keys())

			# Creating Popup Window
			def open_pop_up() -> None:
				"""Creates the All Accounts window, or raises it if already open."""
				global popup
				if popup is None:
					popup = Toplevel(window)
					popup.title("All Accounts")
					popup.minsize()
					popup.protocol("WM_DELETE_WINDOW", on_close)
					text_box = Listbox(popup, bg="white", fg="black", height=15, width=50)
					def double_click_listener(event) -> None:
						"""Reveals the credentials for the double-clicked row.

						Bound to <Double-Button-1> below, so Tk calls this with an
						Event; `event.y` is the click's pixel offset inside the
						listbox. Unlike delete_selected() (a Button command with no
						mouse info), this can resolve the row from the click itself.
						"""
						# Pixel -> row number. nearest() CLAMPS: a click in the blank
						# space under the last row returns the last row's index, so
						# the range check below is what stops a stray double-click in
						# dead space from revealing the bottom account.
						index = text_box.nearest(event.y)
						if index < 0 or index >= len(websites):
							return

						# Row number -> vault key -> credentials. data has no
						# positions to index by, so websites is what converts the
						# row number into a key. Use websites (not a fresh
						# list(data.keys())) - it is the copy delete_selected keeps
						# in step with the rows, so it stays correct after a delete.
						website = websites[index]
						email = data[website]["email"]
						password = data[website]["password"]

						messagebox.showinfo(title=f"{website}", message=f"Email :{email}\nPassword :{password} ")
					for row in sites_and_user_name:
						text_box.insert(END, row)
					text_box.bind("<Double-Button-1>", double_click_listener)
					text_box.grid(row=0, column=0)


					def delete_selected() -> None:
						"""Deletes the highlighted account after confirmation."""
						selection = text_box.curselection()
						if selection:
							index = selection[0]
							account = websites[index]
							y_or_n = messagebox.askyesno(title="Delete Selected Account?",
							                             message=f"Do you want to delete this account? {account}?",
							                             parent=popup)
							if y_or_n:
								delete(account)
								text_box.delete(index)
								websites.pop(index)

					delete_button = Button(popup, text="Delete Selected Account", bg="white", fg="black",
					                       command=delete_selected)
					delete_button.grid(row=0, column=1)
				else:
					popup.lift()
			# Text Box
			open_pop_up()

		except KeyError:
			messagebox.showinfo(title="Oops", message="Email entry corrupted")
# ---------------------------- UI SETUP ----------------------------- #
# Export/Import Key GUI file dialog building
def export_vault_wrapper() -> None:
	"""Asks where to save a vault backup, then copies the vault there.
	"""
	user_chosen_path = filedialog.asksaveasfilename(
		defaultextension=".enc",
		filetypes=[("Encrypted File", "*.enc"), ("All Files", "*.*")],
		initialfile="pyvault_vault_backup.enc",
	)
	if not user_chosen_path or user_chosen_path == "":
		return
	try:
		encryption.export_vault(user_chosen_path)
		messagebox.showinfo(title="Success!", message=f"Your file has been exported to: {user_chosen_path}!")
	except encryption.VaultNotFoundError:
		messagebox.showerror(title="Error", message="Vault Can't Be Found")



def import_vault_wrapper() -> None:
	user_chosen_path = filedialog.askopenfilename(
		defaultextension=".enc",
		filetypes=[("Encrypted File", "*.enc"), ("All Files", "*.*")],
		initialfile="pyvault_vault.enc",
	)
	if not user_chosen_path or user_chosen_path == "":
		return
	if DATA_FILE.is_file():
		y_or_n = messagebox.askyesno(title="Replacing Current Vault", message="Replace your current vault? (Your current vault will be backed up automatically first.)")
		if y_or_n is None or y_or_n is False:
			return
	while True:
		password = prompt_for_password()
		if password is None:
			return
		try:
			vault_string = Path(user_chosen_path).read_text()
			encryption.open_vault(password, vault_string)
		except InvalidToken:
			messagebox.showinfo(title="Error: Password", message="Incorrect Password")
			continue
		except ValueError:
			messagebox.showinfo(title="Error: Not A Vault", message="Not a valid v2 Vault")
			return
		break

	backup = encryption.import_vault(user_chosen_path)

	encryption.lock()
	encryption.unlock(password)
	if backup is None:
		messagebox.showinfo(title="Success!", message="Your new vault has been imported!")
	else:
		messagebox.showinfo(title="Success!", message=f"Your new vault has been imported and a backup of your previous vault is located at: {backup}!")
# Popup Management

def on_close() -> None:
	"""Destroys the All Accounts window and resets the flag so it can reopen."""
	global popup
	popup.destroy()
	popup = None
def prompt_for_password() -> str | None:
	"""Prompts the user once to enter a password for a vault."""
	password = simpledialog.askstring(
		title="Password",
		prompt="Please enter your Master Password to open the vault you are importing",
		show="*",
		parent=window
	)
	if password is None:
		return None
	return password

def prompt_new_master_pw() -> str | None:
	"""Prompts user twice for master password returns string or None"""
	answer_1 = simpledialog.askstring(
		title="No Vault File",
		prompt="Please enter your Master Password to build your new Vault",
		show="*",
		parent=window
	)
	answer_2 = simpledialog.askstring(
		title="No Vault File",
		prompt="Please enter your Master Password to build your new Vault",
		show="*",
		parent=window
	)
	if answer_1 is None or answer_2 is None:
		return None
	elif answer_1 != answer_2:
		return None
	elif (answer_1 == "") or (answer_2 == ""):
		return None
	elif len(answer_2) < MP_LENGTH_REQ:
		y_or_n = messagebox.askyesno(title="Invalid Password",
									 message="The password you entered is to short or invalid,try again?\nPasswords must be 12 characters long")
		if y_or_n is None or y_or_n is False:
			return None
		if y_or_n:
			return prompt_new_master_pw()
	else:
		return answer_2
# A Gated Startup
def start_up_gate() -> bool:
	"""To be filled in"""


	if not DATA_FILE.is_file():
			password = prompt_new_master_pw()
			serialized_json_string = encryption.create_vault(password, json.dumps({}))
			DATA_FILE.write_text(serialized_json_string, encoding="utf-8")
			encryption.unlock(password)
			return True
	elif  encryption.is_v1_vault():
		y_or_n = messagebox.askyesno(
			title="We've upgraded to v2!",
			message=(
				"PyVault now locks your vault with a master password, using stronger "
				"encryption (Argon2id) than the previous version.\n\n"
				"To upgrade, you'll choose a master password on the next screen. "
				"You'll enter it each time PyVault starts from now on, so pick "
				"something you won't forget — it cannot be recovered.\n\n"
				"Your current vault is copied to data.enc.bak in your PyVault_Vault "
				"folder before anything is changed.\n\n"
				"If you decline, PyVault will close: this version cannot open an "
				"old vault.\n\n"
				"Upgrade now?"
			),
		)
		if y_or_n is None or y_or_n is False:
			return False
		elif y_or_n:
			password = prompt_new_master_pw()
			encryption.migrate_v1_to_v2(password)
			encryption.unlock(password)
			return True
	else:
		password = simpledialog.askstring(
		title="Vault Locked",
		prompt="Please enter your Master Password to open your Vault",
		show="*",
		parent=window
	)
		if password is None:
			return False
		try:
			encryption.unlock(password)
			return True
		except encryption.IncorrectPasswordError:
			start_up_gate()

# Window Creation
window = Tk()

window.title(f"PyVault: Password Manager v{VERSION}")
window.minsize(300, 300)
window.config(bg="white", padx=50, pady=50)

# Lock Canvas Creation
canvas = Canvas(width=200, height=200, bg="white", highlightthickness=0)
lock_img = PhotoImage(file=LOGO_IMG_PATH)
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

add_button = Button(width=36, text="Save", bg="white", fg="black", command=save)
add_button.grid(row=4, column=1, columnspan=2, sticky=EW)

search_button = Button(text="Search", bg="white", fg="black", command=find_password)
search_button.grid(row=1, column=2, sticky=EW)

all_accounts_button = Button(width=16, text="All Accounts", bg="white", fg="black", command=find_all_accounts)
all_accounts_button.grid(row=5, column=1, columnspan=2,sticky=EW)

# File Menu Creation
menu_bar = Menu(window)                                      # Parent: window
sub_menu = Menu(menu_bar, tearoff=0)                         # Parent: menu_bar
sub_menu.add_command(label="Export Vault", command=export_vault_wrapper)  # Creating Export Vault button
sub_menu.add_command(label="Import Vault", command=import_vault_wrapper)  # Creating Import Vault button
sub_menu.add_command(label="Exit", command=window.destroy)                  # Command and label for exit
menu_bar.add_cascade(label="Options", menu=sub_menu)			 # Make a cascading menu
window.config(menu=menu_bar)								 # put the menu_bar together on the window

start_up_gate()
window.mainloop()
