from flask import Flask, redirect, render_template, request, json, jsonify
from cs50 import SQL
from datetime import datetime
import json
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///library.db")

def check_books():
    db.execute("INSERT INTO users (first_name, last_name, email) VALUES ('Jan', 'Nowak', 'imejl');")

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(check_books,'interval',seconds=10)
scheduler.start()



@app.route("/")
def main():
    return render_template("index.html")


@app.route("/borrow", methods=["GET", "POST"])
def borrow():
    """Borrow a book from library"""
    if request.method == "POST":
        if not request.form.get("user_id") or not request.form.get("book_id"):
            return render_template("apology.html", message="You must provide User ID and Book ID")
        user_id = request.form.get("user_id")
        books_borrowed = db.execute("SELECT book_id FROM books WHERE user_id = ?;", user_id)

        # user can borrow max 3 books
        if len(books_borrowed) > 2:
            return render_template("apology.html", message="You can have a maximum of 3 books borrowed.")

        # user can not borrow book if he has a book not return on time
        books_borrowed_id_list = []
        dates_list = []
        for i in range(0, len(books_borrowed)):
            books_borrowed_id_list.append(books_borrowed[i]["book_id"])
            dates_list.append(db.execute("SELECT date FROM history WHERE book_id = ?;", books_borrowed[i]["book_id"]))
        today = datetime.now()

        max_borrow_days = 30
        for i in range(0, len(dates_list)):
            date_string = dates_list[i][len(dates_list[i]) - 1]["date"]
            date_obj = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            time_delta = today - date_obj
            if time_delta.days > max_borrow_days:
                return render_template("apology.html", message="You must first return the book(s) that you did not return on time.")

        # user can borrow a book
        book_id = request.form.get("book_id")
        book_status = db.execute("SELECT status FROM books WHERE book_id = ?;", book_id)[0]["status"]
        # book is already borrowed
        if book_status == 0:
            return render_template("apology.html", message="The book is already borrowed")

        # The book was borrowed correctly. Add history and update books db.
        datetime_status = today.strftime('%Y-%m-%d %H:%M:%S')
        db.execute("INSERT INTO history (user_id, book_id, date, status) VALUES (?, ?, ?, 0);", user_id, book_id, datetime_status)
        db.execute("UPDATE books SET status = 0, user_id = ? WHERE book_id = ?;", user_id, book_id)
        return redirect("/")
    else:
        return render_template("borrow.html")


@app.route("/returned", methods=["GET", "POST"])
def returned():
    """Return a book to library"""
    if request.method == "POST":
        book_id = request.form.get("book_id")
        book_status = db.execute("SELECT status FROM books WHERE book_id = ?;", book_id)[0]["status"]

        # check if book is borrowed
        if book_status == 1:
            # Book is in library
            return render_template("apology.html", message="Sorry, but you can't return a book that's in the library.")
        else:
            # book can be return - add record to history table and update books table
            datetime_status = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_id = db.execute("SELECT user_id FROM books WHERE book_id = ?;", book_id)[0]["user_id"]
            db.execute("INSERT INTO history (user_id, book_id, date, status) VALUES (?, ?, ?, 1);", user_id, book_id, datetime_status)
            db.execute("UPDATE books SET status = 1, user_id = 0 WHERE book_id = ?;", book_id)
            return redirect("/returned")
    else:
        return render_template("return.html")


@app.route("/report", methods=["GET", "POST"])
def report():
    """Create a borrowing report for 1 user or all users"""
    # create list of user id's
    user_list_dict = db.execute("SELECT user_id FROM users")
    user_list = []
    for user in user_list_dict:
        user_list.append(user["user_id"])

    if request.method == "POST":
        # check if user provide user_id
        if not request.form.get("user_id"):
            return render_template("apology.html", message="You must provide User ID")
        user_id = request.form.get("user_id")
        report_dict = {}
        user_list_fullname = []
        if user_id == "all_users":
            # create dict with each user fullname and list of borrowed books
            for user in user_list:
                # create list of full names
                user_row = db.execute("SELECT first_name, last_name FROM users WHERE user_id = ?;", user)
                user_fullname = user_row[0]["first_name"] + " " + user_row[0]["last_name"]
                user_list_fullname.append(user_fullname)\

                # create list of book titles
                books_id_list = db.execute("SELECT book_id FROM history WHERE (user_id = ? AND status = 0);", user)
                # check if user borrowed at least 1 book
                if len(books_id_list) == 0:
                    continue
                books_title_list = []
                for book in books_id_list:
                    new_book = db.execute("SELECT title FROM books WHERE book_id = ?;", book["book_id"])[0]["title"]
                    books_title_list.append(new_book)
                report_dict[user] = books_title_list
            return render_template("report.html", report_dict=report_dict, report_dict_len=len(report_dict), user_list_fullname=user_list_fullname)
        else:
            # create list of full names (in this case only 1 element)
            user_row = db.execute("SELECT first_name, last_name FROM users WHERE user_id = ?;", user_id)
            user_fullname = user_row[0]["first_name"] + " " + user_row[0]["last_name"]
            user_list_fullname.append(user_fullname)

            # create list of book titles
            books_id_list = db.execute("SELECT book_id FROM history WHERE (user_id = ? AND status = 0);", user_id)
            # check if user borrowed at least 1 book
            if len(books_id_list) == 0:
                    return render_template("apology.html", message="The user never borrowed any book.")
            books_title_list = []
            for book in books_id_list:
                new_book = db.execute("SELECT title FROM books WHERE book_id = ?;", book["book_id"])[0]["title"]
                books_title_list.append(new_book)
            return render_template("report.html", report_dict=books_title_list, report_dict_len=1, user_list_fullname=user_list_fullname)
    else:
        return render_template("generate.html", user_list=user_list)


@app.route("/rodo_choose")
def rodo_choose():
    """Export or import user to JSON"""
    return render_template("rodo_choose.html")


@app.route("/rodo_export", methods=["GET", "POST"])
def rodo_export():
    """Export to JSON"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        if not request.form.get("user_id"):
            return render_template("apology.html", message="You must provide User ID")
        user_data = db.execute("SELECT * FROM users WHERE user_id = ?;", user_id)
        if len(user_data) == 0:
            return render_template("apology.html", message="You must provide correct User ID")
        first_name = user_data[0]["first_name"]
        last_name = user_data[0]["last_name"]
        email = user_data[0]["email"]
        return jsonify(firstname=first_name,
                        lastname=last_name,
                        email=email)
    else:
        return render_template("rodo_export.html")


@app.route("/rodo_import", methods=["GET", "POST"])
def rodo_import():
    """Import user from JSON file"""
    if request.method == "POST":
        with open("rodo_import.json") as file:
             datastore = json.load(file)
        db.execute("INSERT INTO users (first_name, last_name, email) VALUES (?, ?, ?);", datastore["firstname"], datastore["lastname"], datastore["email"])
        return redirect("/")
    else:
        return render_template("rodo_import.html")

