from pprint import pprint
import csv
import re
import os
from datetime import datetime


def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            # Вызываем оригинальную функцию и сохраняем результат
            result = old_function(*args, **kwargs)
            
            # Подготавливаем данные для записи в лог
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            function_name = old_function.__name__
            
            # Формируем строку с аргументами
            args_str = ', '.join([repr(arg) for arg in args])
            kwargs_str = ', '.join([f'{key}={repr(value)}' for key, value in kwargs.items()])
            all_args = ', '.join(filter(None, [args_str, kwargs_str]))
            
            # Формируем запись для лога
            log_entry = f"{timestamp} - {function_name}({all_args}) -> {repr(result)}\n"
            
            # Записываем в файл по указанному пути
            with open(path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)
            
            return result

        return new_function

    return __logger


# читаем адресную книгу в формате CSV в список contacts_list
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


@logger("phonebook_processing.log")
def format_phone(phone):
    """Приводит телефон к формату +7(999)999-99-99 или +7(999)999-99-99 доб.9999"""
    if not phone or phone.strip() == '':
        return ''

    # Ищем добавочный номер
    extension_match = re.search(r'доб\.?\s*(\d+)', phone, re.IGNORECASE)
    extension = ''
    if extension_match:
        extension = f' доб.{extension_match.group(1)}'
        phone = re.sub(r'доб\.?\s*\d+', '', phone, flags=re.IGNORECASE)

    # Удаляем все нецифровые символы
    phone = re.sub(r'\D', '', phone)

    # Если номер пустой после очистки
    if not phone:
        return ''

    # Если номер начинается с 8 или 7, делаем +7
    if phone.startswith('8') or phone.startswith('7'):
        if len(phone) == 11:
            # Форматируем как +7(999)999-99-99
            formatted_phone = f"+7({phone[1:4]}){phone[4:7]}-{phone[7:9]}-{phone[9:11]}"
            return formatted_phone + extension
        else:
            # Если номер неполный, возвращаем как есть
            return f"+7{phone[1:]}" + extension
    else:
        # Если номер не начинается с 7 или 8, возвращаем как есть
        return phone + extension


@logger("phonebook_processing.log")
def parse_fio(contact):
    """Разбирает ФИО из первых трех полей без использования регулярных выражений"""
    # Объединяем первые три поля и разбиваем по пробелам
    fio_text = ' '.join(contact[:3])
    fio_parts = fio_text.split()

    # Заполняем lastname, firstname, surname (максимум 3 части)
    result = ['', '', '']
    for i in range(min(len(fio_parts), 3)):
        result[i] = fio_parts[i]

    return result


@logger("phonebook_processing.log")
def process_contacts(contacts_list):
    """Основная функция обработки контактов"""
    # Шаг 1: Приводим в порядок ФИО и телефоны
    processed_contacts = []
    header = None

    for i, contact in enumerate(contacts_list):
        if not any(contact):  # Пропускаем пустые строки
            continue

        # Сохраняем заголовок
        if i == 0:
            header = contact
            continue

        # Парсим ФИО (без регулярок)
        lastname, firstname, surname = parse_fio(contact)

        # Форматируем телефон
        phone = format_phone(contact[5])

        # Создаем новый контакт с правильной структурой
        new_contact = [
            lastname,
            firstname,
            surname,
            contact[3],  # organization
            contact[4],  # position
            phone,
            contact[6]  # email
        ]

        processed_contacts.append(new_contact)

    # Шаг 2: Объединяем дублирующиеся записи по Фамилии и Имени
    unique_contacts = {}
    for contact in processed_contacts:
        key = (contact[0], contact[1])  # Ключ по Фамилии и Имени

        if key in unique_contacts:
            # Объединяем данные существующего контакта с новыми
            existing_contact = unique_contacts[key]
            for i in range(len(contact)):
                if not existing_contact[i] and contact[i]:
                    existing_contact[i] = contact[i]
        else:
            unique_contacts[key] = contact.copy()

    # Преобразуем словарь обратно в список
    final_contacts = list(unique_contacts.values())

    # Добавляем заголовок
    final_contacts.insert(0, header)

    return final_contacts


@logger("phonebook_processing.log")
def save_contacts_to_file(contacts_list, filename):
    """Сохраняет контакты в CSV файл"""
    with open(filename, "w", encoding="utf-8", newline='') as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerows(contacts_list)
    return f"Файл {filename} успешно сохранен"


# Основной блок выполнения
if __name__ == "__main__":
    # Очищаем лог-файл перед началом работы
    if os.path.exists("phonebook_processing.log"):
        os.remove("phonebook_processing.log")

    # Обрабатываем контакты
    final_contacts = process_contacts(contacts_list)
    
    # Сохраняем результат
    save_result = save_contacts_to_file(final_contacts, "phonebook.csv")
    
    # Заменяем исходный список
    contacts_list = final_contacts

    print("Обработка завершена. Результат сохранен в phonebook.csv")
    print("Лог работы сохранен в phonebook_processing.log")
    pprint(contacts_list)
