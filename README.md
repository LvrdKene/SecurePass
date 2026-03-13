# Password Tools Web App

A simple web application for generating secure passwords and checking password strength, with a modern web interface.

## Features

- **Password Generator**: Create strong passwords with customizable length (8-50 characters)
- **Password Strength Checker**: Analyze passwords and get detailed feedback
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Clean, professional interface inspired by lab management systems


## Usage

- **Dashboard**: Overview of available tools
- **Generate Password**: Enter desired length and generate a secure password
- **Check Strength**: Enter a password to analyze its strength and get improvement suggestions

## Security Notes

- Passwords are generated client-side and not stored
- No user data is collected or stored
- For production, set the `SECRET_KEY` environment variable to a secure random value