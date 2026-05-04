import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time

SERVER_URL = "http://127.0.0.1:5000"
PING_INTERVAL = 10  # секунд

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
        "sort_asc": "Сорт. ↑",
        "sort_desc": "Сорт. ↓",
        "search_btn": "Найти",
        "search_title": "Поиск",
        "search_label": "Введите текст:",
        "search_find": "Искать",
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
        "new_row_not_saved": "Нельзя редактировать/удалять несохранённую запись. Сначала сохраните изменения на сервер.",
        "no_column_selected": "Сначала выделите столбец (щёлкните по любой ячейке столбца)"
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
        "sort_asc": "Sort ↑",
        "sort_desc": "Sort ↓",
        "search_btn": "Search",
        "search_title": "Search",
        "search_label": "Enter text:",
        "search_find": "Find",
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
        "new_row_not_saved": "Cannot edit/delete unsaved row. Save changes to server first.",
        "no_column_selected": "Click on a cell in the column you want to sort"
    }
}

# ====================== ДИАЛОГИ ======================
class EditCellDialog(tk.Toplevel):
    def __init__(self, parent, title, column, initial_value, theme, lang):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.theme = theme
        self.lang = lang
        self.configure(bg="#121212" if theme == "dark" else "#F0F0F0")
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text=f"{LANGUAGES[lang]['column']}: {column}").pack(pady=5)
        self.entry = ttk.Entry(frm, width=30)
        self.entry.pack(pady=5)
        self.entry.insert(0, initial_value)
        self.entry.focus_set()

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.on_ok, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=LANGUAGES[lang]["cancel"], command=self.on_cancel, width=8).pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_ok(self):
        self.result = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

class SearchDialog(tk.Toplevel):
    def __init__(self, parent, theme, lang):
        super().__init__(parent)
        self.title(LANGUAGES[lang]["search_title"])
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.theme = theme
        self.lang = lang
        self.configure(bg="#121212" if theme == "dark" else "#F0F0F0")
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text=LANGUAGES[lang]["search_label"]).pack(pady=5)
        self.entry = ttk.Entry(frm, width=30)
        self.entry.pack(pady=5)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.on_search())

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text=LANGUAGES[lang]["search_find"], command=self.on_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=LANGUAGES[lang]["cancel"], command=self.on_cancel).pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_search(self):
        self.result = self.entry.get()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

