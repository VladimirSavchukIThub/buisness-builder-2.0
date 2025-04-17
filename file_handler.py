import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """
    Проверяет, допустимо ли расширение файла.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder='uploads'):
    """
    Сохраняет загруженный файл с уникальным именем.
    Возвращает относительный путь к файлу.
    """
    if file and allowed_file(file.filename):
        # Создаем уникальное имя файла
        filename = secure_filename(file.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        
        # Создаем директорию для хранения файлов, если она не существует
        upload_folder = os.path.join('static', folder)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Полный путь для сохранения файла
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Сохраняем файл
        file.save(file_path)
        
        # Возвращаем относительный путь для использования в URL
        return os.path.join(folder, unique_filename)
    
    return None

def delete_file(file_path):
    """
    Удаляет файл, если он существует.
    """
    if file_path:
        full_path = os.path.join('static', file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
    
    return False 