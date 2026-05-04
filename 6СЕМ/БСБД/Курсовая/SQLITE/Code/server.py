import sqlite3
import hashlib
import threading
import os
import uuid
import time
import shutil
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "server.db"
BACKUP_DIR = "backups"
SESSION_TIMEOUT = 30

os.makedirs(BACKUP_DIR, exist_ok=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_token(token):
    if not token:
        return None
    db = get_db()
    row = db.execute("SELECT user_id FROM sessions WHERE token = ?", (token,)).fetchone()
    return row['user_id'] if row else None

def log_event(user_id, action, details=""):
    db = get_db()
    db.execute("INSERT INTO event_log (user_id, action, details) VALUES (?, ?, ?)",
               (user_id, action, details))
    db.commit()

# ---------- Резервное копирование ----------
def backup_databases():
    while True:
        try:
            db = get_db()
            schedules = db.execute("SELECT * FROM backup_schedules").fetchall()
            now = datetime.now()
            for s in schedules:
                last_bkp = s['last_backup']
                if last_bkp:
                    last_time = datetime.strptime(last_bkp, "%Y-%m-%d %H:%M:%S")
                    if (now - last_time).total_seconds() < s['interval_seconds']:
                        continue
                database = db.execute("SELECT * FROM databases WHERE id = ?", (s['database_id'],)).fetchone()
                if not database or not os.path.isfile(database['path']):
                    continue
                backup_name = f"{database['name']}_{now.strftime('%Y%m%d_%H%M%S')}.db"
                backup_path = os.path.join(BACKUP_DIR, backup_name)
                shutil.copy2(database['path'], backup_path)
                db.execute("UPDATE backup_schedules SET last_backup = ? WHERE database_id = ?",
                           (now.strftime("%Y-%m-%d %H:%M:%S"), s['database_id']))
                db.commit()
                log_event(None, "backup", f"Бэкап базы {database['name']} сохранён как {backup_name}")
        except Exception as e:
            print(f"Backup error: {e}")
        time.sleep(1)

# ---------- Консоль ----------
def admin_menu():
    while True:
        print("\n=== СЕРВЕР АДМИНИСТРАТОРА ===")
        print("1. Управление пользователями")
        print("2. Управление базами данных")
        print("3. Управление резервным копированием")
        print("4. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            manage_users()
        elif choice == "2":
            manage_databases()
        elif choice == "3":
            manage_backups()
        elif choice == "4":
            print("Остановка сервера...")
            os._exit(0)
        else:
            print("Неверный ввод")

def manage_users():
    while True:
        print("\n--- Пользователи ---")
        db = get_db()
        users = db.execute("SELECT * FROM users").fetchall()
        for u in users:
            print(f"ID: {u['id']}, Логин: {u['username']}, Роль: {u['role']}")
        print("\n1. Добавить пользователя")
        print("2. Удалить пользователя")
        print("3. Управление правами доступа")
        print("4. Назад")
        choice = input("> ").strip()
        if choice == "1":
            username = input("Логин: ").strip()
            password = input("Пароль: ").strip()
            role = input("Роль (admin/user): ").strip()
            if role not in ("admin", "user"):
                print("Роль может быть только admin или user")
                continue
            db = get_db()
            try:
                db.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, hash_password(password), role))
                db.commit()
                print("Пользователь создан.")
            except sqlite3.IntegrityError:
                print("Пользователь с таким логином уже существует.")
        elif choice == "2":
            user_id = input("ID пользователя для удаления: ").strip()
            if not user_id.isdigit():
                print("Некорректный ID")
                continue
            db = get_db()
            db.execute("DELETE FROM users WHERE id = ?", (int(user_id),))
            db.execute("DELETE FROM permissions WHERE user_id = ?", (int(user_id),))
            db.execute("DELETE FROM sessions WHERE user_id = ?", (int(user_id),))
            db.commit()
            print("Пользователь удалён.")
        elif choice == "3":
            manage_permissions()
        elif choice == "4":
            break
        else:
            print("Неверный ввод")

