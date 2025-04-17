import os
import hashlib
from functools import wraps
from flask import session, redirect, url_for, flash

# В реальном проекте эти значения должны храниться в БД с хешированными паролями
# Для демонстрации используем простую переменную
ADMIN_CREDENTIALS = {
    'admin': '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'  # sha256 хеш для 'admin'
}

def hash_password(password):
    """Создает SHA-256 хеш пароля."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(username, password):
    """Проверяет правильность логина и пароля."""
    if username not in ADMIN_CREDENTIALS:
        return False
    
    hashed_password = hash_password(password)
    return ADMIN_CREDENTIALS[username] == hashed_password

def login_admin(username):
    """Устанавливает сессию для авторизованного администратора."""
    session['admin_logged_in'] = True
    session['admin_username'] = username

def logout_admin():
    """Разлогинивает администратора."""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)

def is_admin_logged_in():
    """Проверяет, авторизован ли администратор."""
    return session.get('admin_logged_in', False)

def admin_required(f):
    """Декоратор для проверки авторизации администратора."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            flash('Для доступа к этой странице необходимо авторизоваться', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function 