from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, \
    DateField
from wtforms.validators import DataRequired

from app.logics.sql import *


class Login(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class Register(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


class Income(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    bank_accounts = SelectField('Счет', validators=[DataRequired()])
    comment = StringField('Комментарий')
    sum = StringField('Сумма', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i.id_deposit_category), i.name) for i in
                                get_deposit_categories()]
        self.categories.choices = [i[1] for i in self.categories_data]
        self.bank_accounts_data = [(str(i.id_bank_account), i.name, str(i.current_sum))
                                   for i in get_bank_accounts()]
        self.bank_accounts.choices = [i[1] + ' (' + i[2] + '₽)' for i in self.bank_accounts_data]


class Expense(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    bank_accounts = SelectField('Счет', validators=[DataRequired()])
    comment = StringField('Комментарий')
    sum = StringField('Сумма', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i.id_category), i.name) for i in get_categories()]
        self.categories.choices = [i[1] for i in self.categories_data]
        self.bank_accounts_data = [(str(i.id_bank_account), i.name, str(i.current_sum))
                                   for i in get_bank_accounts()]
        self.bank_accounts.choices = [i[1] + ' (' + i[2] + '₽)' for i in self.bank_accounts_data]


class IncomeCategory(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i.id_deposit_category), i.name)
                                for i in get_deposit_categories()]
        self.categories_data.insert(0, ('-1', 'Новая категория'))
        self.categories.choices = [i[1] for i in self.categories_data]


class ExpensesCategory(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i.id_category), i.name) for i in get_categories()]
        self.categories_data.insert(0, ('-1', 'Новая категория'))
        self.categories.choices = [i[1] for i in self.categories_data]


class BankAccounts(FlaskForm):
    bank_accounts = SelectField('Счет', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    sum = StringField('Сумма', validators=[DataRequired()], default='0')
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')

    def __init__(self):
        super().__init__()
        self.bank_accounts_data = [(str(i.id_bank_account), i.name) for i in get_bank_accounts()]
        self.bank_accounts_data.insert(0, ('-1', 'Новый счет'))
        self.bank_accounts.choices = [i[1] for i in self.bank_accounts_data]


class Analytics(FlaskForm):
    mode = SelectField('Режим', validators=[DataRequired()], choices=['Доходам', 'Расходам'])
    date_start = StringField('От', validators=[DataRequired()])
    date_end = StringField('До', validators=[DataRequired()])
    submit1 = SubmitField('', id='first')
    submit2 = SubmitField('', id='second')
    submit3 = SubmitField('', id='third')
    submit4 = SubmitField('', id='forth')
