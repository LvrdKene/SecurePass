from flask import Flask, render_template, request, flash, redirect, url_for
import os
import random
import string
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-fallback-key")


# Import functions from existing files
SPECIAL_CHARS = "!@#$%^&*(),.?\":{}|<>"


def generate_password(length):
    # Character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Ensure at least one character from each category
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(symbols)
    ]

    # Fill the rest with random characters from all categories
    allChar = lowercase + uppercase + digits + symbols
    for i in range(length - 4):
        password.append(random.choice(allChar))

    # Shuffle the password to randomize the order
    random.shuffle(password)

    # Convert list back to string
    return ''.join(password)


def check_password_strength(password: str) -> tuple[int, list[str]]:
    """Return (score, issues).

    Score is between 0 and 6. Higher is better.
    issues is a list of strings explaining what's missing.
    """

    score = 0
    issues: list[str] = []

    if len(password) < 8:
        issues.append("Password is too short (minimum 8 characters)")
    else:
        score += 2

    if re.search(r"[a-z]", password):
        score += 1
    else:
        issues.append("Add at least one lowercase letter (a-z)")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        issues.append("Add at least one uppercase letter (A-Z)")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        issues.append("Add at least one number (0-9)")

    if re.search(fr"[{re.escape(SPECIAL_CHARS)}]", password):
        score += 1
    else:
        issues.append("Add at least one special character (e.g. !@#$%^&*())")

    return score, issues


def _strength_label(score: int) -> str:
    if score <= 2:
        return "VERY WEAK"
    if score <= 4:
        return "WEAK"
    if score == 5:
        return "MEDIUM"
    return "STRONG"




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    generated_password = None
    if request.method == 'POST':
        try:
            length = int(request.form['length'])
            if length < 8:
                flash('Password length must be at least 8 characters.', 'warning')
            elif length > 50:
                flash('Password length must be at most 50 characters.', 'warning')
            else:
                generated_password = generate_password(length)
                flash('Password generated successfully!', 'success')
        except ValueError:
            flash('Please enter a valid number for length.', 'danger')
    return render_template('generate.html', generated_password=generated_password)


@app.route('/check', methods=['GET', 'POST'])
def check():
    score = None
    issues = None
    strength = None
    password = None
    if request.method == 'POST':
        password = request.form['password']
        if not password:
            flash('Please enter a password to check.', 'warning')
        else:
            score, issues = check_password_strength(password)
            strength = _strength_label(score)
            if not issues:
                flash('Password strength checked successfully!', 'success')
    return render_template('check.html', score=score, issues=issues, strength=strength, password=password)


if __name__ == '__main__':
    app.run(debug=False)
