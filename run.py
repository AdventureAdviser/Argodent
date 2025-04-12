from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.permanent_session_lifetime = timedelta(days=7)
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'clinic.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS specialists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        photo TEXT,
        description TEXT,
        id_position INTEGER,
        FOREIGN KEY (id_position) REFERENCES positions(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cost INTEGER NOT NULL,
        description TEXT,
        photo TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        specialist_id INTEGER NOT NULL,
        service_id INTEGER NOT NULL,
        appointment_datetime TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (specialist_id) REFERENCES specialists(id),
        FOREIGN KEY (service_id) REFERENCES services(id)
    )
    ''')
    conn.commit()
    conn.close()

def seed_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM positions")
    if cur.fetchone()[0] == 0:
        positions = [
            "Главный врач, Стоматолог-хирург",
            "Врач-стоматолог, Терапевт",
            "Врач-стоматолог, Хирург",
            "Врач-стоматолог, Ортодонт",
            "Врач-стоматолог, Пародонтолог",
            "Врач-стоматолог, Ортопед",
            "Врач-стоматолог, Имплантолог",
            "Врач-стоматолог, Педиатр",
            "Врач-стоматолог, Эстетист"
        ]
        for pos in positions:
            cur.execute("INSERT INTO positions (name) VALUES (?)", (pos,))
    cur.execute("SELECT COUNT(*) FROM specialists")
    if cur.fetchone()[0] == 0:
        def get_position_id(name):
            cur.execute("SELECT id FROM positions WHERE name = ?", (name,))
            return cur.fetchone()[0]
        specialists_data = [
            ("Иванов Иван Иванович", "Главный врач, Стоматолог-хирург", "images/specialists/ivanov.jpg",
             "Главный врач клиники, обладающий обширным опытом в области стоматологии и хирургии."),
            ("Петрова Екатерина Сергеевна", "Врач-стоматолог, Терапевт", "images/specialists/petrova.jpg",
             "Врач-стоматолог с акцентом на терапевтическое лечение и индивидуальный подход к каждому пациенту."),
            ("Смирнов Дмитрий Александрович", "Врач-стоматолог, Хирург", "images/specialists/smirnov.jpg",
             "Хирург с глубокими знаниями и опытом проведения сложных стоматологических операций."),
            ("Сидорова Наталья Викторовна", "Врач-стоматолог, Ортодонт", "images/specialists/sidorova.jpg",
             "Специалист в области ортодонтии, предлагающая современные методы коррекции прикуса."),
            ("Кузнецова Ирина Валерьевна", "Врач-стоматолог, Терапевт", "images/specialists/kuznetsova.jpg",
             "Врач-стоматолог с акцентом на терапевтическое лечение и качественное обслуживание."),
            ("Морозов Алексей Дмитриевич", "Врач-стоматолог, Пародонтолог", "images/specialists/morozov.jpg",
             "Опытный специалист в области пародонтологии, следящий за последними тенденциями в лечении десен."),
            ("Лебедева Мария Владимировна", "Врач-стоматолог, Хирург", "images/specialists/lebedeva.jpg",
             "Хирург с впечатляющим опытом и высокой квалификацией в проведении стоматологических операций."),
            ("Григорьева Ольга Борисовна", "Врач-стоматолог, Ортопед", "images/specialists/grigorieva.jpg",
             "Специалист-ортопед, уделяющая особое внимание комфорту пациентов и качеству протезирования."),
            ("Никитин Александр Михайлович", "Врач-стоматолог, Имплантолог", "images/specialists/nikitin.jpg",
             "Имплантолог с многолетним опытом установки зубных имплантатов."),
            ("Васильева Татьяна Игоревна", "Врач-стоматолог, Педиатр", "images/specialists/vasilieva.jpg",
             "Педиатр в области стоматологии, создающая комфортные условия для маленьких пациентов."),
            ("Ковалев Сергей Владимирович", "Врач-стоматолог, Эстетист", "images/specialists/kovalev.jpg",
             "Эстетист, специализирующийся на улучшении внешнего вида улыбки с использованием современных методик."),
            ("Федорова Алёна Павловна", "Врач-стоматолог, Терапевт", "images/specialists/fedorova.jpg",
             "Врач-стоматолог с опытом в терапевтическом лечении, обеспечивающая высокое качество ухода за полостью рта."),
            ("Дмитриева Оксана Сергеевна", "Врач-стоматолог, Ортодонт", "images/specialists/dmitrieva.jpg",
             "Ортодонт с акцентом на современные методы коррекции прикуса и выравнивания зубов."),
            ("Чистякова Валерия Анатольевна", "Врач-стоматолог, Пародонтолог", "images/specialists/chistyakova.jpg",
             "Пародонтолог, уделяющая внимание профилактике и лечению заболеваний десен."),
            ("Чернов Артем Павлович", "Врач-стоматолог, Хирург", "images/specialists/chernov.jpg",
             "Хирург, известный своими точными и безопасными стоматологическими операциями.")
        ]
        for full_name, position_name, photo, description in specialists_data:
            parts = full_name.split()
            lastname = parts[0]
            firstname = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
            pos_id = get_position_id(position_name)
            cur.execute("INSERT INTO specialists (firstname, lastname, photo, description, id_position) VALUES (?, ?, ?, ?, ?)",
                        (firstname, lastname, photo, description, pos_id))
    cur.execute("SELECT COUNT(*) FROM services")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO services (name, cost, description, photo) VALUES (?, ?, ?, ?)",
                    ("Профилактика", 2000, "Профилактический осмотр и чистка.", "https://via.placeholder.com/400x300?text=Профилактика"))
        cur.execute("INSERT INTO services (name, cost, description, photo) VALUES (?, ?, ?, ?)",
                    ("Лечение кариеса", 3500, "Лечение кариеса с пломбированием.", "https://via.placeholder.com/400x300?text=Лечение+кариеса"))
        cur.execute("INSERT INTO services (name, cost, description, photo) VALUES (?, ?, ?, ?)",
                    ("Отбеливание", 5000, "Отбеливание зубов профессиональными средствами.", "https://via.placeholder.com/400x300?text=Отбеливание"))
    conn.commit()
    conn.close()

init_db()
seed_db()

def get_specialists():
    conn = get_db_connection()
    specialists = conn.execute("SELECT s.id, s.firstname, s.lastname, s.photo, s.description, p.name as position FROM specialists s JOIN positions p ON s.id_position = p.id").fetchall()
    conn.close()
    return specialists

def get_services():
    conn = get_db_connection()
    services = conn.execute("SELECT * FROM services").fetchall()
    conn.close()
    return services

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    services_list = get_services()
    return render_template('services.html', services=services_list)

@app.route('/specialists')
def specialists_page():
    specialists_list = get_specialists()
    return render_template('specialists.html', specialists=specialists_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        if not fullname or not email or not phone or not password:
            flash('Все поля обязательны', 'error')
            return redirect(url_for('register'))
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (fullname, email, phone, password) VALUES (?, ?, ?, ?)', (fullname, email, phone, password))
            conn.commit()
            flash('Регистрация прошла успешно! Теперь войдите в систему.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('cabinet'))
    if request.method == 'POST':
        login_input = request.form.get('login')
        password = request.form.get('password')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE (email = ? OR phone = ?) AND password = ?', (login_input, login_input, password)).fetchone()
        conn.close()
        if user:
            session.permanent = True
            session['user_id'] = user['id']
            session['user_fullname'] = user['fullname']
            flash('Вы успешно вошли', 'success')
            return redirect(url_for('cabinet'))
        else:
            flash('Неверные данные', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/cabinet', methods=['GET', 'POST'])
def cabinet():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        if not fullname or not email or not phone:
            flash('Все поля обязательны для обновления', 'error')
            return redirect(url_for('cabinet'))
        try:
            conn.execute('UPDATE users SET fullname = ?, email = ?, phone = ? WHERE id = ?', (fullname, email, phone, session['user_id']))
            conn.commit()
            session['user_fullname'] = fullname
            flash('Данные успешно обновлены', 'success')
        except sqlite3.IntegrityError:
            flash('Ошибка обновления данных. Возможно, email уже используется', 'error')
            return redirect(url_for('cabinet'))
    appointments = conn.execute('''
        SELECT a.id, a.appointment_datetime, 
               s.firstname || ' ' || s.lastname as specialist_name,
               srv.name as service_name
        FROM appointments a
        JOIN specialists s ON a.specialist_id = s.id
        JOIN services srv ON a.service_id = srv.id
        WHERE a.user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('cabinet.html', user=user, appointments=appointments)

