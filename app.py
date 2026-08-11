from flask import Flask, render_template, request, redirect, url_for,session
from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysecretkey"



# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- STUDENT REGISTRATION ----------------

@app.route("/student_registration", methods=["GET", "POST"])
def student_registration():

    if request.method == "POST":

        fullname = request.form["fullname"]
        hostel_number = request.form["hostel_number"]
        email = request.form["email"]
        phone = request.form["phone"]
        gender = request.form["gender"]
        dob = request.form["dob"]
        department = request.form["department"]
        course = request.form["course"]
        year = request.form["year"]
       
        room = request.form["room"]
        
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        # Check if passwords match
        if password != confirm_password:
         return "❌ Password and Confirm Password do not match!"
        
        conn = get_connection()

        if conn is None:
            return "Database Connection Failed!"

        cursor = conn.cursor()
        sql = """
        INSERT INTO students
       (fullname, email, phone, gender, dob, department, course, year, room, hostel_number, password)
       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
       """
       

        

        values = (
            fullname,
            email,
            phone,
            gender,
            dob,
            department,
            course,
            year,
           
            room,
            hostel_number,
            password
        )

        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()

        return "✅ Student Registered Successfully"

    return render_template("student_registration.html")


# ---------------- STUDENT LOGIN ----------------


        
@app.route("/student_login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_connection()

        if conn is None:
            return "Database Connection Failed!"

        cursor = conn.cursor(dictionary=True, buffered=True)

        cursor.execute(
            "SELECT * FROM students WHERE email=%s AND password=%s",
            (email, password)
        )

        student = cursor.fetchone()

        cursor.close()
        conn.close()

        if student:
            session["student_id"] = student["id"]
            session["student_name"] = student["fullname"]
            return redirect(url_for("student_dashboard"))
        else:
            return "❌ Invalid Email or Password"

    return render_template("student_login.html")
@app.route("/forgot_password", methods=["GET","POST"])
def forgot_password():

    if request.method=="POST":

        email=request.form["email"]

        con=get_connection()
        cursor=con.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE email=%s",
            (email,)
        )

        student=cursor.fetchone()

        if student:
            session["reset_email"]=email
            return redirect(url_for("reset_password"))

        else:
            return "Email not found"

    return render_template("forgot_password.html")







# ---------------- STUDENT DASHBOARD ----------------

@app.route("/student_dashboard")
def student_dashboard():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor(dictionary=True)

    # Get all complaints of logged-in student
    cursor.execute(
        "SELECT * FROM complaints WHERE student_id=%s ORDER BY complaint_date DESC",
        (student_id,)
    )
    complaints = cursor.fetchall()

    # Total complaints
    cursor.execute(
        "SELECT COUNT(*) AS total FROM complaints WHERE student_id=%s",
        (student_id,)
    )
    total = cursor.fetchone()["total"]

    # Pending complaints
    cursor.execute(
        "SELECT COUNT(*) AS pending FROM complaints WHERE student_id=%s AND status='Pending'",
        (student_id,)
    )
    pending = cursor.fetchone()["pending"]

    # Completed complaints
    cursor.execute(
        "SELECT COUNT(*) AS completed FROM complaints WHERE student_id=%s AND status='Completed'",
        (student_id,)
    )
    completed = cursor.fetchone()["completed"]

    # In Progress complaints
    cursor.execute(
        "SELECT COUNT(*) AS progress FROM complaints WHERE student_id=%s AND status='In Progress'",
        (student_id,)
    )
    progress = cursor.fetchone()["progress"]

    cursor.close()
    conn.close()

    student = {
        "fullname": session["student_name"]
    }

    return render_template(
        "student_dashboard.html",
        student=student,
        complaints=complaints,
        total=total,
        pending=pending,
        completed=completed,
        progress=progress
    )





 



       
    
    
   


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_connection()

        if conn is None:
            return "Database Connection Failed!"

        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )

        admin = cursor.fetchone()

        if admin:

            # Previous Login Time
            session["previous_login"] = str(admin["last_login"]) if admin["last_login"] else "First Login"

            # Update Current Login Time
            cursor.execute(
                "UPDATE admin SET last_login = NOW() WHERE id=%s",
                (admin["id"],)
            )

            conn.commit()

            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]

            cursor.close()
            conn.close()

            return redirect(url_for("admin_dashboard"))

        else:
            cursor.close()
            conn.close()
            return "❌ Invalid Username or Password"

    return render_template("admin_login.html")
        
# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin_dashboard")
def admin_dashboard():
    
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor(dictionary=True)

    # Get all complaints
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    # Count total complaints
    cursor.execute("SELECT COUNT(*) AS total FROM complaints")
    total = cursor.fetchone()["total"]

    # Count pending complaints
    cursor.execute(
        "SELECT COUNT(*) AS pending FROM complaints WHERE status='Pending'"
    )
    pending = cursor.fetchone()["pending"]

    # Count completed complaints
    cursor.execute(
        "SELECT COUNT(*) AS completed FROM complaints WHERE status='Completed'"
    )
    completed = cursor.fetchone()["completed"]
    # Count In Progress complaints
    cursor.execute(
    "SELECT COUNT(*) AS progress FROM complaints WHERE status='In Progress'"
    )
    progress = cursor.fetchone()["progress"]
    
    

    

    cursor.close()
    conn.close()
    return render_template(
    "admin_dashboard.html",
    complaints=complaints,
    total=total,
    pending=pending,
    completed=completed,
    progress=progress,
    previous_login=session.get("previous_login")
)

   


