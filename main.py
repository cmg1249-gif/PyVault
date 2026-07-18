from tkinter import *
from tkinter import messagebox
from random import choice, randint, shuffle
import pyperclip
from cryptography.fernet import InvalidToken
import encryption

VERSION = "1.2.0"
DEFAULT_EMAIL = "@gmail.com"


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
# Password Generator Project
def generate_password():
	pw_entry.delete(0, END)
	letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
	           'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
	           'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
	numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
	symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

	password_letters = [choice(letters) for _ in range(randint(8, 10))]
	password_symbols = [choice(symbols) for _ in range(randint(2, 4))]
	password_numbers = [choice(numbers) for _ in range(randint(2, 4))]

	password_list = password_letters + password_symbols + password_numbers
	shuffle(password_list)

	password = "".join(password_list)
	pw_entry.insert(0, password)
	pyperclip.copy(password)


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
			sites_and_user_name = [f"Website: {website}\nUsername:{details['email']}\n" for website, details in data.items()]
			sites_and_user_name = "\n -------------------------------- \n".join(sites_and_user_name)
			# Creating Popup Window
			popup = Toplevel()
			popup.title("All Accounts")
			popup.minsize()
			# Text Box
			text_box = Text(popup, bg="white", fg="black")
			text_box.insert(END, sites_and_user_name)
			text_box.grid(row=0, column=0)
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