@app.route('/appointment', endpoint='appointment')
def appointment_start():
    session.pop('appointment', None)
    return redirect(url_for('appointment_specialist'))

@app.route('/appointment/specialist', methods=['GET', 'POST'])
def appointment_specialist():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему для записи', 'error')
        return redirect(url_for('login'))
    specialists_list = get_specialists()
    if request.method == 'POST':
        specialist_id = request.form.get('specialist')
        if not specialist_id:
            flash("Выберите специалиста", "error")
            return redirect(url_for('appointment_specialist'))
        selected = next((dict(s) for s in specialists_list if str(s["id"]) == specialist_id), None)
        if selected:
            session['appointment'] = {}
            session['appointment']['specialist'] = selected
            session.modified = True
            return redirect(url_for('appointment_service'))
        else:
            flash("Неверный выбор", "error")
    return render_template('appointment_specialist.html', specialists=specialists_list)

@app.route('/appointment/service', methods=['GET', 'POST'])
def appointment_service():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему для записи', 'error')
        return redirect(url_for('login'))
    if 'appointment' not in session or 'specialist' not in session['appointment']:
        flash('Сначала выберите специалиста', 'error')
        return redirect(url_for('appointment_specialist'))
    services_list = get_services()
    if request.method == 'POST':
        service_id = request.form.get('service')
        if not service_id:
            flash("Выберите услугу", "error")
            return redirect(url_for('appointment_service'))
        selected = next((dict(s) for s in services_list if str(s["id"]) == service_id), None)
        if selected:
            appointment = session.get('appointment', {})
            appointment['service'] = selected
            session['appointment'] = appointment
            session.modified = True
            return redirect(url_for('appointment_datetime'))
        else:
            flash("Неверный выбор", "error")
    return render_template('appointment_service.html', services=services_list)