def manage_permissions():
    user_id = input("ID пользователя: ").strip()
    if not user_id.isdigit():
        print("Некорректный ID")
        return
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (int(user_id),)).fetchone()
    if not user:
        print("Пользователь не найден")
        return
    print(f"Права для пользователя: {user['username']}")
    databases = db.execute("SELECT * FROM databases").fetchall()
    for d in databases:
        perm = db.execute("SELECT * FROM permissions WHERE user_id = ? AND database_id = ?",
                          (int(user_id), d['id'])).fetchone()
        can_view = bool(perm['can_view']) if perm else False
        can_edit = bool(perm['can_edit']) if perm else False
        can_add  = bool(perm['can_add']) if perm else False
        print(f"База ID {d['id']} ({d['name']}): просмотр={can_view}, изм={can_edit}, добав={can_add}")
    db_id = input("ID базы для изменения прав (Enter - отмена): ").strip()
    if not db_id.isdigit():
        return
    db_id = int(db_id)
    base = db.execute("SELECT * FROM databases WHERE id = ?", (db_id,)).fetchone()
    if not base:
        print("База не найдена")
        return
    can_view = input("Разрешить просмотр? (y/n): ").strip().lower() == 'y'
    can_edit = input("Разрешить изменение? (y/n): ").strip().lower() == 'y'
    can_add  = input("Разрешить добавление? (y/n): ").strip().lower() == 'y'

    existing = db.execute("SELECT * FROM permissions WHERE user_id = ? AND database_id = ?",
                          (int(user_id), db_id)).fetchone()
    if existing:
        db.execute("UPDATE permissions SET can_view=?, can_edit=?, can_add=? WHERE user_id=? AND database_id=?",
                   (int(can_view), int(can_edit), int(can_add), int(user_id), db_id))
    else:
        db.execute("INSERT INTO permissions (user_id, database_id, can_view, can_edit, can_add) VALUES (?, ?, ?, ?, ?)",
                   (int(user_id), db_id, int(can_view), int(can_edit), int(can_add)))
    db.commit()
    print("Права обновлены.")

def manage_databases():
    while True:
        print("\n--- Базы данных ---")
        db = get_db()
        databases = db.execute("SELECT * FROM databases").fetchall()
        for d in databases:
            print(f"ID: {d['id']}, Имя: {d['name']}, Путь: {d['path']}")
        print("\n1. Добавить базу данных")
        print("2. Удалить базу из списка")
        print("3. Назад")
        choice = input("> ").strip()
        if choice == "1":
            name = input("Наименование базы (для списка): ").strip()
            path = input("Полный путь к файлу .db: ").strip()
            if not os.path.isfile(path):
                print("Файл не найден. Проверьте путь.")
                continue
            db = get_db()
            try:
                db.execute("INSERT INTO databases (name, path) VALUES (?, ?)", (name, path))
                db.commit()
                print("База добавлена.")
            except sqlite3.IntegrityError:
                print("База с таким именем уже существует.")
        elif choice == "2":
            db_id = input("ID базы для удаления из списка (файл останется): ").strip()
            if not db_id.isdigit():
                print("Некорректный ID")
                continue
            db = get_db()
            db.execute("DELETE FROM databases WHERE id = ?", (int(db_id),))
            db.execute("DELETE FROM permissions WHERE database_id = ?", (int(db_id),))
            db.commit()
            print("База удалена из списка.")
        elif choice == "3":
            break
        else:
            print("Неверный ввод")

def manage_backups():
    while True:
        print("\n--- Управление резервным копированием ---")
        db = get_db()
        databases = db.execute("SELECT * FROM databases").fetchall()
        for d in databases:
            sched = db.execute("SELECT * FROM backup_schedules WHERE database_id = ?", (d['id'],)).fetchone()
            interval = sched['interval_seconds'] if sched else 180
            print(f"База {d['id']} ({d['name']}): интервал {interval} сек")
        print("\n1. Изменить интервал для базы")
        print("2. Назад")
        choice = input("> ").strip()
        if choice == "1":
            db_id = input("ID базы: ").strip()
            if not db_id.isdigit():
                print("Некорректный ID")
                continue
            interval = input("Интервал в секундах (мин. 10): ").strip()
            if not interval.isdigit() or int(interval) < 10:
                print("Некорректный интервал")
                continue
            interval = int(interval)
            db = get_db()
            db.execute("REPLACE INTO backup_schedules (database_id, interval_seconds) VALUES (?, ?)",
                       (int(db_id), interval))
            db.commit()
            print("Интервал обновлён.")
        elif choice == "2":
            break
        else:
            print("Неверный ввод")

