import sys
import os
import time
import shutil
import getpass


folder_path = "/Users/MACM2/Desktop/python_project"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)


users_file_path = os.path.join(folder_path, "users.txt")
books_file_path = os.path.join(folder_path, "library_data.txt")
backup_folder_path = os.path.join(folder_path, "backups")


users = {}
books = {}

def addUser():
    userId = str(int(max(users.keys())) + 1)
    userType = input("Enter user type (student/staff): ").lower()
    userName = input("Enter user name: ")
    emailAddress = input("Enter email address: ")
    phoneNumer = input("Enter phone number: ")
    password = getpass.getpass("Enter password: ")

    users[userId] = {
        "userId": userId,
        "userType": userType,
        "userName": userName,
        "emailAddress": emailAddress,
        "phoneNumer": phoneNumer,
        "password": password,
        "borrowedBooks": []
    }

    writeDataToFile(users_file_path, users)
    print(f"User '{userName}' added successfully with ID {userId}.")

def load_users():
    global users
    if os.path.exists(users_file_path):
        with open(users_file_path, "r") as file:
            for line in file:
                parts = line.strip().split('|')
                if len(parts) == 7:
                    userId, userType, userName, emailAddress, phoneNumer, password, borrowedBooks_str = parts
                    users[userId] = {
                        "userId": userId,
                        "userType": userType,
                        "userName": userName,
                        "emailAddress": emailAddress,
                        "phoneNumer": phoneNumer,
                        "password": password,
                        "borrowedBooks": eval(borrowedBooks_str) if borrowedBooks_str else []
                    }
                else:
                    print(f"Skipping invalid line: {line.strip()}")
    else:
        users["1001"] = {"userId": "1001", "userType": "staff", "userName": "Admin User", "emailAddress": "admin@mail.com", "phoneNumer": "123456789", "password": "admin123", "borrowedBooks": []}
        users["1002"] = {"userId": "1002", "userType": "student", "userName": "Student User", "emailAddress": "student@mail.com", "phoneNumer": "987654321", "password": "student123", "borrowedBooks": []}
        writeDataToFile(users_file_path, users)

def load_books():
    global books
    if os.path.exists(books_file_path):
        with open(books_file_path, "r") as file:
            for line in file:
                parts = line.strip().split('|')
                if len(parts) == 9:
                    bookId, bookName, author, genre, pages, status, borrowedBy, dueDate, borrowerInfo = parts
                    books[bookId] = {
                        "bookId": bookId,
                        "bookName": bookName,
                        "author": author,
                        "genre": genre,
                        "pages": int(pages),
                        "status": status,
                        "borrowedBy": None if borrowedBy == "None" else borrowedBy,
                        "dueDate": None if dueDate == "None" else float(dueDate),
                        "borrowerInfo": eval(borrowerInfo) if borrowerInfo else {}
                    }
                else:
                    print(f"Skipping invalid line: {line.strip()}")

def writeDataToFile(fileName, data):
    with open(fileName, "w") as file:
        for key, value in data.items():
            line = '|'.join([str(v) for v in value.values()]) + '\n'
            file.write(line)

def addBook():
    bookId = len(books) + 2000
    bookName = input("Enter book name: ")
    author = input("Enter author name: ")
    genre = input("Enter book genre: ")
    pages = int(input("Enter number of pages: "))

    books[bookId] = {
        "bookId": str(bookId),
        "bookName": bookName,
        "author": author,
        "genre": genre,
        "pages": pages,
        "status": "available",
        "borrowedBy": None,
        "dueDate": None,
        "borrowerInfo": {}
    }

    writeDataToFile(books_file_path, books)
    print(f"Book '{bookName}' added successfully with ID {bookId}.")

def removeBook():
    listBooks()
    bookId = input("Enter the book ID to remove: ")
    if bookId in books:
        del books[bookId]
        writeDataToFile(books_file_path, books)
        print("Book removed successfully!")
    else:
        print("Book not found.")

def borrowBook(userId):
    print("Available Books for Borrowing:")
    for book in books.values():
        if book["status"] == "available":
            print(f"Book ID: {book['bookId']}, Name: {book['bookName']}, Author: {book['author']}")

    bookId = input("Enter book ID to borrow: ")
    if bookId in books and books[bookId]["status"] == "available":
        books[bookId]["status"] = "borrowed"
        books[bookId]["borrowedBy"] = userId
        books[bookId]["dueDate"] = time.time() + 7 * 86400
        books[bookId]["borrowerInfo"] = users[userId]
        users[userId]["borrowedBooks"].append(bookId)
        print(f"Book borrowed successfully. Due date: {time.ctime(books[bookId]['dueDate'])}")
        writeDataToFile(books_file_path, books)
    else:
        print("Book is not available.")

def returnBook(userId):
    bookId = input("Enter book ID to return: ")
    if bookId in books and books[bookId]["borrowedBy"] == userId:
        overdueFine = calculateFine(bookId)
        books[bookId]["status"] = "available"
        books[bookId]["borrowedBy"] = None
        books[bookId]["dueDate"] = None
        print(f"Book returned successfully. Fine: {overdueFine}")
        writeDataToFile(books_file_path, books)
    else:
        print("This book wasn't borrowed by you.")

def calculateFine(bookId):
    if bookId in books and books[bookId]["dueDate"]:
        overdueDays = (time.time() - books[bookId]["dueDate"]) / 86400
        if overdueDays > 0:
            return overdueDays * 1
    return 0

