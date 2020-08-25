from cs50 import SQL
from csv import DictReader
from random import choice
from datetime import datetime
import sqlite3

##################
# create database

conn = sqlite3.connect('library.db')

db = SQL("sqlite:///library.db")

db.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT NOT NULL);")
db.execute("CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL, year TEXT NOT NULL, status INTEGER DEFAULT 1, user_id INTEGER DEFAULT 0);")
db.execute("CREATE TABLE history (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, book_id INTEGER NOT NULL, date TEXT NOT NULL, status INTEGER DEFAULT 0);")
db.execute("CREATE TABLE reminder (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, last_email INTEGER DEFAULT 7, status INTEGER DEFAULT 0);")

##################
# insert data into users table
with open("users.csv", newline='') as csvfile:
    reader = DictReader(csvfile)
    for row in reader:
        first_name = row["first_name"]
        last_name = row["last_name"]
        email = row["email"]
        db.execute("INSERT INTO users (first_name, last_name, email) VALUES (?, ?, ?);", first_name, last_name, email)
csvfile.close()

#################
# insert data into books table
with open("books.csv", newline='') as csvfile:
    reader = DictReader(csvfile)
    for row in reader:
        title = row["title"]
        author = row["author"]
        year = row["year"]
        db.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?);", title, author, year)
csvfile.close()

##################
# insert data into history table

# create list of users_id
users_id_list_dict = db.execute("SELECT user_id FROM users;")
users_id_list = []
for dic in users_id_list_dict:
    users_id_list.append(dic["user_id"])

# create list of books_id
books_id_list_dict = db.execute("SELECT book_id FROM books;")
books_id_list = []
for dic in books_id_list_dict:
    books_id_list.append(dic["book_id"])



# create history table

year = 2020
month = 1
for m in range(0, 8):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        day = 1
        for d in range(0, 30):
            hours = 10
            for h in range(0, 3):
                minutes = choice(range(0, 60))
                seconds = choice(range(0, 60))
                datetime_status = datetime(year, month, day, hours, minutes, seconds)
                hours += 3
                #
                # random book_id
                book_id = choice(books_id_list)

                # status of book_id
                status = db.execute("SELECT status FROM books WHERE book_id = ?", book_id)[0]["status"]
                # status == 1 - in library, status == 0 - borrowed
                # when book is in library any user can borrow
                if status == 1:
                    user_id = choice(users_id_list)

                    # add to history - default status == 0
                    db.execute("INSERT INTO history (user_id, book_id, date) VALUES (?, ?, ?);", user_id, book_id, datetime_status)
                    db.execute("UPDATE books SET status = 0, user_id = ? WHERE book_id = ?;", user_id, book_id)

                # when book is borrowed, only user which borrowed can return
                else:
                    user_id = db.execute("SELECT user_id FROM books WHERE book_id = ?;", book_id)[0]["user_id"]
                    db.execute("INSERT INTO history (user_id, book_id, date, status) VALUES (?, ?, ?, 1);", user_id, book_id, datetime_status)
                    db.execute("UPDATE books SET status = 1, user_id = 0 WHERE book_id = ?;", book_id)

                #
            day += 1
    elif month in [4, 6, 9, 11]:
        day = 1
        for d in range(0, 29):
            hours = 10
            for h in range(0, 3):
                minutes = choice(range(0, 60))
                seconds = choice(range(0, 60))
                datetime_status = datetime(year, month, day, hours, minutes, seconds)
                hours += 3
                #
                                # random book_id
                book_id = choice(books_id_list)

                # status of book_id
                status = db.execute("SELECT status FROM books WHERE book_id = ?", book_id)[0]["status"]
                # status == 1 - in library, status == 0 - borrowed
                # when book is in library any user can borrow
                if status == 1:
                    user_id = choice(users_id_list)

                    # add to history - default status == 0
                    db.execute("INSERT INTO history (user_id, book_id, date) VALUES (?, ?, ?);", user_id, book_id, datetime_status)
                    db.execute("UPDATE books SET status = 0, user_id = ? WHERE book_id = ?;", user_id, book_id)

                # when book is borrowed, only user which borrowed can return
                else:
                    user_id = db.execute("SELECT user_id FROM books WHERE book_id = ?;", book_id)[0]["user_id"]
                    db.execute("INSERT INTO history (user_id, book_id, date, status) VALUES (?, ?, ?, 1);", user_id, book_id, datetime_status)
                    db.execute("UPDATE books SET status = 1, user_id = 0 WHERE book_id = ?;", book_id)
                #
            day += 1
    else:
        day = 1
        for d in range(0, 28):
            hours = 10
            for h in range(0, 3):
                minutes = choice(range(0, 60))
                seconds = choice(range(0, 60))
                datetime_status = datetime(year, month, day, hours, minutes, seconds)
                hours += 3
                #
                                # random book_id
                book_id = choice(books_id_list)

                # status of book_id
                status = db.execute("SELECT status FROM books WHERE book_id = ?", book_id)[0]["status"]
                # status == 1 - in library, status == 0 - borrowed
                # when book is in library any user can borrow
                if status == 1:
                    user_id = choice(users_id_list)

                    # add to history - default status == 0
                    db.execute("INSERT INTO history (user_id, book_id, date) VALUES (?, ?, ?);", user_id, book_id, datetime_status)
                    db.execute("UPDATE books SET status = 0, user_id = ? WHERE book_id = ?;", user_id, book_id)

                # when book is borrowed, only user which borrowed can return
                else:
                    user_id = db.execute("SELECT user_id FROM books WHERE book_id = ?;", book_id)[0]["user_id"]
                    db.execute("INSERT INTO history (user_id, book_id, date, status) VALUES (?, ?, ?, 1);", user_id, book_id, datetime_status)
                    db.execute("UPDATE books SET status = 1, user_id = 0 WHERE book_id = ?;", book_id)
                #
            day += 1
    month += 1