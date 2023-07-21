from collections import UserDict
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime, date
import re

# Клас Field, який буде батьківським для всіх полів, 
# у ньому потім реалізуємо логіку, загальну для всіх полів.   
class Field:
    def __init__(self, value) -> None:
        self.value = value
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return str(self)

# Клас Name, обов'язкове поле з ім'ям.     
class Name(Field):
    ...

# Клас Phone, необов'язкове поле з телефоном 
# та таких один запис (Record) може містити кілька.   
class Phone(Field):

    def __init__(self, value) -> None:
            if not self._is_valid_phone(value):
                raise ValueError("Invalid phone number format. Please enter 10 digits without spaces or separators.")
            self.__value = value

    @staticmethod
    def _is_valid_phone(phone):
        pattern = r'^\d{10}$'
        return bool(re.match(pattern, phone))

    @property
    def value(self):
        return self.__value 
    
    @value.setter
    def value(self, value):
        if not self._is_valid_phone(value):
            raise ValueError("Invalid phone number format. Please enter 10 digits without spaces or separators.")
        self.__value = value

    def __str__(self):
        return self.__value

class BirthdayError(BaseException):
    def __init__(self, message="Invalid birthday date. Please enter date format dd-mm-yyyy") -> None:
        super().__init__(message)

class Birthday(Field):
    def __init__(self, value) -> None:
        self.value = value
        # super().__init__(value)
    ...

    @property
    def value(self):
        return self.__value #.strftime("%d -%m -%Y")
    
    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, "%d-%m-%Y")
        except ValueError as e:
            raise BirthdayError()
    
    def __str__(self):
        return self.__value.strftime("%d-%m-%Y")


# Клас Record, який відповідає за логіку додавання/видалення/редагування 
# необов'язкових полів та зберігання обов'язкового поля Name.
# Клас Record приймає ще один додатковий (опціональний) аргумент класу Birthday. Це поле не обов'язкове 
class Record:
    def __init__(self, name: Name, phone: Phone = None, Birthday: Birthday = None) -> None:
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = Birthday
    
    def add_phone(self, phone: Phone):
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)
            return f"phone {phone} add to contact {self.name}"
        return f"{phone} present in phones of contact {self.name}"
    
    def change_phone(self, old_phone, new_phone):
        for idx, p in enumerate(self.phones):
            if old_phone.value == p.value:
                self.phones[idx] = new_phone
                return f"old phone {old_phone} change to {new_phone}"
        return f"{old_phone} not present in phones of contact {self.name}"

    def change_name(self, new_name: Name):
        self.name = new_name
        return f"Name changed to {new_name} for contact {self.name}"    


# Додамо функцію days_to_birthday, яка повертає кількість днів до наступного дня народження.
    def days_to_birthday(self):
        if self.birthday:
            today = date.today()
            birthday_date = self.birthday.value.date()
            birthday_date = birthday_date.replace(year=today.year)

            if birthday_date < today:
                birthday_date = birthday_date.replace(year=today.year + 1)

            days_to_birthday = (birthday_date - today).days
            return days_to_birthday
        return None


    def __str__(self) -> str:
        birthday_info = ""
        if self.birthday:
            days_to_birthday = self.days_to_birthday()
            birthday_info = f", Days to birthday: {days_to_birthday}" if days_to_birthday is not None else ""
        return f"{self.name}: {', '.join(str(p) for p in self.phones)}{birthday_info}"


# Клас AddressBook, який наслідується від UserDict, 
# та ми потім додамо логіку пошуку за записами до цього класу.
class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[str(record.name)] = record
        return f"Contact {record} add success"
    
    def delete_record(self, name: str):
        if name in self.data:
            del self.data[name]
            return f"Contact with name '{name}' deleted successfully"
        return f"No contact with name '{name}' in address book"
    
# метод iterator, який повертає генератор за записами    
    def __iter__(self, n=2):
        keys = list(self.data.keys())
        for i in range(0, len(keys), n):
            chunk = {key: self.data[key] for key in keys[i:i + n]}
            yield chunk

    

    def __str__(self) -> str:
        return "\n".join(str(r) for r in self.data.values())
# another module .py


address_book = AddressBook()


