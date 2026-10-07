from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "mawuli-secret-key-change-me"
DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Students table
    c.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        full_name TEXT NOT NULL,
        class_name TEXT,
        gender TEXT,
        guardian_phone TEXT
    )""")

    # PTA fees table
    c.execute("""CREATE TABLE IF NOT EXISTS pta_fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        amount REAL,
        payment_date TEXT,
        term TEXT,
        receipt_no TEXT
    )""")

    # Teacher attendance
    c.execute("""CREATE TABLE IF NOT EXISTS teacher_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_name TEXT,
        att_date TEXT,
        status TEXT
    )""")

    # Student attendance
    c.execute("""CREATE TABLE IF NOT EXISTS student_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        att_date TEXT,
        status TEXT
    )""")

    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM pta_fees")
    total_fees = c.fetchone()[0] or 0
    conn.close()
    return render_template("index.html", total_students=total_students, total_fees=total_fees)

# ---------- STUDENTS ----------
@app.route("/students", methods=["GET", "POST"])
def students():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if request.method == "POST":
        c.execute("INSERT INTO students (student_id, full_name, class_name, gender, guardian_phone) VALUES (?,?,?,?,?)",
                  (request.form["student_id"], request.form["full_name"],
                   request.form["class_name"], request.form["gender"],
                   request.form["guardian_phone"]))
        conn.commit()
        flash("Student added successfully!")
        return redirect(url_for("students"))
    c.execute("SELECT * FROM students ORDER BY full_name")
    all_students = c.fetchall()
    conn.close()
    return render_template("students.html", students=all_students)

# ---------- PTA FEES ----------
@app.route("/fees", methods=["GET", "POST"])
def fees():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if request.method == "POST":
        c.execute("INSERT INTO pta_fees (student_id, amount, payment_date, term, receipt_no) VALUES (?,?,?,?,?)",
                  (request.form["student_id"], request.form["amount"],
                   request.form["payment_date"], request.form["term"],
                   request.form["receipt_no"]))
        conn.commit()
        flash("Payment recorded!")
        return redirect(url_for("fees"))
    c.execute("""SELECT p.id, p.student_id, s.full_name, p.amount, p.payment_date, p.term, p.receipt_no
                 FROM pta_fees p LEFT JOIN students s ON p.student_id = s.student_id
                 ORDER BY p.payment_date DESC""")
    payments = c.fetchall()
    c.execute("SELECT student_id, full_name FROM students ORDER BY full_name")
    all_students = c.fetchall()
    conn.close()
    return render_template("fees.html", payments=payments, students=all_students)

# ---------- TEACHER ATTENDANCE ----------
@app.route("/teacher-attendance", methods=["GET", "POST"])
def teacher_attendance():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if request.method == "POST":
        c.execute("INSERT INTO teacher_attendance (teacher_name, att_date, status) VALUES (?,?,?)",
                  (request.form["teacher_name"], request.form["att_date"], request.form["status"]))
        conn.commit()
        flash("Teacher attendance recorded!")
        return redirect(url_for("teacher_attendance"))
    c.execute("SELECT * FROM teacher_attendance ORDER BY att_date DESC LIMIT 100")
    records = c.fetchall()
    conn.close()
    return render_template("teacher_attendance.html", records=records, today=date.today().isoformat())

# ---------- STUDENT ATTENDANCE ----------
@app.route("/student-attendance", methods=["GET", "POST"])
def student_attendance():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if request.method == "POST":
        c.execute("INSERT INTO student_attendance (student_id, att_date, status) VALUES (?,?,?)",
                  (request.form["student_id"], request.form["att_date"], request.form["status"]))
        conn.commit()
        flash("Student attendance recorded!")
        return redirect(url_for("student_attendance"))
    c.execute("""SELECT a.id, a.student_id, s.full_name, a.att_date, a.status
                 FROM student_attendance a LEFT JOIN students s ON a.student_id = s.student_id
                 ORDER BY a.att_date DESC LIMIT 100""")
    records = c.fetchall()
    c.execute("SELECT student_id, full_name FROM students ORDER BY full_name")
    all_students = c.fetchall()
    conn.close()
    return render_template("student_attendance.html", records=records, students=all_students, today=date.today().isoformat())

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
