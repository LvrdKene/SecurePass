from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import os
import random
import string
import re
import secrets

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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORDLIST_PATH = os.path.join(BASE_DIR, "wordlist.txt")


def _load_wordlist() -> list[str]:
    try:
        with open(WORDLIST_PATH, "r", encoding="utf-8") as handle:
            words = [line.strip().lower() for line in handle if line.strip()]
        words = [w for w in words if w.isalpha()]
        return words
    except OSError:
        return ["anchor", "forest", "ember", "river"]


WORDLIST = _load_wordlist()


def generate_pin(length: int) -> str:
    return "".join(secrets.choice(string.digits) for _ in range(length))


def _random_word(min_len: int = 4, max_len: int = 8) -> str:
    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"
    length = secrets.choice(range(min_len, max_len + 1))
    chars = []
    use_consonant = True
    for _ in range(length):
        if use_consonant:
            chars.append(secrets.choice(consonants))
        else:
            chars.append(secrets.choice(vowels))
        use_consonant = not use_consonant
    return "".join(chars)


def generate_passphrase(word_count: int, separator: str) -> str:
    words = [secrets.choice(WORDLIST) for _ in range(word_count)]
    return separator.join(words)


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


@app.route('/generate', methods=['GET'])
def generate():
    generated_password = None
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


@app.route('/api/password', methods=['POST'])
def api_password():
    data = request.get_json(silent=True) or {}
    try:
        length = int(data.get('length', 16))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid length"}), 400
    if length < 8 or length > 50:
        return jsonify({"error": "Length must be between 8 and 50"}), 400
    return jsonify({"password": generate_password(length), "length": length})


@app.route('/api/pin', methods=['POST'])
def api_pin():
    data = request.get_json(silent=True) or {}
    try:
        length = int(data.get('length', 6))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid length"}), 400
    if length < 4 or length > 12:
        return jsonify({"error": "Length must be between 4 and 12"}), 400
    return jsonify({"pin": generate_pin(length), "length": length})


@app.route('/api/passphrase', methods=['POST'])
def api_passphrase():
    data = request.get_json(silent=True) or {}
    try:
        count = int(data.get('words', 4))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid word count"}), 400
    if count < 3 or count > 8:
        return jsonify({"error": "Word count must be between 3 and 8"}), 400
    separator = data.get('separator', '-')
    if not isinstance(separator, str):
        separator = '-'
    return jsonify({"passphrase": generate_passphrase(count, separator), "words": count})


if __name__ == '__main__':
    app.run(debug=False)
