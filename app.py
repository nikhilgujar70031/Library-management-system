from flask import Flask, render_template, request, redirect, url_for, session
import os
import secrets
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")
)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_database()


@app.route("/")
def index():
    conn = get_db()

    total_books = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    available_books = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM books"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_books=total_books,
        available_books=available_books
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            return redirect(url_for("index"))

        error = "Invalid username or password. Try admin / admin123"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/add", methods=["GET", "POST"])
def add_book():

    if request.method == "POST":
        name = request.form["name"]
        author = request.form["author"]
        quantity = request.form["quantity"]

        conn = get_db()

        conn.execute(
            "INSERT INTO books (name, author, quantity) VALUES (?, ?, ?)",
            (name, author, quantity)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("books"))

    return render_template("add_book.html")


@app.route("/books")
def books():

    search = request.args.get("search", "")

    conn = get_db()

    if search:
        books = conn.execute(
            """
            SELECT * FROM books
            WHERE name LIKE ? OR author LIKE ?
            """,
            ("%" + search + "%", "%" + search + "%")
        ).fetchall()
    else:
        books = conn.execute(
            "SELECT * FROM books"
        ).fetchall()

    conn.close()

    return render_template(
        "books.html",
        books=books,
        search=search
    )


@app.route("/issue/<int:book_id>")
def issue_book(book_id):

    conn = get_db()

    book = conn.execute(
        "SELECT quantity FROM books WHERE id = ?",
        (book_id,)
    ).fetchone()

    if book and book["quantity"] > 0:
        conn.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE id = ?",
            (book_id,)
        )

    conn.commit()
    conn.close()

    return redirect(url_for("books"))


@app.route("/return/<int:book_id>")
def return_book(book_id):

    conn = get_db()

    conn.execute(
        "UPDATE books SET quantity = quantity + 1 WHERE id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("books"))


@app.route("/delete/<int:book_id>")
def delete_book(book_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("books"))


if __name__ == "__main__":
    app.run(debug=True)