# ========== API ==========
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or user['password_hash'] != hash_password(password):
        log_event(None, "login_failed", f"Попытка входа {username}")
        return jsonify({'success': False, 'message': 'Неверный логин или пароль'}), 401

    existing = db.execute("SELECT * FROM sessions WHERE user_id = ?", (user['id'],)).fetchone()
    if existing:
        last_ping = existing['last_ping']
        try:
            last_ping_time = datetime.strptime(last_ping, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last_ping_time).total_seconds() > SESSION_TIMEOUT:
                db.execute("DELETE FROM sessions WHERE user_id = ?", (user['id'],))
                db.commit()
            else:
                log_event(user['id'], "login_blocked", "Сессия уже активна")
                return jsonify({'success': False, 'message': 'Уже есть активная сессия'}), 409
        except:
            db.execute("DELETE FROM sessions WHERE user_id = ?", (user['id'],))
            db.commit()

    token = str(uuid.uuid4())
    db.execute("INSERT INTO sessions (user_id, token, last_ping) VALUES (?, ?, datetime('now'))",
               (user['id'], token))
    db.commit()
    log_event(user['id'], "login", f"Вход пользователя {username}")
    return jsonify({'success': True, 'user_id': user['id'], 'role': user['role'], 'token': token})

@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    token = data.get('token')
    if token:
        db = get_db()
        user_id = get_user_by_token(token)
        if user_id:
            log_event(user_id, "logout", "Выход из системы")
        db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        db.commit()
    return jsonify({'success': True})

@app.route('/ping', methods=['POST'])
def ping():
    data = request.json
    token = data.get('token')
    if not token:
        return jsonify({'success': False, 'message': 'Токен обязателен'}), 400
    db = get_db()
    db.execute("UPDATE sessions SET last_ping = datetime('now') WHERE token = ?", (token,))
    db.commit()
    return jsonify({'success': True})

@app.route('/databases', methods=['GET'])
def list_databases():
    token = request.args.get('token')
    user_id = get_user_by_token(token)
    if not user_id:
        return jsonify({'error': 'Недействительный токен'}), 403
    db = get_db()
    user = db.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return jsonify([])

    databases = []
    if user['role'] == 'admin':
        databases = db.execute("SELECT * FROM databases").fetchall()
        # Виртуальная база "Журнал событий"
        databases.append({
            "id": -1,
            "name": "Журнал событий",
            "path": "",
            "can_view": True,
            "can_edit": False,
            "can_add": False
        })
    else:
        databases = db.execute('''
            SELECT d.*, p.can_view, p.can_edit, p.can_add
            FROM databases d
            JOIN permissions p ON p.database_id = d.id
            WHERE p.user_id = ? AND p.can_view = 1
        ''', (user_id,)).fetchall()
    return jsonify([dict(row) for row in databases])

@app.route('/tables/<int:db_id>')
def get_tables(db_id):
    token = request.args.get('token')
    user_id = get_user_by_token(token)
    if not user_id:
        return jsonify({'error': 'Недействительный токен'}), 403

    if db_id == -1:  # виртуальная база журнала
        return jsonify(["event_log"])

    db = get_db()
    database = db.execute("SELECT * FROM databases WHERE id = ?", (db_id,)).fetchone()
    if not database:
        return jsonify({"error": "База не найдена"}), 404

    user = db.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    if user['role'] != 'admin':
        perm = db.execute("SELECT can_view FROM permissions WHERE user_id=? AND database_id=?",
                          (user_id, db_id)).fetchone()
        if not perm or not perm['can_view']:
            return jsonify({"error": "Нет прав на просмотр"}), 403

    target_conn = sqlite3.connect(database['path'])
    cursor = target_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    target_conn.close()
    return jsonify(tables)

@app.route('/table_data/<int:db_id>/<path:table_name>')
def get_table_data(db_id, table_name):
    token = request.args.get('token')
    user_id = get_user_by_token(token)
    if not user_id:
        return jsonify({'error': 'Недействительный токен'}), 403

    if db_id == -1 and table_name == "event_log":
        db = get_db()
        rows = db.execute("SELECT * FROM event_log ORDER BY timestamp DESC").fetchall()
        col_names = [desc[0] for desc in db.execute("SELECT * FROM event_log LIMIT 0").description]
        data = [dict(row) for row in rows]
        return jsonify({"columns": col_names, "rows": data})

    db = get_db()
    database = db.execute("SELECT * FROM databases WHERE id = ?", (db_id,)).fetchone()
    if not database:
        return jsonify({"error": "База не найдена"}), 404

    user = db.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    if user['role'] != 'admin':
        perm = db.execute("SELECT can_view FROM permissions WHERE user_id=? AND database_id=?",
                          (user_id, db_id)).fetchone()
        if not perm or not perm['can_view']:
            return jsonify({"error": "Нет прав на просмотр"}), 403

    target_conn = sqlite3.connect(database['path'])
    target_conn.row_factory = sqlite3.Row
    cursor = target_conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM "{table_name}"')
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        data = [dict(row) for row in rows]
        target_conn.close()
        return jsonify({"columns": col_names, "rows": data})
    except Exception as e:
        target_conn.close()
        return jsonify({"error": str(e)}), 400