@app.route('/appointment/datetime', methods=['GET', 'POST'])
def appointment_datetime():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему для записи', 'error')
        return redirect(url_for('login'))
    if 'appointment' not in session or 'service' not in session['appointment']:
        flash('Сначала выберите услугу', 'error')
        return redirect(url_for('appointment_service'))
    if request.method == 'POST':
        datetime_value = request.form.get('appointment_datetime')
        if not datetime_value:
            flash("Укажите дату и время", "error")
            return redirect(url_for('appointment_datetime'))
        appointment_data = session.get('appointment')
        specialist_id = appointment_data['specialist']['id']
        service_id = appointment_data['service']['id']
        conn = get_db_connection()
        conn.execute('INSERT INTO appointments (user_id, specialist_id, service_id, appointment_datetime) VALUES (?, ?, ?, ?)', (session['user_id'], specialist_id, service_id, datetime_value))
        conn.commit()
        conn.close()
        session.pop('appointment', None)
        flash("Запись успешно оформлена!", "success")
        return redirect(url_for('cabinet'))
    return render_template('appointment_datetime.html')

@app.route('/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    appointment = conn.execute('SELECT * FROM appointments WHERE id = ? AND user_id = ?', (appointment_id, session['user_id'])).fetchone()
    if appointment:
        conn.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
        conn.commit()
        flash('Запись успешно отменена', 'success')
    else:
        flash('Запись не найдена или доступ запрещен', 'error')
    conn.close()
    return redirect(url_for('cabinet'))

@app.route('/reschedule_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def reschedule_appointment(appointment_id):
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в систему', 'error')
        return redirect(url_for('login'))
    conn = get_db_connection()
    appointment = conn.execute('SELECT * FROM appointments WHERE id = ? AND user_id = ?', (appointment_id, session['user_id'])).fetchone()
    if not appointment:
        conn.close()
        flash('Запись не найдена или доступ запрещен', 'error')
        return redirect(url_for('cabinet'))
    if request.method == 'POST':
        new_datetime = request.form.get('appointment_datetime')
        if not new_datetime:
            flash('Новая дата и время обязательны', 'error')
            return redirect(url_for('reschedule_appointment', appointment_id=appointment_id))
        conn.execute('UPDATE appointments SET appointment_datetime = ? WHERE id = ?', (new_datetime, appointment_id))
        conn.commit()
        conn.close()
        flash('Запись успешно перенесена', 'success')
        return redirect(url_for('cabinet'))
    conn.close()
    return render_template('reschedule.html', appointment=appointment)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)