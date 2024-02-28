from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle

def input_error(func): #декоратор з обробки помилок
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Enter the argument for the command"
        except KeyError:
            return "Enter the argument for the command"
        except IndexError:
            return "Enter the argument for the command"
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not re.match(r"\d{10}", value): #перевірка формату номеру телефону
            raise(Exception("Invalid phone number"))
        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y") #перевірка формату дати
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")
        
class Record:
    def __init__(self, name):
        self.name = Name(name) 
        self.phones = []
        self.birthday = None
        # self.email = []

    @input_error
    def add_phone(self, phone):
        self.phones.append(Phone(phone)) #додавання номера
        print(f'New phone number for contact {self.name} added')

    @input_error
    def find_in_list(self, phone) -> int:
        for i in range(len(self.phones)):
            if self.phones[i].value == phone: #пошук номера в списку контакту та повертання його індексу
                return i
        return None
    
    @input_error
    def remove_phone(self, phone): #видалення номеру телефона
        i = self.find_in_list(phone)
        if i != None:
            del self.phones[i] 
            return f'Phone number {phone} was delated from {self.name.value} contact.'
        else:
            return f'Phone {phone} not found in {self.name} contact'
        
    @input_error
    def edit_phone(self, old_phone, new_phone): #зміна номеру телефона
        i = self.find_in_list(old_phone)
        if i != None:
            self.phones[i].value = new_phone
            return f"Phone number {old_phone} was changed to {new_phone}"
        else:
            return f"Phone {old_phone} not found in {self.name} contact"

    @input_error
    def find_phone(self, phone):
        if phone in map(str, self.phones): #пошук номеру телефона в контакті
            return phone   
        else: 
            return f"Phone {phone} not found in {self.name} contact"

    @input_error
    def contact_phone(self, name): #номери телефонів контакта
        phones = ""
        phones = f'{self.name.value} : '
        for phone in self.phones:
            phones += F'{phone.value} '
        return phones 

    @input_error
    def add_birthday(self, bday): #додавання дня народження
        self.birthday = Birthday(bday)
        return f'Birthday for contact {self.name.value} added'

    @input_error
    def show_birthday(self): #день народження контакта
        if self.birthday:
            return f'{self.name.value} birthday at {self.birthday.value.strftime("%d.%m.%Y")}'
        else:
            return f'There is no birthday record for contact {self.name.value}'

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):

    @input_error
    def add_record(self, record):
        self.data[record.name.value] = record #додавання запису
        return f"Contact added"
    
    @input_error
    def find(self, name): # пошук контакту
        if name in self.data:
            return self.data[name]
        else:
            return f"Record {name} not found"
                                    
    @input_error    
    def del_record(self, name):
        del self.data[name] #видалення запису
        return f'The entry {name} was deleted'

    def birthdays(self) -> list:
        self.book = self
        congratulation_list = [] #словник вітань
        current_date = datetime.today().date() #поточна дата
        birthday_list = ""

        for v in self.book.book:
            try:
                bday = self.book[v].birthday.value #день народження
            except Exception:
                break
            bday = bday.replace(year = current_date.year) #зміна року народження на поточний
            if bday.toordinal() < current_date.toordinal(): #якщо дн вже пройшов, додається 1 рік
                bday = bday.replace(year = current_date.year + 1)
            if bday.toordinal() - current_date.toordinal() <= 7: #якщо різниця менше 7 днів:
                if bday.weekday() == 5: #якщо день народження випадає на суботу, додається 2 дні
                        bday = bday + timedelta(days=2)
                elif bday.weekday() == 6: #якщо день народження випадає на неділю, додається 1 день
                        bday = bday + timedelta(days=1)
                congratulation_list.append({'name': self.book[v].name.value, 'congratulation_day': bday.strftime("%d.%m.%Y")}) #додавання іменинника до списку
        for rec in congratulation_list:
            birthday_list += f'{rec["name"]:10}{rec["congratulation_day"]}\n'
        if birthday_list:
            return birthday_list
        else:
            return "No birthdays the next seven days"                    



def parse_input(user_input): #розбір команди та аргументів
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) != 2:
                print("Enter the argument for the command")
            else:
                name, phone = args
                record = book.find(name)
                if type(record) == str:
                    record = Record(name)
                    print(book.add_record(record))
                record.add_phone(phone)

        elif command == "del":
            if len(args) != 1:
                print("Enter the argument for the command")
            else:
                name = args[0]
                record = book.find(name)
                if type(record) != str:
                    print(book.del_record(name))                
                else:
                    print(record)

        elif command == "remove":
            if len(args) != 2:
                print("Enter the argument for the command")
            else:
                name, phone = args
                record = book.find(name)
                if type(record) != str:
                    print(record.remove_phone(phone))
                else:
                    print(record)

        elif command == "change":
            if len(args) != 3:
                print("Enter the argument for the command")
            else:
                name, old_phone, new_phone = args
                record = book.find(name)
                if type(record) != str:
                    print(record.edit_phone(old_phone, new_phone))
                else:
                    print(record)

        elif command == "phone":
            if len(args) != 1:
                print("Enter the argument for the command")
            else:
                name = args[0]
                record = book.find(name)
                if type(record) != str:
                    print(record.contact_phone(name))
                else:
                    print(record)
    
        elif command == "all":
            for name, record in book.data.items():
                print(record.contact_phone(name))

        elif command == "add-birthday":
            if len(args) != 2:
                print("Enter the argument for the command")
            else:
                name, birthday = args
                record = book.find(name)
                if type(record) != str:
                    print(record.add_birthday(birthday))
                else:
                    print(record)

        elif command == "show-birthday":
            if len(args) != 1:
                print("Enter the argument for the command")
            else:
                name = args[0]
                record = book.find(name)
                if type(record) != str:
                    print(record.show_birthday())
                else:
                    print(record)


        elif command == "birthdays":
                print(book.birthdays())

        else:
            print("Invalid command.")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

if __name__ == "__main__":
    main()
    book = load_data()

   # # Створення запису для John
    # john_record = Record("John")
    # john_record.add_phone("1234567890")
    # john_record.add_phone("5555555555")

    # # Додавання запису John до адресної книги
    # book.add_record(john_record)

    # # Створення та додавання нового запису для Jane
    # jane_record = Record("Jane")
    # jane_record.add_phone("9876543210")
    # book.add_record(jane_record)

    # # Виведення всіх записів у книзі
    # for name, record in book.data.items():
    #     print(record)

    # # john_record.remove_phone("5555555555")
    # # book.del_record(jane_record)

    # for name, record in book.data.items():
    #     print(record)

    # jane_record.find_phone('9876543210')

    # # Знаходження та редагування телефону для John
    # john = book.find("John")
    # john.edit_phone("1234567890", "1112223333")

    # print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # # Пошук конкретного телефону у записі John
    # found_phone = john.find_phone("5555555555")
    # print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # jane_record.add_birthday("25.02.1998")
    # john_record.add_birthday("27.02.1972")
    # print(john)

    # print(book.birthdays())
    # print(jane_record.show_birthday())


    # Видалення запису Jane
    # book.delete("Jane")