@app.route('/commit/<int:db_id>', methods=['POST'])
def commit_changes(db_id):
    token = request.json.get('token')
    user_id = get_user_by_token(token)
    if not user_id:
        return jsonify({"error": "Недействительный токен"}), 403

    if db_id == -1:
        return jsonify({"error": "Журнал только для чтения"}), 403

    db = get_db()
    database = db.execute("SELECT * FROM databases WHERE id = ?", (db_id,)).fetchone()
    if not database:
        return jsonify({"error": "База не найдена"}), 404

    user = db.execute("SELECT role FROM users WHERE id = ?", (user_id,)).fetchone()
    if user['role'] != 'admin':
        perm = db.execute("SELECT can_edit, can_add FROM permissions WHERE user_id=? AND database_id=?",
                          (user_id, db_id)).fetchone()
        if not perm:
            return jsonify({"error": "Нет прав на изменение"}), 403
        can_edit = perm['can_edit']
        can_add = perm['can_add']
        if not can_edit and not can_add:
            return jsonify({"error": "Нет прав на изменение"}), 403

    target_path = database['path']
    payload = request.json
    inserts = payload.get('inserts', [])
    deletes = payload.get('deletes', [])
    updates = payload.get('updates', [])
    conn = sqlite3.connect(target_path)
    cursor = conn.cursor()
    try:
        for ins in inserts:
            table = ins['table']
            values = ins['values']
            columns = ', '.join([f'"{k}"' for k in values.keys()])
            placeholders = ', '.join(['?' for _ in values])
            cursor.execute(f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})', list(values.values()))
        for d in deletes:
            table = d['table']
            row_id = d['id']
            cursor.execute(f'DELETE FROM "{table}" WHERE rowid = ?', (row_id,))
        for upd in updates:
            table = upd['table']
            row_id = upd['id']
            vals = upd['values']
            set_clause = ', '.join([f'"{k}" = ?' for k in vals.keys()])
            params = list(vals.values()) + [row_id]
            cursor.execute(f'UPDATE "{table}" SET {set_clause} WHERE rowid = ?', params)
        conn.commit()
        conn.close()
        log_event(user_id, "commit", f"Изменения в таблицах базы {database['name']}")
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/user_logs', methods=['GET'])
def user_logs():
    token = request.args.get('token')
    user_id = get_user_by_token(token)
    if not user_id:
        return jsonify({'error': 'Недействительный токен'}), 403
    limit = request.args.get('limit', 100, type=int)
    db = get_db()
    logs = db.execute("SELECT * FROM event_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                      (user_id, limit)).fetchall()
    return jsonify([dict(row) for row in logs])

# ---------- Инициализация ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user'
    );
    CREATE TABLE IF NOT EXISTS databases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        path TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        database_id INTEGER NOT NULL,
        can_view INTEGER NOT NULL DEFAULT 0,
        can_edit INTEGER NOT NULL DEFAULT 0,
        can_add INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (database_id) REFERENCES databases(id),
        UNIQUE(user_id, database_id)
    );
    CREATE TABLE IF NOT EXISTS sessions (
        user_id INTEGER PRIMARY KEY,
        token TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        last_ping TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS event_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS backup_schedules (
        database_id INTEGER PRIMARY KEY,
        interval_seconds INTEGER NOT NULL DEFAULT 180,
        last_backup TEXT,
        FOREIGN KEY (database_id) REFERENCES databases(id)
    );
    ''')
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                       ('admin', hash_password('admin')))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    threading.Thread(target=backup_databases, daemon=True).start()
    threading.Thread(target=lambda: app.run(host='192.168.0.102', port=5000, debug=False), daemon=True).start()
    print("Сервер запущен на http://127.0.0.1:5000")
    admin_menu()