import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests

SERVER_URL = "http://127.0.0.1:5000"

# ====================== ЛОКАЛИЗАЦИЯ ======================
LANGUAGES = {
    "ru": {
        "title": "Управление базами данных КИИ",
        "login_title": "Вход в систему",
        "username": "Логин:",
        "password": "Пароль:",
        "login_btn": "Войти",
        "file": "Файл",
        "connect_db": "Подключиться к БД",
        "save": "Сохранение",
        "save_server": "Сохранить на сервере",
        "profile": "Профиль",
        "logout": "Выйти",
        "change_account": "Сменить аккаунт",
        "history": "История",
        "show_history": "Просмотр истории",
        "theme": "Тема",
        "light": "Светлая",
        "dark": "Тёмная",
        "language": "Язык",
        "russian": "Русский",
        "english": "Английский",
        "table_menu": "Таблица",
        "center_columns": "Отцентровать столбцы",
        "error": "Ошибка",
        "warning": "Предупреждение",
        "info": "Информация",
        "login_fail": "Неверный логин или пароль",
        "fill_fields": "Введите логин и пароль",
        "connection_error": "Не удалось подключиться к серверу",
        "session_active": "Уже есть активная сессия этого пользователя",
        "exit_confirm": "Вы уверены, что хотите выйти?",
        "change_confirm": "Вы уверены, что хотите сменить аккаунт?",
        "no_open_db": "Нет открытой базы данных",
        "save_success": "Изменения сохранены на сервере",
        "no_dbs_available": "Нет доступных баз данных.",
        "connect_dialog_title": "Выберите базу данных",
        "connect": "Подключиться",
        "cancel": "Отмена",
        "history_stub": "Здесь будет отображаться история действий",
        "root_text": "Базы данных",
        "logo_placeholder": "ЛОГОТИП",
        "save_error": "Не удалось сохранить базу данных",
        "table_error": "Не удалось отобразить таблицу",
        "add_record": "Добавить запись",
        "delete_record": "Удалить запись",
        "edit_cell": "Редактировать ячейку",
        "confirm_delete": "Удалить выбранную запись?",
        "column": "Столбец",
        "value": "Значение",
        "new_record_title": "Новая запись",
        "add_btn": "Добавить",
        "edit_title": "Редактирование ячейки",
        "refresh": "Обновить",
        "select_cell": "Сначала щёлкните по нужной ячейке в таблице",
        "new_row_not_saved": "Нельзя редактировать/удалять несохранённую запись. Сначала сохраните изменения на сервер."
    },
    "en": {
        "title": "CII Database Manager",
        "login_title": "Login",
        "username": "Username:",
        "password": "Password:",
        "login_btn": "Log in",
        "file": "File",
        "connect_db": "Connect to DB",
        "save": "Save",
        "save_server": "Save to server",
        "profile": "Profile",
        "logout": "Log out",
        "change_account": "Switch account",
        "history": "History",
        "show_history": "View history",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "language": "Language",
        "russian": "Russian",
        "english": "English",
        "table_menu": "Table",
        "center_columns": "Center columns",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "login_fail": "Invalid username or password",
        "fill_fields": "Enter username and password",
        "connection_error": "Cannot connect to server",
        "session_active": "Active session already exists for this user",
        "exit_confirm": "Are you sure you want to exit?",
        "change_confirm": "Switch account?",
        "no_open_db": "No database open",
        "save_success": "Changes saved to server",
        "no_dbs_available": "No databases available.",
        "connect_dialog_title": "Select database",
        "connect": "Connect",
        "cancel": "Cancel",
        "history_stub": "History will be shown here",
        "root_text": "Databases",
        "logo_placeholder": "LOGO",
        "save_error": "Failed to save database",
        "table_error": "Failed to display table",
        "add_record": "Add record",
        "delete_record": "Delete record",
        "edit_cell": "Edit cell",
        "confirm_delete": "Delete selected record?",
        "column": "Column",
        "value": "Value",
        "new_record_title": "New record",
        "add_btn": "Add",
        "edit_title": "Edit cell",
        "refresh": "Refresh",
        "select_cell": "Click on a cell in the table first",
        "new_row_not_saved": "Cannot edit/delete unsaved row. Save changes to server first."
    }
}

