import sqlite3
import hashlib
import threading
import os
import uuid
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask(__name__)
DB_PATH = "server.db"
SESSION_TIMEOUT = 10  # секунд

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

# ---------- Консольное меню администратора ----------
def admin_menu():
    while True:
        print("\n=== СЕРВЕР АДМИНИСТРАТОРА ===")
        print("1. Управление пользователями")
        print("2. Управление базами данных")
        print("3. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            manage_users()
        elif choice == "2":
            manage_databases()
        elif choice == "3":
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

# ========== Flask API ========== #
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or user['password_hash'] != hash_password(password):
        return jsonify({'success': False, 'message': 'Неверный логин или пароль'}), 401

    # Проверяем существующую сессию
    existing = db.execute("SELECT * FROM sessions WHERE user_id = ?", (user['id'],)).fetchone()
    if existing:
        last_ping = existing['last_ping']
        # Если сессия устарела, удаляем её
        try:
            last_ping_time = datetime.strptime(last_ping, "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last_ping_time).total_seconds() > SESSION_TIMEOUT:
                db.execute("DELETE FROM sessions WHERE user_id = ?", (user['id'],))
                db.commit()
            else:
                return jsonify({'success': False, 'message': 'Уже есть активная сессия этого пользователя'}), 409
        except:
            # Если не можем распарсить дату, удаляем сессию для безопасности
            db.execute("DELETE FROM sessions WHERE user_id = ?", (user['id'],))
            db.commit()

    token = str(uuid.uuid4())
    db.execute("INSERT INTO sessions (user_id, token, last_ping) VALUES (?, ?, datetime('now'))",
               (user['id'], token))
    db.commit()
    return jsonify({
        'success': True,
        'user_id': user['id'],
        'role': user['role'],
        'token': token
    })

@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    token = data.get('token')
    if token:
        db = get_db()
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
    # Обновляем last_ping
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

    if user['role'] == 'admin':
        databases = db.execute("SELECT * FROM databases").fetchall()
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
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
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
    ''')
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                       ('admin', hash_password('admin')))
    conn.commit()
    conn.close()

    threading.Thread(target=lambda: app.run(host='127.0.0.1', port=5000, debug=False), daemon=True).start()
    print("Сервер запущен на http://127.0.0.1:5000")
    admin_menu()