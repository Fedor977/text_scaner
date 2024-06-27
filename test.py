import unittest
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from io import BytesIO
from main import App
import os


class TestAppFunctionality(unittest.TestCase):
    """Тестирование функционала на вход и выход данных"""

    def setUp(self):
        """Настройка перед выполнением каждого теста."""
        self.root = tk.Tk()
        self.app = App(self.root)
        self.app.root.withdraw()  # скрыть основное окно

    def tearDown(self):
        """Очистка после выполнения каждого теста."""
        self.root.destroy()

    def test_upload_image(self):
        """Тест загрузки изображения."""
        # подготовка заглушки для диалога выбора файла
        self.app.file_path = None
        file_path = os.path.abspath('content/test_image.jpg')  # Путь к тестовому изображению
        # моделирование диалога выбора файла
        with unittest.mock.patch('tkinter.filedialog.askopenfilename', return_value=file_path):
            self.app.upload_image()
        # проверка, что файл был выбран
        self.assertEqual(self.app.file_path, file_path)

    def test_convert_to_pdf(self):
        """Тест конвертации изображения в PDF."""
        # подготовка заглушки для диалога выбора файла
        self.app.file_path = os.path.abspath('test_image.jpg')  # Путь к тестовому изображению
        # моделирование диалога сохранения файла PDF
        with unittest.mock.patch('tkinter.filedialog.asksaveasfilename', return_value=os.path.abspath('test.pdf')):
            self.app.convert_image()
        # проверка успешного сохранения PDF
        self.assertTrue(os.path.exists('test.pdf'))

    def test_convert_to_word(self):
        """Тест конвертации изображения в Word."""
        # подготовка заглушки для диалога выбора файла
        self.app.file_path = os.path.abspath('test_image.jpg')  # Путь к тестовому изображению
        # моделирование диалога сохранения файла Word
        with unittest.mock.patch('tkinter.filedialog.asksaveasfilename', return_value=os.path.abspath('test.docx')):
            self.app.format_var.set("word")
            self.app.convert_image()
        # проверка успешного сохранения Word
        self.assertTrue(os.path.exists('test.docx'))

    def test_detect_language(self):
        """Тест автоматического определения языка."""
        # подготовка заглушки для извлечения текста
        test_text = "This is a test text"
        with unittest.mock.patch.object(App, 'extract_text', return_value=test_text):
            language = self.app.detect_language('test.jpg')
        # проверка корректного определения языка
        self.assertEqual(language, 'eng')

    def test_extract_text_from_image(self):
        """Тест извлечения текста из изображения."""
        # подготовка тестового изображения
        test_image = Image.new('RGB', (100, 100))
        image_data = BytesIO()
        test_image.save(image_data, format='JPEG')
        image_data.seek(0)
        # моделирование извлечения текста
        extracted_text = self.app.extract_text(image_data, 'eng')
        # проверка наличия извлеченного текста
        self.assertTrue(extracted_text)


if __name__ == "__main__":
    unittest.main()