# ====================== ГЛАВНЫЙ КЛАСС ======================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "ru"
        self.theme = "light"
        self.token = None
        self.user_id = None
        self.role = None
        self.current_db_id = None
        self.current_table = None
        self.columns = []          # имена столбцов (первый = первичный ключ)
        self.original_data = []    # список словарей
        self.current_data = []     # рабочий список словарей с ключом 'id' (значение первого столбца)
        self.pending_inserts = []  # список новых строк (словари без id)
        self.pending_updates = {}  # {id: {col: new_value}}
        self.pending_deletes = set() # множество id

        # Для выбора ячейки
        self.selected_row_values = None  # значения строки
        self.selected_col = None

        self.title(LANGUAGES[self.lang]["title"])
        self.geometry("1280x720")

        # Экран входа
        self.login_frame = tk.Frame(self)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=360)
        self.build_login_widgets()

        # Главный интерфейс
        self.main_frame = tk.Frame(self)
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        self.build_menus()

        self.paned = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashwidth=5, bg="#c0c0c0")
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Левая панель
        left_frame = tk.Frame(self.paned, width=300)
        self.paned.add(left_frame, minsize=200)
        self.tree_databases = ttk.Treeview(left_frame, show="tree", selectmode="browse")
        self.tree_databases.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.tree_databases.insert("", tk.END, iid="root", text=LANGUAGES[self.lang]["root_text"], open=True)
        self.tree_databases.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Правая панель
        right_frame = tk.Frame(self.paned)
        self.paned.add(right_frame, minsize=400)

        # Панель инструментов
        self.toolbar = tk.Frame(right_frame, bd=1, relief=tk.RAISED)
        self.toolbar.pack(fill=tk.X, pady=2)
        self.btn_add = tk.Button(self.toolbar, text="+", command=self.add_record, width=3)
        self.btn_add.pack(side=tk.LEFT, padx=2)
        self.btn_del = tk.Button(self.toolbar, text="–", command=self.delete_record, width=3)
        self.btn_del.pack(side=tk.LEFT, padx=2)
        self.btn_edit = tk.Button(self.toolbar, text="✎", command=self.edit_cell, width=3)
        self.btn_edit.pack(side=tk.LEFT, padx=2)
        self.btn_refresh = tk.Button(self.toolbar, text=LANGUAGES[self.lang]["refresh"], command=self.refresh_table)
        self.btn_refresh.pack(side=tk.LEFT, padx=2)

        # Область таблицы
        self.table_frame = tk.Frame(right_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ================= ЛОГИН И СЕССИЯ =================
    def build_login_widgets(self):
        self.logo_label = tk.Label(self.login_frame, text=LANGUAGES[self.lang]["logo_placeholder"],
                                   font=("Arial", 18, "bold"), relief=tk.GROOVE,
                                   width=10, height=5)
        self.logo_label.pack(pady=20)
        self.lbl_username = tk.Label(self.login_frame, text=LANGUAGES[self.lang]["username"])
        self.lbl_username.pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.login_frame, width=30)
        self.username_entry.pack(pady=5)
        self.lbl_password = tk.Label(self.login_frame, text=LANGUAGES[self.lang]["password"])
        self.lbl_password.pack()
        self.password_entry = tk.Entry(self.login_frame, show="*", width=30)
        self.password_entry.pack(pady=5)
        self.btn_login = tk.Button(self.login_frame, text=LANGUAGES[self.lang]["login_btn"],
                                   command=self.login, width=15)
        self.btn_login.pack(pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"],
                                   LANGUAGES[self.lang]["fill_fields"])
            return
        try:
            resp = requests.post(f"{SERVER_URL}/login", json={
                "username": username,
                "password": password
            })
        except requests.exceptions.ConnectionError:
            messagebox.showerror(LANGUAGES[self.lang]["error"],
                                 LANGUAGES[self.lang]["connection_error"])
            return

        if resp.status_code != 200:
            if resp.status_code == 409:
                messagebox.showerror(LANGUAGES[self.lang]["error"],
                                     LANGUAGES[self.lang]["session_active"])
            else:
                messagebox.showerror(LANGUAGES[self.lang]["error"],
                                     LANGUAGES[self.lang]["login_fail"])
            return

        try:
            data = resp.json()
            if data.get("success"):
                self.user_id = data['user_id']
                self.role = data['role']
                self.token = data['token']
                self.show_main_window()
            else:
                messagebox.showerror(LANGUAGES[self.lang]["error"],
                                     data.get('message', LANGUAGES[self.lang]["login_fail"]))
        except Exception:
            messagebox.showerror(LANGUAGES[self.lang]["error"],
                                 "Сервер вернул некорректный ответ")

    def show_main_window(self):
        self.login_frame.place_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.set_theme(self.theme)

    def logout(self, silent=False):
        if not silent:
            if not messagebox.askyesno(LANGUAGES[self.lang]["logout"],
                                       LANGUAGES[self.lang]["exit_confirm"]):
                return
        if self.token:
            try:
                requests.post(f"{SERVER_URL}/logout", json={"token": self.token})
            except:
                pass
        self.token = None
        self.user_id = None
        self.role = None
        self.current_db_id = None
        self.current_table = None
        self.columns.clear()
        self.current_data.clear()
        self.pending_inserts.clear()
        self.pending_updates.clear()
        self.pending_deletes.clear()
        for child in self.tree_databases.get_children("root"):
            self.tree_databases.delete(child)
        for w in self.table_frame.winfo_children():
            w.destroy()
        self.main_frame.pack_forget()
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=360)
        self.set_theme(self.theme)

    def change_account(self):
        if messagebox.askyesno(LANGUAGES[self.lang]["change_account"],
                               LANGUAGES[self.lang]["change_confirm"]):
            self.logout(silent=True)

    # ================= МЕНЮ И ТЕМЫ =================
    def build_menus(self):
        self.menubar.delete(0, tk.END)
        lang = self.lang

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label=LANGUAGES[lang]["connect_db"], command=self.connect_to_database)
        self.menubar.add_cascade(label=LANGUAGES[lang]["file"], menu=file_menu)

        save_menu = tk.Menu(self.menubar, tearoff=0)
        save_menu.add_command(label=LANGUAGES[lang]["save_server"], command=self.save_to_server)
        self.menubar.add_cascade(label=LANGUAGES[lang]["save"], menu=save_menu)

        # Меню "Таблица"
        table_menu = tk.Menu(self.menubar, tearoff=0)
        table_menu.add_command(label=LANGUAGES[lang]["center_columns"], command=self.center_columns)
        self.menubar.add_cascade(label=LANGUAGES[lang]["table_menu"], menu=table_menu)

        profile_menu = tk.Menu(self.menubar, tearoff=0)
        profile_menu.add_command(label=LANGUAGES[lang]["logout"], command=self.logout)
        profile_menu.add_command(label=LANGUAGES[lang]["change_account"], command=self.change_account)
        self.menubar.add_cascade(label=LANGUAGES[lang]["profile"], menu=profile_menu)

        history_menu = tk.Menu(self.menubar, tearoff=0)
        history_menu.add_command(label=LANGUAGES[lang]["show_history"], command=self.show_history)
        self.menubar.add_cascade(label=LANGUAGES[lang]["history"], menu=history_menu)

        theme_menu = tk.Menu(self.menubar, tearoff=0)
        theme_menu.add_command(label=LANGUAGES[lang]["light"], command=lambda: self.set_theme("light"))
        theme_menu.add_command(label=LANGUAGES[lang]["dark"], command=lambda: self.set_theme("dark"))
        self.menubar.add_cascade(label=LANGUAGES[lang]["theme"], menu=theme_menu)

        lang_menu = tk.Menu(self.menubar, tearoff=0)
        lang_menu.add_command(label=LANGUAGES[lang]["russian"], command=lambda: self.set_language("ru"))
        lang_menu.add_command(label=LANGUAGES[lang]["english"], command=lambda: self.set_language("en"))
        self.menubar.add_cascade(label=LANGUAGES[lang]["language"], menu=lang_menu)

    def set_language(self, new_lang):
        if new_lang == self.lang:
            return
        self.lang = new_lang
        self.title(LANGUAGES[self.lang]["title"])
        self.logo_label.config(text=LANGUAGES[self.lang]["logo_placeholder"])
        self.lbl_username.config(text=LANGUAGES[self.lang]["username"])
        self.lbl_password.config(text=LANGUAGES[self.lang]["password"])
        self.btn_login.config(text=LANGUAGES[self.lang]["login_btn"])
        self.tree_databases.item("root", text=LANGUAGES[self.lang]["root_text"])
        self.btn_refresh.config(text=LANGUAGES[self.lang]["refresh"])
        self.build_menus()

    def set_theme(self, theme_name):
        self.theme = theme_name
        style = ttk.Style()
        if theme_name == "light":
            bg_color = "white"
            fg_color = "black"
            entry_bg = "white"
            entry_fg = "black"
            btn_bg = "SystemButtonFace"
            btn_fg = "black"
        else:
            bg_color = "#2e2e2e"
            fg_color = "white"
            entry_bg = "#3e3e3e"
            entry_fg = "white"
            btn_bg = "#444444"
            btn_fg = "white"

        self.configure(bg=bg_color)
        style.theme_use("clam")
        style.configure(".", background=bg_color, foreground=fg_color)
        style.configure("Treeview", background=bg_color, fieldbackground=bg_color, foreground=fg_color)
        style.map("Treeview", background=[("selected", "#555555" if theme_name == "dark" else "#c0c0c0")])
        style.configure("TButton", background=btn_bg, foreground=btn_fg)

        if self.login_frame.winfo_ismapped():
            self.login_frame.configure(bg=bg_color)
            for widget in self.login_frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=bg_color, fg=fg_color)
                elif isinstance(widget, tk.Entry):
                    widget.configure(bg=entry_bg, fg=entry_fg, insertbackground=entry_fg)
                elif isinstance(widget, tk.Button):
                    widget.configure(bg=btn_bg, fg=btn_fg, activebackground=btn_bg)

    # ================= ПОДКЛЮЧЕНИЕ К БД =================
    def connect_to_database(self):
        if self.token is None:
            return
        try:
            resp = requests.get(f"{SERVER_URL}/databases?token={self.token}")
            if resp.status_code != 200:
                messagebox.showerror(LANGUAGES[self.lang]["error"],
                                     LANGUAGES[self.lang]["connection_error"])
                return
            dbs = resp.json()
            if not dbs:
                messagebox.showinfo(LANGUAGES[self.lang]["info"],
                                    LANGUAGES[self.lang]["no_dbs_available"])
                return

            dialog = tk.Toplevel(self)
            dialog.title(LANGUAGES[self.lang]["connect_dialog_title"])
            dialog.geometry("500x300")
            dialog.transient(self)
            dialog.grab_set()

            columns = ("id", "name", "permissions")
            tree = ttk.Treeview(dialog, columns=columns, show="headings")
            tree.heading("id", text="ID")
            tree.heading("name", text="Название")
            tree.heading("permissions", text="Права")
            tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            for db in dbs:
                perm = ""
                if db.get('can_view'): perm += "Просмотр "
                if db.get('can_edit'): perm += "Изменение "
                if db.get('can_add'): perm += "Добавление "
                tree.insert("", tk.END, values=(db['id'], db['name'], perm.strip()))

            def connect_selected():
                selected = tree.selection()
                if not selected:
                    messagebox.showwarning(LANGUAGES[self.lang]["warning"], "Выберите базу")
                    return
                item = tree.item(selected[0])
                db_id = item['values'][0]
                db_name = item['values'][1]
                self.current_db_id = db_id
                self.load_tables_for_db(db_id, db_name)
                dialog.destroy()

            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text=LANGUAGES[self.lang]["connect"], command=connect_selected).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text=LANGUAGES[self.lang]["cancel"], command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        except requests.exceptions.ConnectionError:
            messagebox.showerror(LANGUAGES[self.lang]["error"], LANGUAGES[self.lang]["connection_error"])

    def load_tables_for_db(self, db_id, db_name):
        self.tree_databases.delete(*self.tree_databases.get_children("root"))
        db_iid = f"server_db_{db_id}"
        self.tree_databases.insert("root", tk.END, iid=db_iid, text=db_name, open=True)

        try:
            resp = requests.get(f"{SERVER_URL}/tables/{db_id}?token={self.token}")
            if resp.status_code == 200:
                tables = resp.json()
                for t in tables:
                    self.tree_databases.insert(db_iid, tk.END, iid=f"table_{db_id}_{t}", text=t)
                self.tree_databases.item(db_iid, open=True)
            else:
                messagebox.showerror(LANGUAGES[self.lang]["error"], "Не удалось получить таблицы")
        except Exception as e:
            messagebox.showerror(LANGUAGES[self.lang]["error"], str(e))

    # ================= ОТОБРАЖЕНИЕ ТАБЛИЦЫ =================
    def on_tree_select(self, event):
        selected = self.tree_databases.selection()
        if not selected:
            return
        iid = selected[0]
        if iid.startswith("table_"):
            parts = iid.split("_", 2)
            if len(parts) < 3:
                return
            db_id = parts[1]
            table_name = parts[2]
            self.current_table = table_name
            self.display_table(db_id, table_name)

    def display_table(self, db_id, table_name):
        self.pending_inserts.clear()
        self.pending_updates.clear()
        self.pending_deletes.clear()
        self.columns = []
        self.original_data = []
        self.current_data = []
        self.selected_row_values = None
        self.selected_col = None

        try:
            resp = requests.get(f"{SERVER_URL}/table_data/{db_id}/{table_name}?token={self.token}")
            if resp.status_code != 200:
                messagebox.showerror(LANGUAGES[self.lang]["error"], LANGUAGES[self.lang]["table_error"])
                return
            data = resp.json()
            if "error" in data:
                messagebox.showerror(LANGUAGES[self.lang]["error"], data["error"])
                return

            self.columns = data["columns"]          # первый = первичный ключ
            self.original_data = data["rows"]       # список словарей
            # Преобразуем: добавляем ключ 'id' со значением первого столбца
            for row in self.original_data:
                row['id'] = row[self.columns[0]]
            self.current_data = [dict(row) for row in self.original_data]
            self.build_table_view()
        except Exception as e:
            messagebox.showerror(LANGUAGES[self.lang]["error"], f"{LANGUAGES[self.lang]['table_error']}: {e}")

    def build_table_view(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.tree = ttk.Treeview(self.table_frame, columns=self.columns, show="headings", selectmode="browse")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)

        for row in self.current_data:
            values = [row.get(col, "") for col in self.columns]
            self.tree.insert("", tk.END, values=values)

        vsb = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_cell_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if item and col:
            col_idx = int(col.replace('#', '')) - 1
            if 0 <= col_idx < len(self.columns):
                self.selected_col = self.columns[col_idx]
                # Сохраняем всю строку
                self.selected_row_values = self.tree.item(item)['values']
            else:
                self.selected_col = None
                self.selected_row_values = None
        else:
            self.selected_col = None
            self.selected_row_values = None

    def on_double_click(self, event):
        self.on_cell_click(event)
        if self.selected_row_values is not None and self.selected_col is not None:
            self.edit_cell()
        else:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["select_cell"])

    def refresh_table(self):
        if self.current_db_id and self.current_table:
            self.display_table(self.current_db_id, self.current_table)

    def center_columns(self):
        if hasattr(self, 'tree') and self.columns:
            for col in self.columns:
                self.tree.column(col, width=120)

    # ================= CRUD операции =================
    def add_record(self):
        if not self.current_table:
            return
        dialog = tk.Toplevel(self)
        dialog.title(LANGUAGES[self.lang]["new_record_title"])
        dialog.grab_set()

        entries = {}
        row = 0
        for col in self.columns:
            # Не даём редактировать первичный ключ (первый столбец)
            if col == self.columns[0]:
                continue
            tk.Label(dialog, text=col).grid(row=row, column=0, padx=5, pady=2)
            entry = tk.Entry(dialog, width=30)
            entry.grid(row=row, column=1, padx=5, pady=2)
            entries[col] = entry
            row += 1

        def on_save():
            new_row = {col: entry.get() for col, entry in entries.items()}
            # Присваиваем временный отрицательный id
            temp_id = -len(self.pending_inserts) - 1
            new_row['id'] = temp_id
            new_row[self.columns[0]] = temp_id  # для отображения в первом столбце
            self.current_data.append(new_row)
            self.pending_inserts.append({k: v for k, v in new_row.items() if k != 'id' and k != self.columns[0]})
            # В pending_inserts храним только пользовательские поля без временного id
            self.build_table_view()
            dialog.destroy()

        tk.Button(dialog, text=LANGUAGES[self.lang]["add_btn"], command=on_save).grid(row=row, columnspan=2, pady=10)

    def delete_record(self):
        if not self.current_table:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], "Выберите запись для удаления")
            return
        item = selected[0]
        values = self.tree.item(item)['values']
        if not values:
            return
        id_val = values[0]  # первый столбец
        if isinstance(id_val, int) and id_val < 0:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["new_row_not_saved"])
            return

        if not messagebox.askyesno(LANGUAGES[self.lang]["confirm_delete"],
                                   LANGUAGES[self.lang]["confirm_delete"]):
            return

        # Удаляем из current_data
        for i, row in enumerate(self.current_data):
            if row['id'] == id_val:
                del self.current_data[i]
                break
        if id_val > 0:
            self.pending_deletes.add(id_val)
        self.build_table_view()

    def edit_cell(self):
        if not self.current_table:
            return
        if self.selected_row_values is None or self.selected_col is None:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"],
                                   LANGUAGES[self.lang]["select_cell"])
            return
        # Запрет редактирования первого столбца (первичный ключ)
        if self.selected_col == self.columns[0]:
            messagebox.showinfo(LANGUAGES[self.lang]["info"], "Нельзя редактировать идентификатор")
            return

        id_val = self.selected_row_values[0]
        if isinstance(id_val, int) and id_val < 0:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["new_row_not_saved"])
            return

        old_value = self.selected_row_values[self.columns.index(self.selected_col)]
        new_value = simpledialog.askstring(LANGUAGES[self.lang]["edit_title"],
                                           f"{self.selected_col}:",
                                           initialvalue=old_value,
                                           parent=self)
        if new_value is not None and new_value != old_value:
            # Обновляем current_data
            for row in self.current_data:
                if row['id'] == id_val:
                    row[self.selected_col] = new_value
                    break
            if id_val > 0:
                if id_val not in self.pending_updates:
                    self.pending_updates[id_val] = {}
                self.pending_updates[id_val][self.selected_col] = new_value
            self.build_table_view()

    # ================= СОХРАНЕНИЕ НА СЕРВЕР =================
    def save_to_server(self):
        if not self.current_db_id or not self.current_table:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"],
                                   LANGUAGES[self.lang]["no_open_db"])
            return

        inserts_payload = []
        for row in self.pending_inserts:
            # row уже словарь без id
            inserts_payload.append({"table": self.current_table, "values": row})

        deletes_payload = [{"table": self.current_table, "id": id_val} for id_val in self.pending_deletes]

        updates_payload = []
        for id_val, changes in self.pending_updates.items():
            updates_payload.append({
                "table": self.current_table,
                "id": id_val,
                "values": changes
            })

        payload = {
            "token": self.token,
            "inserts": inserts_payload,
            "deletes": deletes_payload,
            "updates": updates_payload
        }

        try:
            resp = requests.post(f"{SERVER_URL}/commit/{self.current_db_id}", json=payload)
            if resp.status_code == 200:
                messagebox.showinfo(LANGUAGES[self.lang]["info"],
                                    LANGUAGES[self.lang]["save_success"])
                self.pending_inserts.clear()
                self.pending_updates.clear()
                self.pending_deletes.clear()
                self.refresh_table()
            else:
                error_msg = resp.text
                try:
                    error_data = resp.json()
                    error_msg = error_data.get("error", error_msg)
                except:
                    pass
                messagebox.showerror(LANGUAGES[self.lang]["error"],
                                     f"{LANGUAGES[self.lang]['save_error']}: {error_msg}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror(LANGUAGES[self.lang]["error"],
                                 LANGUAGES[self.lang]["connection_error"])

    def show_history(self):
        messagebox.showinfo(LANGUAGES[self.lang]["history"],
                            LANGUAGES[self.lang]["history_stub"])

    def on_closing(self):
        if self.token:
            self.logout(silent=True)
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()