# ---------------- RAISE COMPLAINT ----------------

@app.route("/raise_complaint")
def raise_complaint():
    return render_template("raise_complaint.html")


# ---------------- SUBMIT COMPLAINT ----------------
@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]
    name = session["student_name"]

    room = request.form.get("room")
    category = request.form.get("category")
    subject = request.form.get("subject")
    description = request.form.get("description")

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO complaints
        (student_id, name, room, category, subject, description, complaint_date)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """,
    (
        student_id,
        name,
        room,
        category,
        subject,
        description
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("student_dashboard"))
    
    

# ---------------- VIEW COMPLAINTS ----------------

@app.route("/view_complaints")
def view_complaints():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]
    print("Student ID:", student_id)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM complaints WHERE student_id=%s",
        (student_id,)
    )

    complaints = cursor.fetchall()
    print(complaints)

    cursor.close()
    conn.close()

    return render_template("view_complaints.html", complaints=complaints)

    

# ---------------- UPDATE COMPLAINT STATUS ----------------

@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):

    status = request.form.get("status")

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status=%s WHERE id=%s",
        (status, id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin_dashboard")
@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    fullname = request.form["fullname"]
    email = request.form["email"]
    phone = request.form["phone"]
    room = request.form["room"]

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET fullname=%s,
            email=%s,
            phone=%s,
            room=%s
        WHERE id=%s
    """, (
        fullname,
        email,
        phone,
        room,
        session["student_id"]
    ))

    conn.commit()

    cursor.close()
    conn.close()

    session["student_name"] = fullname

    return redirect(url_for("profile"))

# ---------------- MANAGE NOTICES ----------------

@app.route("/manage_notices")
def manage_notices():

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM notices
        ORDER BY notice_date DESC
    """)

    notices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "manage_notices.html",
        notices=notices
    )

# ---------------- DELETE COMPLAINT ----------------

@app.route("/delete_complaint/<int:id>")
def delete_complaint(id):

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM complaints WHERE id=%s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin_dashboard")
# ---------------- ADD NOTICE ----------------
@app.route("/add_notice")
def add_notice():
    return render_template("add_notice.html")



# ---------------- SAVE NOTICE ----------------

@app.route("/save_notice", methods=["POST"])
def save_notice():

    try:
        title = request.form["title"]
        message = request.form["message"]

        conn = get_connection()

        if conn is None:
            return "Database Connection Failed!"

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO notices(title, message)
            VALUES(%s,%s)
        """,(title,message))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("manage_notices"))

    except Exception as e:
        return f"ERROR: {e}"




# ---------------- COMPLETE COMPLAINT ----------------
@app.route("/complete_complaint/<int:id>")
def complete_complaint(id):

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE complaints
        SET status='Completed'
        WHERE id=%s
        """,
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("admin_dashboard"))




# ---------------- NOTICE BOARD ----------------

@app.route("/notice_board")
def notice_board():

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM notices
        ORDER BY notice_date DESC
    """)

    notices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notice_board.html",
        notices=notices
    )




    
    
    


# ---------------- PROFILE ----------------


@app.route("/profile")
def profile():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (session["student_id"],)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "profile.html",
        student=student
    )
@app.route("/edit_profile")
def edit_profile():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (session["student_id"],)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_profile.html",
        student=student
    )

# ---------------- CHANGE PASSWORD ----------------

@app.route("/change_password", methods=["GET","POST"])
def change_password():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    if request.method == "POST":

        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        conn = get_connection()
        cursor = conn.cursor()

        # check old password
        cursor.execute(
            "SELECT password FROM students WHERE id=%s",
            (session["student_id"],)
        )

        result = cursor.fetchone()

        if result and result[0] == old_password:

            cursor.execute(
                "UPDATE students SET password=%s WHERE id=%s",
                (new_password, session["student_id"])
            )

            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for("student_dashboard"))

        else:
            cursor.close()
            conn.close()

            return "Old password incorrect"

    return render_template("change_password.html")
@app.route("/complaint/<int:id>")
def complaint_details(id):

    if "student_id" not in session and "admin_id" not in session:
        return redirect(url_for("student_login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM complaints
        WHERE id=%s
    """, (id,))

    complaint = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "complaint_details.html",
        complaint=complaint
    )



# ---------------- UPDATE PASSWORD ----------------

@app.route("/update_password", methods=["POST"])
def update_password():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    confirm_password = request.form["confirm_password"]

    if new_password != confirm_password:
        return "❌ New Password and Confirm Password do not match!"

    conn = get_connection()

    if conn is None:
        return "Database Connection Failed!"

    cursor = conn.cursor(dictionary=True)

    # Check current password
    cursor.execute(
        "SELECT * FROM students WHERE id=%s AND password=%s",
        (student_id, current_password)
    )

    student = cursor.fetchone()

    if student is None:
        cursor.close()
        conn.close()
        return "❌ Current Password is incorrect!"

    # Update password
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE students SET password=%s WHERE id=%s",
        (new_password, student_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return "✅ Password Updated Successfully! Please login with new password."

@app.route("/admin_logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))
# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():



    session.clear()

    return redirect(url_for("home"))
# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)
   
    




      






    

    