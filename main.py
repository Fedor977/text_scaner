import tkinter as tk  # импортируем модуль tkinter для создания графического интерфейса
from tkinter import filedialog, messagebox  # Импортируем диалоговые окна и сообщения из tkinter
from PIL import Image, ImageOps  # импортируем pillow для работы с изображениями
import pytesseract  # импортируем pytesseract для распознавания текста на изображениях
from fpdf import FPDF  # импортируем FPDF для создания PDF-файлов
from docx import Document  # импортируем Document из docx для создания Word-файлов
import os  # импортируем модуль os для работы с операционной системой
from langdetect import detect, DetectorFactory  # Импортируем langdetect для определения языка текста
from langdetect.lang_detect_exception import LangDetectException  # исключение для langdetect
from googletrans import Translator

# путь к tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # путь до исполняемого файла
DetectorFactory.seed = 0  # устанавливаем seed для детектора языка по умолчанию


class App:
    """Главное окно в приложении"""

    def __init__(self, root):
        self.root = root  # устанавливаем корневое окно приложения
        self.root.title("Image to Text Converter")  # устанавливаем заголовок окна
        self.root.geometry("400x200")  # устанавливаем размеры окна

        self.file_path = None  # инициализируем переменную для хранения пути к файлу

        # кнопка для загрузки изображения
        self.upload_button = tk.Button(root, text="Загрузить изображение",
                                       command=self.upload_image)  # создаем кнопку для загрузки изображения
        self.upload_button.pack(pady=10)  # размещаем кнопку с отступом pady=10

        # кнопка для конвертации изображения
        self.convert_button = tk.Button(root, text="Конвертировать",
                                        command=self.convert_image)  # создаем кнопку для конвертации изображения
        self.convert_button.pack(pady=10)  # размещаем кнопку с отступом pady=10

        # радиокнопки для выбора формата конвертации
        self.format_var = tk.StringVar(value="pdf")  # переменная для хранения выбранного формата (по умолчанию PDF)
        self.radio_pdf = tk.Radiobutton(root, text="PDF", variable=self.format_var,
                                        value="pdf")  # радиокнопка для выбора PDF
        self.radio_pdf.pack()  # размещаем радиокнопку
        self.radio_word = tk.Radiobutton(root, text="Word", variable=self.format_var,
                                         value="word")  # радиокнопка для выбора word
        self.radio_word.pack()  # размещаем радиокнопку

    def upload_image(self):
        """Диалоговое окно для выбора файла изображения"""
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.pdf")])  # открываем диалоговое окно для выбора изображения
        if self.file_path:
            messagebox.showinfo("Файл выбран", os.path.basename(
                self.file_path))  # показываем информационное сообщение с именем выбранного файла

    def convert_image(self):
        """Конвертация изображения"""
        if not self.file_path:  # если файл не выбран
            messagebox.showwarning("Ошибка", "Сначала загрузите изображение")  # показываем предупреждение
            return

        # задать язык OCR в зависимости от выбранного изображения
        language = self.detect_language(self.file_path)  # определение языка текста на изображении
        text = self.extract_text(self.file_path, language)  # извлечение текста с изображения
        if not text:  # если текст не был извлечен
            messagebox.showwarning("Ошибка", "Не удалось извлечь текст из изображения")
            return

        # Проверяем язык текста и при необходимости переводим на русский
        if language != 'rus':
            translated_text = self.translate_to_russian(text)
            text = translated_text if translated_text else text

        if self.format_var.get() == "pdf":  # если выбран формат PDF
            self.save_as_pdf(text)  # сохраняем текст в формате PDF
        else:
            self.save_as_word(text)  # сохраняем текст в формате Word

        messagebox.showinfo("Отлично!",
                            "Конвертация завершена")  # показываем информационное сообщение о завершении операции

    def translate_to_russian(self, text):
        """Перевод текста на русский язык"""
        translator = Translator()
        translation = translator.translate(text, dest='ru')
        return translation.text

    def detect_language(self, file_path):
        """Автоматическое определение зыка"""
        try:
            # извлекаем текст с изображения
            temp_text = self.extract_text(file_path,
                                          lang='eng+rus+chi_sim')  # извлекаем текст с изображения с языковыми параметрами
            detected_lang = detect(temp_text)  # определяем язык текста
            if detected_lang == 'ru':  # если язык русский
                return 'rus'
            elif detected_lang == 'en':  # если язык английский
                return 'eng'
            elif detected_lang == 'zh-cn':  # если язык китайский
                return 'chi_sim'
            else:
                return 'eng'  # по умолчанию возвращаем английский язык
        except LangDetectException:
            return 'eng'  # по умолчанию возвращаем английский язык

    def extract_text(self, file_path, lang):
        """Извлечение текста"""
        if file_path.lower().endswith('.pdf'):  # если выбран PDF-файл
            images = self.pdf_to_images(file_path)  # конвертируем PDF в изображения
            text = ""  # переменная для хранения текста
            for img in images:  # для каждого изображения
                text += pytesseract.image_to_string(img, lang=lang)  # извлекаем текст с помощью pytesseract
            return text  # возвращаем извлеченный текст
        else:  # если выбрано изображение (jpg, jpeg, png)
            img = Image.open(file_path)  # открываем изображение с помощью Pillow
            img = self.resize_image_if_needed(img)  # масштабируем изображение при необходимости
            return pytesseract.image_to_string(img, lang=lang)  # извлекаем текст с изображения с помощью pytesseract

    def resize_image_if_needed(self, img, max_width=2000, max_height=2000):
        """Изменение размера изображения, при необходимости"""
        width, height = img.size  # получаем размеры изображения
        if width > max_width or height > max_height:  # если размеры превышают максимальные значения
            img.thumbnail((max_width, max_height), Image.ANTIALIAS)  # уменьшаем изображение
        return img  # возвращаем измененное изображение

    def pdf_to_images(self, pdf_path):
        """Сохранение текста в формате PDF"""
        from pdf2image import convert_from_path  # импортируем функцию для конвертации
        return convert_from_path(pdf_path)  # возвращаем список изображений из PDF

    def save_as_pdf(self, text):
        pdf = FPDF()  # создаем новый объект PDF
        pdf.add_page()  # добавляем новую страницу
        pdf.set_auto_page_break(auto=True, margin=15)  # устанавливаем автоматический разрыв страницы

        # устанавливаем шрифт, поддерживающий Unicode
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font("DejaVu", size=12)  # устанавливаем размер шрифта

        pdf.multi_cell(0, 10, text)  # добавляем многострочный текст в PDF
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files",
                                                                                        "*.pdf")])  # filedialog открывает диалоговое окно файла, asksaveasfilename спрашивает как назвать файл при сохранении и добавляем путь куда сохранить
        if output_path:  # если указан путь
            try:  # попытайся
                pdf.output(output_path)  # сохраняем PDF
                messagebox.showinfo("Успех", "PDF успешно сохранен")  # показываем информационное сообщение
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении PDF: {e}")  # показываем сообщение об ошибке

    def save_as_word(self, text):
        """Сохранение в формате word"""
        doc = Document()  # создаем новый документ Word
        doc.add_paragraph(text)  # добавляем текст в документ
        output_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word files",
                                                                                         "*.docx")])  # filedialog открывает диалоговое окно файла, asksaveasfilename спрашивает как назвать файл при сохранении, так же вводим путь для сохр файл
        if output_path:  # если указан путь
            doc.save(output_path)  # сохраняем документ Word


if __name__ == "__main__":
    root = tk.Tk()  # создаем главное окно приложения
    app = App(root)  # создаем экземпляр приложения
    root.mainloop()  # запускаем основной цикл приложения

"""
атрибут text в коде представляет собой переменную, содержащую текст, 
который вы хотите сохранить в файле PDF или Word.

атрибут pdf_path используется в функции pdf_to_images для передачи пути к PDF-файлу, 
который требуется конвертировать в изображения.

max_width является аргументом функции resize_image_if_needed. 
Он определяет максимальную ширину изображения, которая будет сохранена при изменении размера.

атрибут lang используется для передачи языка OCR в функции extract_text, где он определяет, 
на каком языке будет проводиться распознавание текста с изображения.

атрибут root является экземпляром tkinter.Tk, который представляет главное окно вашего приложения GUI на tkinter. 
Он используется для создания и управления различными элементами интерфейса.
"""
