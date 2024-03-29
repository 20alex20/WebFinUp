import unittest

from app import app
from app.logics.sql import *


class TestCase(unittest.TestCase):
    def setUp(self):
        app.test_client()

    def test_all(self):
        with app.app_context():
            obj = register("smit5@gmail.com", "smit", "Mr. Smit")  # регистрация и вход
            assert obj[2] == "Mr. Smit"

            res = add_bank_account("Карта", 5000)  # добавление нового счёта
            assert res == "Данные изменены"

            id_ba = get_bank_accounts()[1].id_bank_account
            id_c = get_categories().first().id_category
            id_dc = get_deposit_categories().first().id_deposit_category

            res = add_deposit(id_dc, id_ba, 1300, "01.01.2023", '')  # добавление дохода
            assert res == "Данные изменены"

            res = add_purchase(id_c, id_ba, 2500, "01.01.2023", '')  # добавление траты
            assert res == "Данные изменены"

            res = get_sum()
            assert res == '3800 ₽'  # проверка того, что текущее количество денег подсчитано верно


if __name__ == '__main__':
    unittest.main()
