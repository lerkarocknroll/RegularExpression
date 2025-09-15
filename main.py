from pprint import pprint
import csv
import re

# читаем адресную книгу в формате CSV в список contacts_list
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)


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

    # Удаляем все нецифровые символы, кроме "+"
    phone = re.sub(r'[^\d+]', '', phone)

    # Если номер пустой после очистки
    if not phone:
        return ''

    # Если номер начинается с 8, заменяем на +7
    if phone.startswith('8'):
        phone = '7' + phone[1:]
    # Если номер начинается с 7, добавляем +
    elif phone.startswith('7'):
        phone = '+' + phone
    # Если номер не начинается с +7, но имеет 11 цифр
    elif len(phone) == 11:
        phone = '+7' + phone[1:]

    # Форматируем основной номер
    if len(phone) == 12 and phone.startswith('+7'):
        formatted_phone = f"+7({phone[2:5]}){phone[5:8]}-{phone[8:10]}-{phone[10:12]}"
        return formatted_phone + extension
    else:
        return phone + extension


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


# Шаг 1: Приводим в порядок ФИО и телефоны
processed_contacts = []
for contact in contacts_list:
    if not any(contact):  # Пропускаем пустые строки
        continue

    # Пропускаем заголовок
    if contact[0] == 'lastname' and contact[1] == 'firstname':
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
    key = (contact[0], contact[1])  # Ключ по Фамилии и Имени (как в задании)

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
final_contacts.insert(0, ['lastname', 'firstname', 'surname', 'organization', 'position', 'phone', 'email'])

# Заменяем исходный список
contacts_list = final_contacts

# Сохраняем результат
with open("phonebook.csv", "w", encoding="utf-8", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows(contacts_list)

print("Обработка завершена. Результат сохранен в phonebook.csv")
pprint(contacts_list)