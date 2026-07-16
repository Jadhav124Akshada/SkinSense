import re

# Validate Email
def email_valid(email):
    reg = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    pat = re.compile(reg)
    mat = re.match(pat, email)
    if mat:
        return True
    else:
        return False

# Validate Name
def name_valid(name):
    if name.isalpha() and len(name) > 1:
        return True
    else:
        return False

# Validate Password
def password_valid(pass1):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    mat = re.search(pat, pass1)
    if mat:
        return True
    else:
        return False

# Check if Passwords Match
def password_check(password1, password2):
    if password1 == password2:
        return True
    else:
        return False

# Authentication Function
def authentication(username, pass1, pass2):
    if not email_valid(username):  # Validate email as username
        return "Invalid Username (must be a valid email address)"
    elif not password_valid(pass1):  # Validate password
        return "Password should be in proper format (e.g., Password@1234)"
    elif not password_check(pass1, pass2):  # Check if passwords match
        return "Passwords do not match"
    else:
        return "success"
