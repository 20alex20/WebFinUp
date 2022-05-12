from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, \
    DateField
from wtforms.validators import DataRequired
from flask import Flask, url_for, render_template, redirect, make_response, request
from csv_xlsx import *
from charts import charts

from main import *

import json


class Alert:
    alert = ""

    def get(self):
        s = self.alert
        self.alert = ""
        return s  # вместо s поставить "" для отключения всплывающего окна

    def read(self):
        return self.alert

    def put(self, s):
        self.alert = s


def am_i_not_login():
    flag = 'id_user' not in request.cookies or request.cookies['id_user'] == 'null'
    if get_full_name() is None:
        write_request_cookies(request.cookies)
    return flag


def generate_params(title, **kwargs):
    params = {
        "alert": alert.get(),
        "username": get_full_name(),
        "title": title
    }
    for keys, value in kwargs.items():
        params[keys] = value
    return params


app = Flask(__name__)
app.config['SECRET_KEY'] = 'WebFinUp'
alert = Alert()


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login_web():
    form = LoginForm()
    if form.validate_on_submit():
        answer = login(form.email.data, form.password.data)
        if answer == "Неверный логин или пароль":
            alert.put(answer)
            return render_template('login.html', form=form, alert=alert.get())
        else:
            alert.put(f"Здоавствуйте, {answer[2]}!")
            if form.remember_me.data:
                max_age = 60 * 60 * 24 * 30
            else:
                max_age = None
            resp = make_response(redirect('/'))
            resp.set_cookie('id_user', str(answer[0]), max_age)
            resp.set_cookie('email', answer[1], max_age)
            resp.set_cookie('full_name', answer[2], max_age)
            return resp
    return render_template('login.html', form=form, alert=alert.get())


class Register(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


@app.route('/register', methods=['GET', 'POST'])
def register_web():
    form = Register()
    if form.validate_on_submit():
        answer = register(form.email.data, form.password.data, form.username.data)
        if answer == "Аккаунт на эту почту уже зарегистрирован":
            alert.put(answer)
            return render_template('register.html', form=form, alert=alert.get())
        else:
            alert.put("Поздравляем, Вы создали аккаунт!")
            if form.remember_me.data:
                max_age = 60 * 60 * 24 * 30
            else:
                max_age = None
            resp = make_response(redirect('/'))
            resp.set_cookie('id_user', str(answer[0]), max_age)
            resp.set_cookie('email', answer[1], max_age)
            resp.set_cookie('full_name', answer[2], max_age)
            return resp
    return render_template('register.html', form=form, )


@app.route('/logout')
def logout_():
    resp = make_response(redirect('/login'))
    if not (am_i_not_login()):
        resp.set_cookie('id_user', 'null')
        resp.set_cookie('email', 'null')
        resp.set_cookie('full_name', 'null')
        return resp
    return redirect('/login')


@app.route('/')
@app.route('/index')
def index():
    if am_i_not_login():
        return redirect('/login')

    data = []
    for i in get_all():
        d = {
            "number": i[5],
            "comment": i[4],
            "name_category": i[0],
            "name_bank_account": i[1],
            "sum": i[2],
            "date": i[3]
        }
        data.append(d)
    with open('.' + url_for('static', filename='tables/data.json'), 'w+') as file:
        json.dump(data, file, sort_keys=True, indent=4)

    summa = get_sum()
    income = get_sum_deposits()
    expense = get_sum_purchases()
    params = generate_params("Панель управления", summa=summa, income=income, expense=expense)
    return render_template('index.html', **params)


class Income(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    bank_accounts = SelectField('Счет', validators=[DataRequired()])
    comment = StringField('Комментарий')
    sum = StringField('Сумма', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i[0]), i[1]) for i in get_deposit_categories()]
        self.categories.choices = [i[1] for i in self.categories_data]
        self.bank_accounts_data = [(str(i[0]), i[1], str(i[2])) for i in get_bank_accounts()]
        self.bank_accounts.choices = [i[1] + ' (' + i[2] + '₽)' for i in self.bank_accounts_data]


