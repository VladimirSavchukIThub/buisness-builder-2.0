import os
import urllib.request
import zipfile
import io
import shutil

# Путь для сохранения шрифтов
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

# URL для скачивания шрифтов DejaVu
DEJAVU_URL = 'https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.zip'

def download_and_extract_fonts():
    """Загружает и распаковывает шрифты DejaVu"""
    
    # Создаем директорию fonts, если она не существует
    if not os.path.exists(FONTS_DIR):
        os.makedirs(FONTS_DIR)
        print(f"Создана директория: {FONTS_DIR}")
    
    # Загружаем архив с шрифтами
    try:
        print(f"Загрузка шрифтов с {DEJAVU_URL}...")
        response = urllib.request.urlopen(DEJAVU_URL)
        zip_data = response.read()
        print(f"Загружено {len(zip_data)} байт")
        
        # Распаковываем архив
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
            # Получаем список всех ttf файлов в архиве
            ttf_files = [f for f in zip_file.namelist() if f.endswith('.ttf')]
            
            # Извлекаем только нужные шрифты
            needed_fonts = []
            for ttf_file in ttf_files:
                basename = os.path.basename(ttf_file)
                if basename in ['DejaVuSans.ttf', 'DejaVuSans-Bold.ttf']:
                    needed_fonts.append((ttf_file, basename))
            
            # Извлекаем шрифты
            for src_path, dst_name in needed_fonts:
                dst_path = os.path.join(FONTS_DIR, dst_name)
                with zip_file.open(src_path) as src_file, open(dst_path, 'wb') as dst_file:
                    shutil.copyfileobj(src_file, dst_file)
                print(f"Сохранен шрифт: {dst_name}")
        
        print("Шрифты успешно загружены и распакованы!")
        return True
    
    except Exception as e:
        print(f"Ошибка при загрузке шрифтов: {e}")
        return False

if __name__ == "__main__":
    download_and_extract_fonts() 