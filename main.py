from tkinter import *
from tkinter import messagebox
from random import choice, randint, shuffle
import pyperclip
DEFAULT_EMAIL = "@gmail.com"


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
#Password Generator Project
def generate_password():
	pw_entry.delete(0, END)
	letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
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
	entries = [website, username, password]

	if "" in entries:
		messagebox.showerror("Error", "Please enter all required fields")
		return

	is_ok =	messagebox.askokcancel("Password Manager",
		                    f"These are the details entered: \nEmail:{username}\nPassword:{password}\n "
		                    f"Is it ok to save?")
	if is_ok:
		if "" not in entries:

			with open("data.txt", "a") as file:
				file.write(f"{website}  |  {username}  |  {password}\n")

			web_entry.delete(0, END)
			e_u_entry.delete(0, END)
			pw_entry.delete(0, END)


# ---------------------------- UI SETUP ------------------------------- #
# Window Creation
window = Tk()
window.title("Password Manager")
window.minsize(300, 300)
window.config(bg="white", padx=50, pady=50)

# Lock Canvas Creation
canvas = Canvas(width=200, height=200, bg="white", highlightthickness=0)
lock_img = PhotoImage(file="logo.png")
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
web_entry.grid(row=1, column=1, columnspan=2, sticky=EW)

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

window.mainloop()
