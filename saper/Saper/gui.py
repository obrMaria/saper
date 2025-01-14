# gui.py
import tkinter.messagebox as tkMessageBox
import tkinter as Tkinter
import tkinter.simpledialog as simpledialog
from Saper.constants import *
from Saper.db import initialize_db, add_user, log_game, get_statistics
import tkinter.ttk as ttk


class GUI(Tkinter.Tk):
    is_grid = False

    _time_begin = 1
    _timer_id = False

    def __init__(self, count_rows=COUNT_ROWS, count_columns=COUNT_COLUMNS, mine_count=MINE_COUNT):
        # Инициализируем базу данных
        initialize_db()
        
        Tkinter.Tk.__init__(self)
        self.title(WINDOW_TITLE)
        self.count_rows = count_rows
        self.count_columns = count_columns
        self.mine_count = mine_count
        self.update_window_size(self.count_rows, self.count_columns, self.mine_count)

        # Меню
        menubar = Tkinter.Menu(self)
        self.config(menu=menubar)

        # Меню "Файл"
        file_menu = Tkinter.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Войти как игрок", command=self.player_login)
        file_menu.add_command(label="Войти как администратор", command=self.admin_login)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        menubar.add_cascade(label="меню", menu=file_menu)

        self.tk_frame_toolbar = Tkinter.Frame(self, background="grey",
                                              relief=Tkinter.GROOVE, border=2)

        self.tk_frame_main = Tkinter.Frame(self, background=WINDOW_MAIN_FRAME_COLOR_BACKGROUND,
                                           relief=Tkinter.GROOVE, border=2)

        self.tk_label_timer = Tkinter.Label(self.tk_frame_toolbar, text="0000")
        self.tk_label_timer.grid(row=0, column=0, sticky=Tkinter.NSEW)

        self.tk_label_button_new = Tkinter.Button(self.tk_frame_toolbar, text="NEW", command=self.reset_game)
        self.tk_label_button_new.grid(row=0, column=1, sticky=Tkinter.NSEW)

        self.tk_label_counter = Tkinter.Label(self.tk_frame_toolbar, text="00/00")
        self.tk_label_counter.grid(row=0, column=2, sticky=Tkinter.NSEW)

        self.current_user = None  # Добавляем атрибут для текущего пользователя

    def update_window_size(self, count_rows, count_columns, mine_count):
        """
        Обновляет размер окна и другие параметры на основе новых настроек.
        """
        self.count_rows = count_rows
        self.count_columns = count_columns
        self.mine_count = mine_count

        # Общая ширина окна
        self.window_width = SIZE_CEIL * self.count_columns + 10 + (self.count_columns * (PADDING_BETWEEN_CEIL * 2))

        # Общая высота окна
        self.window_height = SIZE_CEIL * self.count_rows + 10 + (self.count_rows * (PADDING_BETWEEN_CEIL * 2)) + WINDOW_TOOLBAR_HEIGHT

        self.geometry(f"{self.window_width}x{self.window_height}")

    def reset_game(self):
        if hasattr(self, 'reset_callback') and callable(self.reset_callback):
            self.reset_callback()

    def show_all_count_mine(self):
        self.tk_label_counter['text'] = "00/%2d" % self.mine_count

    def show_selected_count_mine(self, selected_mine):
        self.tk_label_counter['text'] = "%2d/%2d" % (selected_mine, self.mine_count)

    def timer_start(self):
        if not self._timer_id and self._time_begin == 1:
            self.timer()

    def timer_stop(self):
        if self._timer_id:
            self.tk_label_timer.after_cancel(self._timer_id)
            self._timer_id = False

    def timer(self):
        self.tk_label_timer['text'] = "%0004d" % self._time_begin
        self._time_begin += 1
        self._timer_id = self.tk_label_timer.after(1000, self.timer)

    def game_over(self):
        self.timer_stop()
        tkMessageBox.showerror(GAME_OVER_WINDOW_TITLE, GAME_OVER_MESSAGE)
        self.log_game_result('loss')
        return False

    def game_winner(self):
        self.timer_stop()
        tkMessageBox.showinfo(WINNER_WINDOW_TITLE, WINNER_MESSAGE)
        self.log_game_result('win')
        return False

    def log_game_result(self, result):
        if self.current_user:
            game_time = self._time_begin - 1
            found_mines = self.game.count_selected_mine
            total_mines = self.mine_count
            log_game(self.current_user, game_time, result, found_mines, total_mines)

    def grid(self):
        super(GUI, self).grid()
        self.tk_frame_toolbar.grid(row=0, column=0)

        self.tk_frame_toolbar.rowconfigure('all', minsize=WINDOW_TOOLBAR_HEIGHT)

        width_label_toolbar = (float(self.window_width - WINDOW_TOOLBAR_HEIGHT)) / 2.0
        self.tk_frame_toolbar.columnconfigure(0, minsize=width_label_toolbar - 5)
        self.tk_frame_toolbar.columnconfigure(1, minsize=WINDOW_TOOLBAR_HEIGHT)
        self.tk_frame_toolbar.columnconfigure(2, minsize=width_label_toolbar - 5)

        self.tk_frame_main.grid(row=1, column=0)
        self.is_grid = True

    def player_login(self):
        self.player_name_dialog()

    def player_name_dialog(self):
        dialog = Tkinter.Toplevel(self)
        dialog.title("Введите имя пользователя")

        label = Tkinter.Label(dialog, text="Имя:")
        label.pack()

        name_entry = Tkinter.Entry(dialog)
        name_entry.pack()

        def save_player_name():
            player_name = name_entry.get().strip()
            if player_name:
                self.current_user = player_name
                add_user(player_name)  # Добавляем пользователя в базу данных
                dialog.destroy()
                self.show()

        submit_button = Tkinter.Button(dialog, text="Войти", command=save_player_name)
        submit_button.pack()

    def admin_login(self):
        self.admin_password_dialog()

    def admin_password_dialog(self):
        dialog = Tkinter.Toplevel(self)
        dialog.title("Введите пароль администратора")

        label = Tkinter.Label(dialog, text="Пароль:")
        label.pack()

        password_entry = Tkinter.Entry(dialog, show='*')
        password_entry.pack()

        def validate_password():
            password = password_entry.get()
            if password == "123":  # Замените ADMIN_PASSWORD на реальный пароль
                dialog.destroy()
                self.admin_interface()
            else:
                tkMessageBox.showerror("Ошибка", "Неверный пароль")

        submit_button = Tkinter.Button(dialog, text="Войти", command=validate_password)
        submit_button.pack()

    def admin_interface(self):
        admin_win = Tkinter.Toplevel(self)
        admin_win.title("Администраторская панель")

        edit_game_params_button = Tkinter.Button(admin_win, text="Редактировать параметры игры", command=self.edit_game_params)
        edit_game_params_button.pack()

        stats_button = Tkinter.Button(admin_win, text="Просмотреть статистику", command=self.show_statistics)
        stats_button.pack()

    def edit_game_params(self):
        params_win = Tkinter.Toplevel(self)
        params_win.title("Настройки игры")

        size_label = Tkinter.Label(params_win, text="Количество строк:")
        size_label.pack()
        size_entry = Tkinter.Entry(params_win)
        size_entry.insert(0, str(self.count_rows))
        size_entry.pack()

        columns_label = Tkinter.Label(params_win, text="Количество столбцов:")
        columns_label.pack()
        columns_entry = Tkinter.Entry(params_win)
        columns_entry.insert(0, str(self.count_columns))
        columns_entry.pack()

        mines_label = Tkinter.Label(params_win, text="Количество мин:")
        mines_label.pack()
        mines_entry = Tkinter.Entry(params_win)
        mines_entry.insert(0, str(self.mine_count))
        mines_entry.pack()

        def save_game_params():
            try:
                new_rows = int(size_entry.get())
                new_columns = int(columns_entry.get())
                new_mines = int(mines_entry.get())

                if new_rows <= 0 or new_columns <= 0 or new_mines < 0 or new_mines >= new_rows * new_columns:
                    tkMessageBox.showerror("Ошибка", "Неверные параметры игры.")
                    return

                self.game.update_parameters(new_rows, new_columns, new_mines)
                params_win.destroy()
            except ValueError:
                tkMessageBox.showerror("Ошибка", "Пожалуйста, введите допустимые числовые значения.")

        save_button = Tkinter.Button(params_win, text="Сохранить", command=save_game_params)
        save_button.pack()

    def show_statistics(self):
        stats = get_statistics()
        stats_win = Tkinter.Toplevel(self)
        stats_win.title("Статистика игр")

        columns = ('username', 'total_games', 'wins', 'losses', 'average_time')
        tree = ttk.Treeview(stats_win, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col.capitalize())

        for row in stats:
            tree.insert('', Tkinter.END, values=row)

        tree.pack(fill=Tkinter.BOTH, expand=True)

    def show(self):
        if not self.is_grid:
            self.grid()
        self.mainloop()

