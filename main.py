from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

app = Flask(__name__)

def create_database():
    conn = sqlite3.connect('employee.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dob TEXT,
            department TEXT,
            salary REAL
        )
    ''')
    conn.commit()
    conn.close()

create_database()  # Create the database if it doesn't exist

@app.route('/')
def index():
    conn = sqlite3.connect('employee.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    conn.close()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        department = request.form['department']
        salary = request.form['salary']

        try:
            datetime.datetime.strptime(dob, '%Y-%m-%d')
            conn = sqlite3.connect('employee.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO employees (name, dob, department, salary) VALUES (?, ?, ?, ?)", (name, dob, department, salary))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))  # Redirect to the main page
        except ValueError:
            return render_template('add.html', error="Invalid date format. Use YYYY-MM-DD.")
        except Exception as e:  # Catch any other exception
            return render_template('add.html', error=f"Error adding employee: {e}")

    return render_template('add.html')  # Render the add employee form


@app.route('/search', methods=['GET', 'POST'])
def search_employee():
    if request.method == 'POST':
        search_term = request.form['search']
        conn = sqlite3.connect('employee.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE name LIKE ? OR department LIKE ?", ('%' + search_term + '%', '%' + search_term + '%'))
        employees = cursor.fetchall()
        conn.close()
        return render_template('index.html', employees=employees, search_term=search_term) #Pass search term to the template
    return render_template('search.html')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_employee(id):
    conn = sqlite3.connect('employee.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        department = request.form['department']
        salary = request.form['salary']

        try:
            datetime.datetime.strptime(dob, '%Y-%m-%d') #Validate date format
            cursor.execute("UPDATE employees SET name=?, dob=?, department=?, salary=? WHERE id=?", (name, dob, department, salary, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except ValueError:
            return render_template('update.html', error="Invalid date format. Use YYYY-MM-DD.", employee=employee) #Pass error message and current employee data
        except Exception as e:
            return render_template('update.html', error=f"Error updating employee: {e}", employee=employee)

    cursor.execute("SELECT * FROM employees WHERE id=?", (id,)) #Get current employee data
    employee = cursor.fetchone()
    conn.close()
    return render_template('update.html', employee=employee) #Pass current data to the template


@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    conn = sqlite3.connect('employee.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM employees WHERE id=?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting employee: {e}")  # Print error to console (for debugging)
    finally:
        conn.close()
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
