# coding=utf-8
import random
from Saper.gui import GUI
from Saper.ceil import Ceil
from Saper.row import Row
from Saper.constants import *
from Saper.db import log_game


class Saper(object):
    # Число проставленных мин пользователя
    count_selected_mine = 0

    def __init__(self, count_rows=COUNT_ROWS, count_columns=COUNT_COLUMNS, mine_count=MINE_COUNT):
        # Параметры игры
        self.count_rows = count_rows
        self.count_columns = count_columns
        self.mine_count = mine_count
        self.count_ceil = self.count_columns * self.count_rows

        # Номера ячеек которые содержат мины
        self.list_numbers_field_for_mine = []

        # Список объектов строк
        self.list_rows = []

        # Объект ячеек с расставленными пользователем минами
        self.list_ceil_on_selected_mine = []

        self.gui = GUI(self.count_rows, self.count_columns, self.mine_count)
        self.gui.game = self  # Связываем GUI с этим экземпляром Saper

        self.gui.show_all_count_mine()

        # рассчет мин
        self.create_mine()

        self.gui.reset_callback = self.reset_game

    def reset_game(self):
        """
        Resets the game state.
        """
        # Stop the timer
        self.gui.timer_stop()

        # Reset timer and counters
        self.gui._time_begin = 1
        self.gui.tk_label_timer['text'] = "0000"
        self.count_selected_mine = 0
        self.gui.show_selected_count_mine(self.count_selected_mine)
        self.gui.show_all_count_mine()

        # Clear the existing rows and grid
        for row in self.list_rows:
            for ceil in row.get_list_ceil():
                ceil.tk_button.destroy()
                ceil.tk_label.destroy()
        self.list_rows.clear()
        self.list_numbers_field_for_mine.clear()
        self.list_ceil_on_selected_mine.clear()

        # Reinitialize the game field
        self.create_mine()
        self.grid()

    def update_parameters(self, new_count_rows, new_count_columns, new_mine_count):
        """
        Обновляет параметры игры и перезапускает игру.
        """
        self.count_rows = new_count_rows
        self.count_columns = new_count_columns
        self.mine_count = new_mine_count
        self.count_ceil = self.count_columns * self.count_rows

        # Обновляем параметры GUI
        self.gui.update_window_size(self.count_rows, self.count_columns, self.mine_count)

        # Перезапускаем игру
        self.reset_game()

    def create_mine(self):
        """
        Создание поля случайных мин
        """

        # формируем случайные мины на поле
        self.create_random_mine()

        for number_row in range(0, self.count_rows):
            self.list_rows.insert(number_row, Row(number_row))

            # пробегаем по строкам и создаём объекты ячеек
            for number_ceil in range(0, self.count_columns):
                ceil = Ceil(number_ceil, self.gui.tk_frame_main)
                ceil.number_in_all = (number_row * self.count_columns) + number_ceil + 1
                ceil.bind(EVENT_LEFT_CLICK, self.left_click)
                ceil.bind(EVENT_RIGHT_CLICK, self.right_click)

                self.list_rows[number_row].add_ceil(ceil)

                if ceil.number_in_all in self.list_numbers_field_for_mine:
                    ceil.is_mine = True

    def create_random_mine(self):
        """
        Формируем случайные мины на поле
        """

        for i in range(0, self.mine_count):
            self.list_numbers_field_for_mine.append(self.random_number_ceil_on_mine())

    def random_number_ceil_on_mine(self):
        """
        Генеририрует случайный номер ячейки где будет располагаться мина
        С проверкой его не вхождения в общую базу сгенерированных номеров
        :rtype: int
        """

        random_number_ceil = random.randint(1, self.count_ceil)

        if random_number_ceil in self.list_numbers_field_for_mine:
            return self.random_number_ceil_on_mine()
        else:
            return random_number_ceil

    def left_click(self, ceil, event=None):
        """
        Обработка действий при нажатии левой клавиши, открытие полей
        :type ceil: Ceil
        :type event: None or Tkinter.Event
        """

        count_mine = 0

        self.gui.timer_start()

        # если на ячейки стоит что мина
        if ceil.is_user_select_mine:
            return False

        # если ячейка является миной
        if ceil.is_mine:
            self.gui.game_over()
            return False

        list_around_ceil = self.find_around_ceil(ceil)

        for tmpCeil in list_around_ceil:
            if tmpCeil.is_mine:
                count_mine += 1

        ceil.count_mine_around = count_mine
        ceil.is_open = True

        # если ноль мин в ячейки
        if count_mine == 0:
            self.open_ceil_empty(ceil)
            for tmpCeil in list_around_ceil:
                if not tmpCeil.is_mine and not tmpCeil.is_user_select_mine and not tmpCeil.is_open:
                    self.left_click(tmpCeil)
        else:
            self.open_ceil(ceil)

    def right_click(self, ceil, event=None):
        """
        Обработка действий при нажатии правой клавиши, расстановка мин
        :type ceil: Ceil
        :type event: None or Tkinter.Event
        """

        if ceil.is_user_select_mine:
            self.add_selected_mine(ceil)
            self.check_selected_mine(True)
        else:
            self.delete_selected_mine(ceil)
            self.check_selected_mine(False)

    def find_around_ceil(self, ceil):
        """
        Находим ячейки рядом с текущей
        :type ceil: Ceil
        :rtype: list
        """

        list_ceil = []

        # смотрим левую ячейку
        try:
            if ceil.number_in_row > 0:
                tmp_ceil = ceil.row.get_ceil(ceil.number_in_row - 1)
                if tmp_ceil:
                    list_ceil.append(tmp_ceil)
        except:
            pass

        # смотрим правую ячейку
        try:
            tmp_ceil = ceil.row.get_ceil(ceil.number_in_row + 1)
            if tmp_ceil:
                list_ceil.append(tmp_ceil)
        except:
            pass

        # смотрим верхний ряд
        try:
            if ceil.row.number_row > 0:
                tmp_row = self.list_rows[ceil.row.number_row - 1]
                if tmp_row:
                    # смотрим левую верхнюю ячейку
                    try:
                        if ceil.number_in_row > 0:
                            tmp_ceil = tmp_row.get_ceil(ceil.number_in_row - 1)
                            if tmp_ceil:
                                list_ceil.append(tmp_ceil)
                    except:
                        pass

                    # смотрим среднюю верхнюю ячейку
                    try:
                        tmp_ceil = tmp_row.get_ceil(ceil.number_in_row)
                        if tmp_ceil:
                            list_ceil.append(tmp_ceil)
                    except:
                        pass

                    # смотрим правую верхнюю ячейку
                    try:
                        tmp_ceil = tmp_row.get_ceil(ceil.number_in_row + 1)
                        if tmp_ceil:
                            list_ceil.append(tmp_ceil)
                    except:
                        pass
        except:
            pass

        # смотрим нижний ряд
        try:
            tmp_row = self.list_rows[ceil.row.number_row + 1]
            if tmp_row:
                # смотрим левую нижнюю ячейку
                try:
                    if ceil.number_in_row > 0:
                        tmp_ceil = tmp_row.get_ceil(ceil.number_in_row - 1)
                        if tmp_ceil:
                            list_ceil.append(tmp_ceil)
                except:
                    pass

                # смотрим среднюю нижнюю ячейку
                try:
                    tmp_ceil = tmp_row.get_ceil(ceil.number_in_row)
                    if tmp_ceil:
                        list_ceil.append(tmp_ceil)
                except:
                    pass

                # смотрим правую нижнюю ячейку
                try:
                    tmp_ceil = tmp_row.get_ceil(ceil.number_in_row + 1)
                    if tmp_ceil:
                        list_ceil.append(tmp_ceil)
                except:
                    pass
        except:
            pass

        return list_ceil

    def open_ceil_empty(self, ceil):
        """
        Закрашиваем пустую ячейку
        :type ceil: Ceil
        """
        ceil.tk_button.destroy()
        ceil.tk_label['text'] = ""
        ceil.tk_label.grid()

    def open_ceil(self, ceil):
        """
        Закрашиваем ячейку с цифрой
        :type ceil: Ceil
        """

        ceil.tk_button.destroy()
        color_char = COLOR_CHAR.get(ceil.count_mine_around, DEFAULT_COLOR_CHAR)

        ceil.tk_label['text'] = ceil.count_mine_around
        ceil.tk_label['font'] = STYLE_FONT_CEIL
        ceil.tk_label['fg'] = color_char
        ceil.tk_label.grid()

    def add_selected_mine(self, ceil):
        """
        Добавляем ячейку в выбранные пользователем
        :type ceil: Ceil
        """
        self.list_ceil_on_selected_mine.append(ceil)

    def delete_selected_mine(self, ceil):
        """
        Удаляем ячейку из выбранных пользователем
        :type ceil: Ceil
        """
        try:
            self.list_ceil_on_selected_mine.remove(ceil)
        except:
            pass

    def check_selected_mine(self, is_mine):
        """
        учитывает число проставленных мин, для победы
        :type is_mine: bool
        """
        count_rules_mine = 0

        if is_mine:
            self.count_selected_mine += 1
            self.gui.show_selected_count_mine(self.count_selected_mine)
        elif not is_mine:
            self.count_selected_mine -= 1
            self.gui.show_selected_count_mine(self.count_selected_mine)

        # проверям кол-во проставленных и всего и проверяем на правильность
        if self.count_selected_mine == self.mine_count:
            for ceil in self.list_ceil_on_selected_mine:
                if ceil.is_mine and ceil.is_user_select_mine:
                    count_rules_mine += 1

            if count_rules_mine == self.mine_count:
                self.gui.game_winner()

    def grid(self):
        """
        Структурируем данные
        """
        self.gui.grid()

        for x, row in enumerate(self.list_rows):
            for y, ceil in enumerate(row.get_list_ceil()):
                ceil.grid()

    def show(self):
        """
        Показываем окно
        """
        self.grid()
        self.gui.show()

    def game_over(self):
        self.gui.game_over()
        self.save_game_result('loss')

    def game_winner(self):
        self.gui.game_winner()
        self.save_game_result('win')

    def save_game_result(self, result):
        if self.gui.current_user:
            game_time = self.gui._time_begin - 1
            found_mines = self.count_selected_mine
            total_mines = self.mine_count
            log_game(self.gui.current_user, game_time, result, found_mines, total_mines)