def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except IndexError as e:
            return e
        except NameError as e:
            return e
        except BirthdayError as e:
            return e
        except ValueError as e:
            return e
        except TypeError as e:
            return e
    return wrapper


# Record реалізує методи для додавання об'єктів Phone.
@input_error
def add_command(*args):
    name = Name(args[0])
    phone = Phone(args[1])
    birthday = Birthday(args[2]) if len(args) > 2 else None
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.add_phone(phone)
    rec = Record(name, phone, birthday)
    return address_book.add_record(rec)

# Record реалізує методи для редагування об'єктів Phone.
@input_error
def change_command(*args):
    name = Name(args[0])
    old_phone = Phone(args[1])
    new_phone = Phone(args[2])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.change_phone(old_phone, new_phone)
    return f"No contact {name} in address book"

# Record реалізує методи для редагування об'єктів Phone.
def edit_name_command(*args):
    name = Name(args[0])
    new_name = Name(args[1])
    rec: Record = address_book.get(str(name))
    if rec:
        return rec.change_name(new_name)
    return f"No contact {name} in address book"


# Record реалізує методи для видалення об'єктів Phone.
@input_error
def delete_contact_command(*args):
    if args:
        name = args[0]
        return address_book.delete_record(name)
    else:
        return "Please provide a name to delete the contact."


def find_command(*args):
    query = args[0]  # Або номер або ім'я
    
    matching_records = []
    for record in address_book.data.values():
        # Перевірка відповідності запиту імені чи номеру телефону
        if query.lower() in str(record.name).lower()\
              or any(query.lower() in str(phone).lower() for phone in record.phones):
            matching_records.append(record)
    
    if matching_records:
        console = Console()
        table = Table(show_header=True, header_style="bold", box=box.ROUNDED)
        table.add_column("Name")
        table.add_column("Phone number")

        for record in matching_records:
            name = str(record.name)
            phone_numbers = ', '.join([str(phone) for phone in record.phones])
            table.add_row(name, phone_numbers)

        console.print(table)
    else:
        return f"No records found for the query: {query}"


def exit_command(*args):
    return "Good bye!"
    

def unknown_command(*args):
    pass


def show_all_command(*args):
    if address_book.data:
        console = Console()
        table = Table(show_header=True, header_style="bold", box=box.ROUNDED)
        table.add_column("Name")
        table.add_column("Phone number")
        table.add_column("Birthday", style="dim")

        for record in address_book.data.values():
            name = str(record.name)
            phone_numbers = ', '.join([str(phone) for phone in record.phones])
            birthday = str(record.birthday) if record.birthday else "N/A"
            table.add_row(name, phone_numbers, birthday)

        console.print(table)
    else:
        print('No contacts saved.')
#     return address_book


def hello_command(*args):
    return "How can I help you?"


def show_address_book():
    if address_book:
        page_number = 1
        for chunk in address_book:
            console = Console()
            table = Table(show_header=True, header_style="bold", box=box.ROUNDED)
            table.add_column("Name")
            table.add_column("Phone number")
            table.add_column("Birthday", style="dim")

            for record in chunk.values():
                name = str(record.name)
                phone_numbers = ', '.join([str(phone) for phone in record.phones])
                birthday = str(record.birthday) if record.birthday else "N/A"
                table.add_row(name, phone_numbers, birthday)

            console.print(f"Page {page_number}:")
            console.print(table)
            page_number += 1
    else:
        print('No contacts saved.')

COMMANDS = {
    add_command: ("add", "+", "2"),
    change_command: ("change", "зміни", "3"),
    exit_command: ("bye", "exit", "end", "0"),
    delete_contact_command:("del","8"),
    find_command: ("find", "4"),
    show_all_command: ("show all", "5"),
    hello_command:("hello", "1"),
    edit_name_command: ("edit", "7"),
    show_address_book: ("page", "**", address_book)   
}


def parser(text:str):
    for cmd, kwds in COMMANDS.items():
        for kwd in kwds:
            if text.lower().startswith(kwd):
                # print(cmd)
                data = text[len(kwd):].strip().split()
                # print(data)
                return cmd, data 
    return unknown_command, []


def main():
    while True:
        user_input = input("--->>> ")
        
        cmd, data = parser(user_input)

        result = cmd(*data)

        print(result)
        
        if cmd == exit_command:
            break

if __name__ == "__main__":
    main()