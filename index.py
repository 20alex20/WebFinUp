from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, SelectField, DateField
from wtforms.validators import DataRequired
from flask import Flask, url_for, render_template, redirect, make_response
from csv_xlsx import *

from main import *
import json

# from input_user_data_form import UserDataForm
# @app.route('/<style>.css')
# def css(style):
#     return open(f'static/styles/{style}.css').read()


# @app.route('/<image>.png')
# def image_png(image):
#     with open(f'images/{image}.png', 'rb') as f:
#         image_binary = f.read()
#     response = make_response(image_binary)
#     response.headers.set('Content-Type', 'image/png')
#     response.headers.set('Content-Disposition', 'attachment', filename=f'{image}.png')
#     return response
#
#
# @app.route('/<image>.jpg')
# def image_jpg(image):
#     return open(f'images/{image}.jpg', 'rb').read()

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
def login_():
    form = LoginForm()
    if form.validate_on_submit():
        alert.put(login(form.email.data, form.password.data))
        if alert.read() == "Неверный логин или пароль":
            return render_template('login.html', form=form, alert=alert.get())
        else:
            return redirect('/index')
    return render_template('login.html', form=form, alert=alert.get())


class Register(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


@app.route('/register', methods=['GET', 'POST'])
def register_():
    form = Register()
    if form.validate_on_submit():
        alert.put(register(form.email.data, form.password.data, form.username.data))
        if alert.read() == "Аккаунт на эту почту уже зарегистрирован":
            return render_template('register.html', form=form, alert=alert.get())
        else:
            return redirect('/index')
    return render_template('register.html', form=form, )


@app.route('/logout')
def logout_():
    alert.put(logout())
    return redirect('/login')


@app.route('/')
@app.route('/index')
def index():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    data = []
    for i in get_get():
        d = {
            "number": i[4],
            "name_category": i[0],
            "name_bank_account": i[1],
            "sum": i[2],
            "date": i[3]
        }
        data.append(d)
    with open('static/tables/data.json', 'w+') as file:
        json.dump(data, file, sort_keys=True, indent=4)

    summa = get_sum()
    income = get_sum_deposits()
    expense = get_sum_purchases()
    params = generate_params("Панель управления", summa=summa, income=income, expense=expense)
    return render_template('index.html', **params)


@app.route('/success')
def success():
    return "Данные успешно внесены"


@app.route('/widgets')
def widgets():
    full_name = get_full_name()
    return render_template('widgets.html', username=full_name)


@app.route('/icons')
def icons():
    full_name = get_full_name()
    return render_template('icons.html', username=full_name)


@app.route('/tables')
def tables():
    full_name = get_full_name()
    return render_template('tables.html', username=full_name)


@app.route('/forms')
def forms():
    full_name = get_full_name()
    return render_template('forms.html', username=full_name)


class Income(FlaskForm):
    categories_ = [(str(i[0]), i[1]) for i in get_deposit_categories()]
    bank_accounts_ = [(str(i[0]), i[1], str(i[2])) for i in get_bank_accounts()]
    categories = SelectField('Категория', validators=[DataRequired()], choices=[i[1] for i in categories_])
    bank_accounts = SelectField('Счет', validators=[DataRequired()], choices=[i[1] + ' (' + i[2] + '₽)' for i in bank_accounts_])
    comment = StringField('Комментарий')
    sum = StringField('Сумма', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    submit = SubmitField('Добавить')


@app.route('/income', methods=['GET', 'POST'])
def income():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    form = Income()
    if form.validate_on_submit():
        for i in form.categories_:
            if i[1] == form.categories.data:
                category = i[0]
        for i in form.bank_accounts_:
            if i[1] == form.bank_accounts.data.split()[0]:
                bank_account = i[0]
        alert.put(add_deposit(category, bank_account, form.sum.data, form.date.data.strftime("%d.%m.%Y"), form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/index')
    params = generate_params("Добавить", name="Доход", form=form)
    return render_template('purchase.html', **params)


class Expense(FlaskForm):
    categories_ = [(str(i[0]), i[1]) for i in get_categories()]
    bank_accounts_ = [(str(i[0]), i[1], str(i[2])) for i in get_bank_accounts()]
    categories = SelectField('Категория', validators=[DataRequired()], choices=[i[1] for i in categories_])
    bank_accounts = SelectField('Счет', validators=[DataRequired()], choices=[i[1] + ' (' + i[2] + '₽)' for i in bank_accounts_])
    comment = StringField('Комментарий')
    sum = StringField('Сумма', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    submit = SubmitField('Добавить')


@app.route('/expense', methods=['GET', 'POST'])
def expense():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    form = Expense()
    if form.validate_on_submit():
        for i in form.categories_:
            if i[1] == form.categories.data:
                category = i[0]
        for i in form.bank_accounts_:
            if i[1] == form.bank_accounts.data.split()[0]:
                bank_account = i[0]
        alert.put(add_purchase(category, bank_account, form.sum.data,
                               form.date.data.strftime("%d.%m.%Y"), form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/index')
    params = generate_params("Добавить", name="Расход", form=form)
    return render_template('purchase.html', **params)


@app.route('/bank_accounts', methods=['GET', 'POST'])
def bank_accounts():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    data = []
    for i in get_bank_accounts():
        d = {
            "name": i[1],
            "sum": str(i[2])
        }
        data.append(d)
    with open('static/tables/data1.json', 'w+') as file:
        json.dump(data, file, indent=4)

    params = generate_params("Счета")
    return render_template('bank_accounts.html', **params)


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    data = []
    for i in get_categories():
        d = {
            "name": i[1],
            "of": "Расходов"
        }
        data.append(d)
    for i in get_deposit_categories():
        d = {
            "name": i[1],
            "of": "Доходов"
        }
        data.append(d)
    with open('static/tables/data2.json', 'w+') as file:
        json.dump(data, file, indent=4)

    params = generate_params("Категории")
    return render_template('categories.html', **params)


class IncomeCategory(FlaskForm):
    categories_ = [(str(i[0]), i[1]) for i in get_deposit_categories()]
    categories_.insert(0, ('-1', 'Новая категория'))
    categories = SelectField('Категория', validators=[DataRequired()], choices=[i[1] for i in categories_])
    name = StringField('Название', validators=[DataRequired()])
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')


@app.route('/income_category', methods=['GET', 'POST'])
def income_category():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    form = IncomeCategory()
    if form.validate_on_submit():
        if form.categories.data == 'Новая категория':
            alert.put(add_deposit_category(form.name.data, form.comment.data))
        else:
            for i in form.categories_:
                if i[1] == form.categories.data:
                    category = i[0]
            alert.put(edit_deposit_category(category, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/index')
    params = generate_params("Добавить", name="Доход", form=form)
    return render_template('category.html', **params)


class ExpensesCategory(FlaskForm):
    categories_ = [(str(i[0]), i[1]) for i in get_categories()]
    categories_.insert(0, ('-1', 'Новая категория'))
    categories = SelectField('Категория', validators=[DataRequired()], choices=[i[1] for i in categories_])
    name = StringField('Название', validators=[DataRequired()])
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')


@app.route('/expenses_category', methods=['GET', 'POST'])
def expenses_category():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    form = ExpensesCategory()
    if form.validate_on_submit():
        if form.categories.data == 'Новая категория':
            alert.put(add_category(form.name.data, form.comment.data))
        else:
            for i in form.categories_:
                if i[1] == form.categories.data:
                    category = i[0]
            alert.put(edit_category(category, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/index')
    params = generate_params("Добавить", name="Расход", form=form)
    return render_template('category.html', **params)


class BankAccounts(FlaskForm):
    bank_accounts_ = [(str(i[0]), i[1]) for i in get_categories()]
    bank_accounts_.insert(0, ('-1', 'Новый счет'))
    bank_accounts = SelectField('Счет', validators=[DataRequired()], choices=[i[1] for i in bank_accounts_])
    name = StringField('Название', validators=[DataRequired()])
    sum = StringField('Сумма', validators=[DataRequired()], default='0')
    comment = StringField('Описание')
    submit = SubmitField('Добавить/Изменить')


@app.route('/bank_account', methods=['GET', 'POST'])
def bank_account():
    with open(session_file, "r") as f:
        if f.read() == '':
            return redirect('/login')

    form = BankAccounts()
    if form.validate_on_submit():
        if form.bank_accounts.data == 'Новый счет':
            alert.put(add_category(form.name.data, form.comment.data))
        else:
            for i in form.bank_accounts_:
                if i[1] == form.bank_accounts.data:
                    bank_account = i[0]
            alert.put(edit_category(bank_account, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/index')
    params = generate_params("Добавить", form=form)
    return render_template('bank_account.html', **params)


@app.route('/export_xlsx')
def export_xlsx_():
    export_xlsx()
    return redirect('/static/export/export_data_FinUp.xlsx')


@app.route('/export_csv')
def export_csv_():
    export_csv()
    return redirect('/static/export/export_data_FinUp.zip')


@app.errorhandler(404)
def web404(error):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