def listBooks():
    for book in books.values():
        print(f"Book ID: {book['bookId']}, Name: {book['bookName']}, Author: {book['author']}, Genre: {book['genre']}, Pages: {book['pages']}, Status: {book['status']}")
        if book["status"] == "borrowed":
            borrowed_user = users[book["borrowedBy"]]
            borrowed_days = int((time.time() - book["dueDate"]) / 86400)
            due_date = time.ctime(book["dueDate"])
            print(f"Borrowed By: {borrowed_user['userName']}, Due Date: {due_date}, Borrowed Days: {borrowed_days} days")

def searchAUser(userInfo):
    for user in users.values():
        if user["userId"] == userInfo or user["userName"].lower() == userInfo.lower():
            return user
    return {}

def listStudents():
    print("Listing all students:")
    for user in users.values():
        if user["userType"] == "student":
            print(f"User ID: {user['userId']}, Name: {user['userName']}, Email: {user['emailAddress']}, Phone: {user['phoneNumer']}")

def removeStudent():
    listStudents()
    userId = input("Enter the user ID to remove: ")
    if userId in users and users[userId]["userType"] == "student":
        del users[userId]
        writeDataToFile(users_file_path, users)
        print(f"Student with ID {userId} removed successfully!")
    else:
        print("Student not found.")

def searchStudentDetails(userInfo):
    user = searchAUser(userInfo)
    if user:
        if user["userType"] == "student":
            print(f"User ID: {user['userId']}, Name: {user['userName']}, Email: {user['emailAddress']}, Phone: {user['phoneNumer']}")
            borrowed_books = [book for book in books.values() if book["borrowedBy"] == user["userId"]]
            if borrowed_books:
                print(f"Books borrowed by {user['userName']}:")
                for book in borrowed_books:
                    borrowed_days = int((time.time() - book["dueDate"]) / 86400)
                    borrow_date = time.ctime(book["dueDate"] - 7 * 86400)
                    print(f"Book Name: {book['bookName']}, Borrowed Date: {borrow_date}, Borrowed Days: {borrowed_days} days")
            else:
                print("No books borrowed.")
        else:
            print("No student found with that name or ID.")
    else:
        print("No student found.")

def searchBookByTitle():
    title = input("Enter the book title to search for: ").lower()
    found_books = [book for book in books.values() if title in book["bookName"].lower()]
    if found_books:
        for book in found_books:
            print(f"Book ID: {book['bookId']}, Name: {book['bookName']}, Author: {book['author']}, Genre: {book['genre']}, Pages: {book['pages']}, Status: {book['status']}")
            if book["status"] == "borrowed":
                borrowed_user = users[book["borrowedBy"]]
                borrowed_days = int((time.time() - book["dueDate"]) / 86400)
                due_date = time.ctime(book["dueDate"])
                print(f"Borrowed By: {borrowed_user['userName']}, Due Date: {due_date}, Borrowed Days: {borrowed_days} days")
    else:
        print("No books found with that title.")

def backup_data():
    if not os.path.exists(backup_folder_path):
        os.makedirs(backup_folder_path)
    shutil.copy(users_file_path, os.path.join(backup_folder_path, "users_backup.txt"))
    shutil.copy(books_file_path, os.path.join(backup_folder_path, "books_backup.txt"))
    print("Backup completed successfully!")

def restore_data():
    if os.path.exists(os.path.join(backup_folder_path, "users_backup.txt")):
        shutil.copy(os.path.join(backup_folder_path, "users_backup.txt"), users_file_path)
        shutil.copy(os.path.join(backup_folder_path, "books_backup.txt"), books_file_path)
        print("Data restored successfully!")
    else:
        print("No backup found.")

def mainMenu(aUser):
    while True:
        if aUser["userType"] == "staff":
            print("1-Add Book")
            print("2-Remove Book")
            print("3-List Books")
            print("4-Borrow Book")
            print("5-Return Book")
            print("6-Add User")
            print("7-Search A User")
            print("8-Remove Student")
            print("9-Backup Data")
            print("10-Restore Data")
            print("11-Search Book by Title")
            print("12-Exit")
            userChoice = input("Enter your choice: ")
            if userChoice == "1":
                addBook()
            elif userChoice == "2":
                removeBook()
            elif userChoice == "3":
                listBooks()
            elif userChoice == "4":
                borrowBook(aUser["userId"])
            elif userChoice == "5":
                returnBook(aUser["userId"])
            elif userChoice == "6":
                addUser()
            elif userChoice == "7":
                userInfo = input("Enter user id or user name: ")
                searchStudentDetails(userInfo)
            elif userChoice == "8":
                removeStudent()
            elif userChoice == "9":
                backup_data()
            elif userChoice == "10":
                restore_data()
            elif userChoice == "11":
                searchBookByTitle()
            elif userChoice == "12":
                sys.exit()
            else:
                print("Invalid choice. Please try again.")
        elif aUser["userType"] == "student":
            print("1-List Books")
            print("2-Borrow Book")
            print("3-Return Book")
            print("4-Exit")
            userChoice = input("Enter your choice: ")
            if userChoice == "1":
                listBooks()
            elif userChoice == "2":
                borrowBook(aUser["userId"])
            elif userChoice == "3":
                returnBook(aUser["userId"])
            elif userChoice == "4":
                sys.exit()
            else:
                print("Invalid choice. Please try again.")

def signIn(userId, userPassword):
    aUser = searchAUser(userId)
    if aUser:
        if aUser["password"] == userPassword:
            return aUser
        else:
            print("Invalid password")
            return False
    else:
        print("Invalid user id")
        return False

load_users()
load_books()

userId = input("Enter your user id: ")
userPassword = getpass.getpass("Enter your password: ")
aUser = signIn(userId, userPassword)

if aUser:
    mainMenu(aUser)
else:
    print("Invalid user id or password")