# ====================== ГЛАВНЫЙ КЛАСС ======================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "ru"
        self.theme = "dark"            # тёмная тема по умолчанию
        self.token = None
        self.user_id = None
        self.role = None
        self.current_db_id = None
        self.current_table = None
        self.columns = []              # имена столбцов (первый = первичный ключ)
        self.original_data = []        # исходные данные
        self.current_data = []         # рабочие данные (список словарей с ключом 'id')
        self.pending_inserts = []
        self.pending_updates = {}      # {id: {col: new_value}}
        self.pending_deletes = set()   # множество id

        self.selected_row_values = None
        self.selected_col = None
        self.filter_text = None        # текст поиска, если активен

        self.ping_thread = None
        self.stop_ping = threading.Event()

        self.title(LANGUAGES[self.lang]["title"])
        self.geometry("1280x720")

        # Экран входа
        self.login_frame = ttk.Frame(self, padding=20)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.build_login_widgets()

        # Главный интерфейс
        self.main_frame = ttk.Frame(self)
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        self.build_menus()

        self.paned = tk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashwidth=5, bg="#333")
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Левая панель
        left_frame = ttk.Frame(self.paned, width=300)
        self.paned.add(left_frame, minsize=200)
        self.tree_databases = ttk.Treeview(left_frame, show="tree", selectmode="browse")
        self.tree_databases.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.tree_databases.insert("", tk.END, iid="root", text=LANGUAGES[self.lang]["root_text"], open=True)
        self.tree_databases.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Правая панель
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, minsize=400)

        # Панель инструментов
        self.toolbar = ttk.Frame(right_frame)
        self.toolbar.pack(fill=tk.X, pady=2)
        self.btn_add = ttk.Button(self.toolbar, text="+", command=self.add_record, width=3)
        self.btn_add.pack(side=tk.LEFT, padx=2)
        self.btn_del = ttk.Button(self.toolbar, text="–", command=self.delete_record, width=3)
        self.btn_del.pack(side=tk.LEFT, padx=2)
        self.btn_edit = ttk.Button(self.toolbar, text="✎", command=self.edit_cell, width=3)
        self.btn_edit.pack(side=tk.LEFT, padx=2)
        self.btn_asc = ttk.Button(self.toolbar, text=LANGUAGES[self.lang]["sort_asc"], command=self.sort_asc)
        self.btn_asc.pack(side=tk.LEFT, padx=2)
        self.btn_desc = ttk.Button(self.toolbar, text=LANGUAGES[self.lang]["sort_desc"], command=self.sort_desc)
        self.btn_desc.pack(side=tk.LEFT, padx=2)
        self.btn_search = ttk.Button(self.toolbar, text=LANGUAGES[self.lang]["search_btn"], command=self.search_record)
        self.btn_search.pack(side=tk.LEFT, padx=2)
        self.btn_refresh = ttk.Button(self.toolbar, text=LANGUAGES[self.lang]["refresh"], command=self.refresh_table)
        self.btn_refresh.pack(side=tk.LEFT, padx=2)

        # Область таблицы
        self.table_frame = ttk.Frame(right_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Запуск с тёмной темой
        self.set_theme("dark")

    # ================= ЛОГИН И СЕССИЯ =================
    def build_login_widgets(self):
        self.logo_label = ttk.Label(self.login_frame, text=LANGUAGES[self.lang]["logo_placeholder"],
                                    font=("Arial", 18, "bold"), relief=tk.GROOVE, anchor=tk.CENTER,
                                    width=12, padding=20)
        self.logo_label.pack(pady=10)

        ttk.Label(self.login_frame, text=LANGUAGES[self.lang]["username"]).pack(pady=(10, 0))
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.pack(pady=5)

        ttk.Label(self.login_frame, text=LANGUAGES[self.lang]["password"]).pack()
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=30)
        self.password_entry.pack(pady=5)

        self.btn_login = ttk.Button(self.login_frame, text=LANGUAGES[self.lang]["login_btn"],
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
                self.start_ping_thread()
                self.show_main_window()
            else:
                messagebox.showerror(LANGUAGES[self.lang]["error"],
                                     data.get('message', LANGUAGES[self.lang]["login_fail"]))
        except Exception:
            messagebox.showerror(LANGUAGES[self.lang]["error"],
                                 "Сервер вернул некорректный ответ")

    def start_ping_thread(self):
        if self.ping_thread and self.ping_thread.is_alive():
            self.stop_ping.set()
            self.ping_thread.join()
        self.stop_ping.clear()
        self.ping_thread = threading.Thread(target=self._ping_loop, daemon=True)
        self.ping_thread.start()

    def _ping_loop(self):
        while not self.stop_ping.is_set() and self.token:
            try:
                requests.post(f"{SERVER_URL}/ping", json={"token": self.token}, timeout=2)
            except:
                pass
            time.sleep(PING_INTERVAL)

    def show_main_window(self):
        self.login_frame.place_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.set_theme(self.theme)   # перекрашиваем

    def logout(self, silent=False):
        if not silent:
            if not messagebox.askyesno(LANGUAGES[self.lang]["logout"],
                                       LANGUAGES[self.lang]["exit_confirm"]):
                return
        self.stop_ping.set()
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
        self.original_data.clear()
        self.pending_inserts.clear()
        self.pending_updates.clear()
        self.pending_deletes.clear()
        self.filter_text = None
        for child in self.tree_databases.get_children("root"):
            self.tree_databases.delete(child)
        for w in self.table_frame.winfo_children():
            w.destroy()
        self.main_frame.pack_forget()
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
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
        self.tree_databases.item("root", text=LANGUAGES[self.lang]["root_text"])
        self.btn_asc.config(text=LANGUAGES[self.lang]["sort_asc"])
        self.btn_desc.config(text=LANGUAGES[self.lang]["sort_desc"])
        self.btn_search.config(text=LANGUAGES[self.lang]["search_btn"])
        self.btn_refresh.config(text=LANGUAGES[self.lang]["refresh"])
        self.build_menus()

    def set_theme(self, theme_name):
        self.theme = theme_name
        style = ttk.Style()
        style.theme_use("clam")

        if theme_name == "light":
            bg = "#F0F0F0"
            fg = "#000000"
            entry_bg = "#FFFFFF"
            entry_fg = "#000000"
            sel_bg = "#0078D7"
            tree_bg = "#FFFFFF"
            tree_fg = "#000000"
            btn_bg = "#E0E0E0"
            btn_active = "#CCCCCC"
        else:
            bg = "#121212"
            fg = "#E0E0E0"
            entry_bg = "#1E1E1E"
            entry_fg = "#FFFFFF"
            sel_bg = "#333333"
            tree_bg = "#1E1E1E"
            tree_fg = "#E0E0E0"
            btn_bg = "#2A2A2A"
            btn_active = "#3A3A3A"

        style.configure(".", background=bg, foreground=fg, fieldbackground=entry_bg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TEntry", fieldbackground=entry_bg, foreground=entry_fg)
        style.configure("TButton", background=btn_bg, foreground=fg, borderwidth=1, relief=tk.FLAT)
        style.map("TButton", background=[("active", btn_active), ("pressed", btn_active)])
        style.configure("Treeview", background=tree_bg, foreground=tree_fg, fieldbackground=tree_bg)
        style.map("Treeview", background=[("selected", sel_bg)], foreground=[("selected", "white")])
        style.configure("Vertical.TScrollbar", background=bg, troughcolor=entry_bg)
        style.configure("Horizontal.TScrollbar", background=bg, troughcolor=entry_bg)

        # Применяем к главному окну
        self.configure(bg=bg)
        if hasattr(self, 'login_frame') and self.login_frame.winfo_ismapped():
            self.login_frame.configure(style='TFrame')
        if hasattr(self, 'main_frame') and self.main_frame.winfo_ismapped():
            self.main_frame.configure(style='TFrame')

        # Перекрашиваем специальные элементы
        style.configure("Highlight.Treeview", background=bg, foreground=fg, fieldbackground=entry_bg)
        if hasattr(self, 'tree'):
            self.tree.tag_configure('match', background='#5A5A00' if theme_name == 'dark' else '#FFFF00')

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
            self.stylize_toplevel(dialog)

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
            self.stylize_toplevel(dialog)
        except requests.exceptions.ConnectionError:
            messagebox.showerror(LANGUAGES[self.lang]["error"], LANGUAGES[self.lang]["connection_error"])

    def stylize_toplevel(self, win):
        """Применяет тему к Toplevel окну (рекурсивно)."""
        bg = "#121212" if self.theme == "dark" else "#F0F0F0"
        win.configure(bg=bg)
        for child in win.winfo_children():
            self._apply_style(child)

    def _apply_style(self, widget):
        if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Entry, ttk.Button, ttk.Treeview)):
            return  # они уже стилизованы через ttk.Style
        if isinstance(widget, tk.Frame):
            widget.configure(bg="#121212" if self.theme == "dark" else "#F0F0F0")
        elif isinstance(widget, tk.Label):
            widget.configure(bg="#121212" if self.theme == "dark" else "#F0F0F0",
                             fg="white" if self.theme == "dark" else "black")
        elif isinstance(widget, tk.Button):
            widget.configure(bg="#2A2A2A" if self.theme == "dark" else "#E0E0E0",
                             fg="white" if self.theme == "dark" else "black")
        elif isinstance(widget, tk.Entry):
            widget.configure(bg="#1E1E1E" if self.theme == "dark" else "white",
                             fg="white" if self.theme == "dark" else "black")
        for child in widget.winfo_children():
            self._apply_style(child)

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
        self.filter_text = None
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

            self.columns = data["columns"]
            self.original_data = data["rows"]
            for row in self.original_data:
                row['id'] = row[self.columns[0]]
            self.current_data = [dict(row) for row in self.original_data]
            self.build_table_view()
        except Exception as e:
            messagebox.showerror(LANGUAGES[self.lang]["error"], f"{LANGUAGES[self.lang]['table_error']}: {e}")

    def build_table_view(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        style = ttk.Style()
        if self.theme == "dark":
            style.configure("Custom.Treeview", background="#1E1E1E", foreground="#E0E0E0", fieldbackground="#1E1E1E")
        else:
            style.configure("Custom.Treeview", background="white", foreground="black", fieldbackground="white")

        self.tree = ttk.Treeview(self.table_frame, columns=self.columns, show="headings",
                                 selectmode="browse", style="Custom.Treeview")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)

        # Определяем тег для подсветки результата поиска
        highlight_bg = '#5A5A00' if self.theme == 'dark' else '#FFFF00'
        self.tree.tag_configure('match', background=highlight_bg, foreground='black')

        # Данные для отображения: с фильтром или полные
        source = self.current_data
        if self.filter_text is not None and self.filter_text != '':
            text_lower = self.filter_text.lower()
            source = [row for row in self.current_data if any(text_lower in str(row.get(col, '')).lower() for col in self.columns)]

        for row in source:
            values = [row.get(col, "") for col in self.columns]
            # Проверяем, нужно ли подсветить строку
            if self.filter_text is not None and self.filter_text != '':
                text_lower = self.filter_text.lower()
                if any(text_lower in str(values[i]).lower() for i in range(len(self.columns))):
                    self.tree.insert("", tk.END, values=values, tags=('match',))
                else:
                    self.tree.insert("", tk.END, values=values)
            else:
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
                self.selected_row_values = self.tree.item(item)['values']
            else:
                self.selected_col = None
                self.selected_row_values = None
        else:
            self.selected_col = None
            self.selected_row_values = None

    def on_double_click(self, event):
        self.on_cell_click(event)
        if self.selected_row_values and self.selected_col:
            self.edit_cell()
        else:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["select_cell"])

    def refresh_table(self):
        if self.current_db_id and self.current_table:
            self.filter_text = None     # сбрасываем фильтр
            self.display_table(self.current_db_id, self.current_table)

    def center_columns(self):
        if hasattr(self, 'tree') and self.columns:
            for col in self.columns:
                self.tree.column(col, width=120)

    # ================= СОРТИРОВКА =================
    def sort_asc(self):
        self._sort(reverse=False)

    def sort_desc(self):
        self._sort(reverse=True)

    def _sort(self, reverse):
        if not self.current_table or not self.current_data:
            return
        col = self.selected_col if self.selected_col else self.columns[0]
        if not col:
            return
        try:
            # Пытаемся сортировать как числа, если не получается — как строки
            if all(self._is_number(row.get(col)) for row in self.current_data):
                self.current_data.sort(key=lambda r: float(r.get(col) or 0), reverse=reverse)
            else:
                self.current_data.sort(key=lambda r: str(r.get(col) or '').lower(), reverse=reverse)
            self.build_table_view()
        except Exception:
            messagebox.showerror(LANGUAGES[self.lang]["error"], "Не удалось отсортировать")

    def _is_number(self, s):
        if s is None:
            return False
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    # ================= ПОИСК =================
    def search_record(self):
        if not self.current_table or not self.current_data:
            return
        dlg = SearchDialog(self, self.theme, self.lang)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        self.filter_text = dlg.result.strip()
        self.build_table_view()

    # ================= CRUD =================
    def add_record(self):
        if not self.current_table:
            return
        dialog = tk.Toplevel(self)
        dialog.title(LANGUAGES[self.lang]["new_record_title"])
        dialog.grab_set()
        self.stylize_toplevel(dialog)

        frm = ttk.Frame(dialog, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)
        entries = {}
        row = 0
        id_col = self.columns[0]
        for col in self.columns:
            if col == id_col:
                continue
            ttk.Label(frm, text=col).grid(row=row, column=0, padx=5, pady=2, sticky="e")
            entry = ttk.Entry(frm, width=30)
            entry.grid(row=row, column=1, padx=5, pady=2)
            entries[col] = entry
            row += 1

        def on_save():
            new_row = {col: entry.get() for col, entry in entries.items()}
            temp_id = -len(self.pending_inserts) - 1
            new_row['id'] = temp_id
            new_row[id_col] = temp_id
            self.current_data.append(new_row)
            self.pending_inserts.append({k: v for k, v in new_row.items() if k != 'id'})
            self.build_table_view()
            dialog.destroy()

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=row, columnspan=2, pady=10)
        ttk.Button(btn_frame, text=LANGUAGES[self.lang]["add_btn"], command=on_save, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=LANGUAGES[self.lang]["cancel"], command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)

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
        id_val = values[0]
        if isinstance(id_val, int) and id_val < 0:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["new_row_not_saved"])
            return
        if not messagebox.askyesno(LANGUAGES[self.lang]["confirm_delete"], LANGUAGES[self.lang]["confirm_delete"]):
            return

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
        if not self.selected_row_values or not self.selected_col:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["select_cell"])
            return
        if self.selected_col == self.columns[0]:
            messagebox.showinfo(LANGUAGES[self.lang]["info"], "Нельзя редактировать идентификатор")
            return

        id_val = self.selected_row_values[0]
        if isinstance(id_val, int) and id_val < 0:
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["new_row_not_saved"])
            return

        old_value = self.selected_row_values[self.columns.index(self.selected_col)]
        dlg = EditCellDialog(self, LANGUAGES[self.lang]["edit_title"], self.selected_col,
                             old_value, self.theme, self.lang)
        self.wait_window(dlg)
        new_value = dlg.result
        if new_value is not None and new_value != old_value:
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
            messagebox.showwarning(LANGUAGES[self.lang]["warning"], LANGUAGES[self.lang]["no_open_db"])
            return

        inserts_payload = []
        for row in self.pending_inserts:
            inserts_payload.append({"table": self.current_table, "values": row})

        deletes_payload = [{"table": self.current_table, "id": id_val} for id_val in self.pending_deletes]
        updates_payload = []
        for id_val, changes in self.pending_updates.items():
            updates_payload.append({"table": self.current_table, "id": id_val, "values": changes})

        payload = {
            "token": self.token,
            "inserts": inserts_payload,
            "deletes": deletes_payload,
            "updates": updates_payload
        }

        try:
            resp = requests.post(f"{SERVER_URL}/commit/{self.current_db_id}", json=payload)
            if resp.status_code == 200:
                messagebox.showinfo(LANGUAGES[self.lang]["info"], LANGUAGES[self.lang]["save_success"])
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
            messagebox.showerror(LANGUAGES[self.lang]["error"], LANGUAGES[self.lang]["connection_error"])

    def show_history(self):
        messagebox.showinfo(LANGUAGES[self.lang]["history"], LANGUAGES[self.lang]["history_stub"])

    def on_closing(self):
        self.stop_ping.set()
        if self.token:
            try:
                requests.post(f"{SERVER_URL}/logout", json={"token": self.token})
            except:
                pass
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()