@app.route('/income', methods=['GET', 'POST'])
def income():
    if am_i_not_login():
        return redirect('/login')

    form = Income()
    if form.validate_on_submit():
        for i in form.categories_data:
            if i[1] == form.categories.data:
                category = i[0]
        for i in form.bank_accounts_data:
            if i[1] == form.bank_accounts.data.split()[0]:
                bank_account = i[0]
        alert.put(
            add_deposit(category, bank_account, form.sum.data, form.date.data.strftime("%d.%m.%Y"),
                        form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/')
    params = generate_params("Добавить", name="Доход", form=form)
    return render_template('purchase.html', **params)


class Expense(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    bank_accounts = SelectField('Счет', validators=[DataRequired()])
    comment = StringField('Комментарий')
    sum = StringField('Сумма', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i[0]), i[1]) for i in get_categories()]
        self.categories.choices = [i[1] for i in self.categories_data]
        self.bank_accounts_data = [(str(i[0]), i[1], str(i[2])) for i in get_bank_accounts()]
        self.bank_accounts.choices = [i[1] + ' (' + i[2] + '₽)' for i in self.bank_accounts_data]


@app.route('/expense', methods=['GET', 'POST'])
def expense():
    if am_i_not_login():
        return redirect('/login')

    form = Expense()
    if form.validate_on_submit():
        for i in form.categories_data:
            if i[1] == form.categories.data:
                category = i[0]
        for i in form.bank_accounts_data:
            if i[1] == form.bank_accounts.data.split()[0]:
                bank_account = i[0]
        alert.put(add_purchase(category, bank_account, form.sum.data,
                               form.date.data.strftime("%d.%m.%Y"), form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/')
    params = generate_params("Добавить", name="Расход", form=form)
    return render_template('purchase.html', **params)


@app.route('/bank_accounts', methods=['GET', 'POST'])
def bank_accounts():
    if am_i_not_login():
        return redirect('/login')

    data = []
    for i in get_bank_accounts():
        d = {
            "name": i[1],
            "sum": str(i[2]),
            "description": i[3]
        }
        data.append(d)
    with open('.' + url_for('static', filename='tables/data1.json'), 'w+') as file:
        json.dump(data, file, indent=4)

    params = generate_params("Счета")
    return render_template('bank_accounts.html', **params)


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if am_i_not_login():
        return redirect('/login')

    data = []
    for i in get_categories():
        d = {
            "name": i[1],
            "of": "Расходов",
            "description": i[2]
        }
        data.append(d)
    for i in get_deposit_categories():
        d = {
            "name": i[1],
            "of": "Доходов",
            "description": i[2]
        }
        data.append(d)
    with open('.' + url_for('static', filename='tables/data2.json'), 'w+') as file:
        json.dump(data, file, indent=4)

    params = generate_params("Категории")
    return render_template('categories.html', **params)


class IncomeCategory(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i[0]), i[1]) for i in get_deposit_categories()]
        self.categories_data.insert(0, ('-1', 'Новая категория'))
        self.categories.choices = [i[1] for i in self.categories_data]


@app.route('/income_category', methods=['GET', 'POST'])
def income_category():
    if am_i_not_login():
        return redirect('/login')

    form = IncomeCategory()
    if form.validate_on_submit():
        if form.categories.data == 'Новая категория':
            alert.put(add_deposit_category(form.name.data, form.comment.data))
        else:
            for i in form.categories_data:
                if i[1] == form.categories.data:
                    category = i[0]
            alert.put(edit_deposit_category(category, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/')
    params = generate_params("Добавить", name="Доход", form=form)
    return render_template('category.html', **params)


class ExpensesCategory(FlaskForm):
    categories = SelectField('Категория', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')

    def __init__(self):
        super().__init__()
        self.categories_data = [(str(i[0]), i[1]) for i in get_categories()]
        self.categories_data.insert(0, ('-1', 'Новая категория'))
        self.categories.choices = [i[1] for i in self.categories]


@app.route('/expenses_category', methods=['GET', 'POST'])
def expenses_category():
    if am_i_not_login():
        return redirect('/login')

    form = ExpensesCategory()
    if form.validate_on_submit():
        if form.categories.data == 'Новая категория':
            alert.put(add_category(form.name.data, form.comment.data))
        else:
            for i in form.categories_data:
                if i[1] == form.categories.data:
                    category = i[0]
            alert.put(edit_category(category, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/')
    params = generate_params("Добавить", name="Расход", form=form)
    return render_template('category.html', **params)


class BankAccounts(FlaskForm):
    bank_accounts = SelectField('Счет', validators=[DataRequired()])
    name = StringField('Название', validators=[DataRequired()])
    sum = StringField('Сумма', validators=[DataRequired()], default='0')
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')

    def __init__(self):
        super().__init__()
        self.bank_accounts_data = [(str(i[0]), i[1]) for i in get_categories()]
        self.bank_accounts_data.insert(0, ('-1', 'Новый счет'))
        self.bank_accounts.choices = [i[1] for i in self.bank_accounts_data]


@app.route('/bank_account', methods=['GET', 'POST'])
def bank_account():
    if am_i_not_login():
        return redirect('/login')

    form = BankAccounts()
    if form.validate_on_submit():
        if form.bank_accounts.data == 'Новый счет':
            alert.put(add_category(form.name.data, form.comment.data))
        else:
            for i in form.bank_accounts_data:
                if i[1] == form.bank_accounts.data:
                    bank_account = i[0]
            alert.put(edit_category(bank_account, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/')
    params = generate_params("Добавить", form=form)
    return render_template('bank_account.html', **params)


class Analytics(FlaskForm):
    mode = SelectField('Режим', validators=[DataRequired()], choices=['Доходам', 'Расходам'])
    date_start = StringField('От', validators=[DataRequired()])
    date_end = StringField('До', validators=[DataRequired()])
    submit1 = SubmitField('', id='first')
    submit2 = SubmitField('', id='second')
    submit3 = SubmitField('', id='third')
    submit4 = SubmitField('', id='forth')


@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if am_i_not_login():
        return redirect('/login')

    form = Analytics()
    if form.validate_on_submit():
        if form.data['submit1']:
            mode = 'bar2'
        elif form.data['submit2']:
            mode = 'pie'
        elif form.data['submit3']:
            mode = 'bar'
        else:
            mode = "plot"
        type = False if form.mode.data == "Доходам" else True
        charts(type, mode, form.date_start.data, form.date_end.data)
        image = url_for('static', filename='images/saved_figure.png')
        params = generate_params("Аналитика", form=form, image=image)
        return render_template('analytics.html', **params)
    params = generate_params("Аналитика", form=form)
    return render_template('analytics.html', **params)


@app.route('/export_xlsx')
def export_xlsx_():
    export_xlsx()
    return redirect(url_for('static', filename='export/export_data_FinUp.xlsx'))


@app.route('/export_csv')
def export_csv_():
    export_csv()
    return redirect(url_for('static', filename='export/export_data_FinUp.zip'))


@app.errorhandler(404)
def web404(error):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
