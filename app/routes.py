from flask import render_template, redirect, make_response, request
import json

from app import app

from app.logics.csv_xlsx import *
from app.logics.charts import charts
from app.forms import *
from app.ru_en import ru_en


directory_name = ['app']


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


alert = Alert()


def temp_dir():
    lang = request.args.get('lang')
    if lang and lang == 'en':
        return 'en/'
    return ''


def to_lang(word):
    lang = request.args.get('lang')
    if lang and lang == 'en':
        return ru_en[word]
    return word


def am_i_not_login():
    flag = 'id_user' not in request.cookies or request.cookies['id_user'] == 'null'
    write_request_cookies(request.cookies)
    return flag


def generate_params(title, **kwargs):
    params = {
        "alert": alert.get(),
        "username": get_full_name(),
        "title": title,
        "to_lang": to_lang
    }
    for keys, value in kwargs.items():
        params[keys] = value
    return params


@app.route('/login', methods=['GET', 'POST'])
def login_web():
    form = Login()
    if form.validate_on_submit():
        answer = login(form.email.data, form.password.data)
        if answer == "Неверный логин или пароль":
            alert.put(to_lang(answer))
            return render_template('login.html', form=form, alert=alert.get(), to_lang=to_lang)
        else:
            alert.put(to_lang("Вы вошли в аккаунт"))
            if form.remember_me.data:
                max_age = 60 * 60 * 24 * 30
            else:
                max_age = None
            resp = make_response(redirect('/' + to_lang('')))
            resp.set_cookie('id_user', str(answer[0]), max_age)
            resp.set_cookie('email', answer[1], max_age)
            resp.set_cookie('full_name', answer[2], max_age)
            return resp
    return render_template('login.html', form=form, alert=alert.get(), to_lang=to_lang)


@app.route('/register', methods=['GET', 'POST'])
def register_web():
    form = Register()
    if form.validate_on_submit():
        answer = register(form.email.data, form.password.data, form.username.data)
        if answer == "Аккаунт на эту почту уже зарегистрирован":
            alert.put(to_lang(answer))
            return render_template('register.html', form=form, alert=alert.get(), to_lang=to_lang)
        else:
            alert.put(to_lang("Поздравляем, Вы создали аккаунт!"))
            if form.remember_me.data:
                max_age = 60 * 60 * 24 * 30
            else:
                max_age = None
            resp = make_response(redirect('/' + to_lang('')))
            resp.set_cookie('id_user', str(answer[0]), max_age)
            resp.set_cookie('email', answer[1], max_age)
            resp.set_cookie('full_name', answer[2], max_age)
            return resp
    return render_template('register.html', form=form, alert=alert.get(), to_lang=to_lang)


@app.route('/logout')
def logout_web():
    resp = make_response(redirect('/login' + to_lang('')))
    if not (am_i_not_login()):
        resp.set_cookie('id_user', 'null')
        resp.set_cookie('email', 'null')
        resp.set_cookie('full_name', 'null')
        write_request_cookies({'id_user': 'null', 'full_name': 'null', 'email': 'null'})
        return resp
    return redirect('/login' + to_lang(''))


@app.route('/')
@app.route('/index')
def index():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

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
    with open(directory_name[0] + url_for('static', filename='tables/data.json'), 'w+') as file:
        json.dump(data, file, sort_keys=True, indent=4)

    summa = get_sum()
    income = get_sum_deposits()
    expense = get_sum_purchases()
    params = generate_params(to_lang("Панель управления"),
                             summa=summa, income=income, expense=expense)
    return render_template('index.html', **params)


@app.route('/income', methods=['GET', 'POST'])
def income():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

    form = Income()
    if form.validate_on_submit():
        category = 0
        for i in form.categories_data:
            if i[1] == form.categories.data:
                category = i[0]
        bank_account = 0
        for i in form.bank_accounts_data:
            if i[1] == ' '.join(form.bank_accounts.data.split(' ')[:-1]):
                bank_account = i[0]
        alert.put(
            add_deposit(category, bank_account, form.sum.data, form.date.data.strftime("%d.%m.%Y"),
                        form.comment.data))
        if alert.read() == "Данные изменены":
            alert.put(to_lang("Данные изменены"))
            return redirect('/' + to_lang(''))
    params = generate_params(to_lang("Добавить"), name=to_lang("Доход"), form=form)
    return render_template('purchase.html', **params)


@app.route('/expense', methods=['GET', 'POST'])
def expense():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

    form = Expense()
    if form.validate_on_submit():
        category = 0
        for i in form.categories_data:
            if i[1] == form.categories.data:
                category = i[0]
        bank_account = 0
        for i in form.bank_accounts_data:
            if i[1] == ' '.join(form.bank_accounts.data.split(' ')[:-1]):
                bank_account = i[0]
        alert.put(add_purchase(category, bank_account, form.sum.data,
                               form.date.data.strftime("%d.%m.%Y"), form.comment.data))
        if alert.read() == "Данные изменены":
            return redirect('/' + to_lang(''))
    params = generate_params(to_lang("Добавить"), name=to_lang("Расход"), form=form)
    return render_template('purchase.html', **params)


@app.route('/bank_accounts', methods=['GET', 'POST'])
def bank_accounts():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

    data = []
    for i in get_bank_accounts():
        d = {
            "name": i.name,
            "sum": str(i.current_sum),
            "description": i.description
        }
        data.append(d)
    with open(directory_name[0] + url_for('static', filename='tables/data1.json'), 'w+') as file:
        json.dump(data, file, indent=4)

    params = generate_params(to_lang("Счета"))
    return render_template('bank_accounts.html', **params)


@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

    data = []
    for i in get_categories():
        d = {
            "name": i.name,
            "of": to_lang("Расходов"),
            "description": i.description
        }
        data.append(d)
    for i in get_deposit_categories():
        d = {
            "name": i.name,
            "of": to_lang("Доходов"),
            "description": i.description
        }
        data.append(d)
    with open(directory_name[0] + url_for('static', filename='tables/data2.json'), 'w+') as file:
        json.dump(data, file, indent=4)

    params = generate_params(to_lang("Категории"))
    return render_template('categories.html', **params)


@app.route('/income_category', methods=['GET', 'POST'])
def income_category():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

    form = IncomeCategory()
    if form.validate_on_submit():
        if form.categories.data == 'Новая категория':
            alert.put(add_deposit_category(form.name.data, form.comment.data))
        else:
            category = 0
            for i in form.categories_data:
                if i[1] == form.categories.data:
                    category = i[0]
            alert.put(edit_deposit_category(category, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            alert.put(to_lang("Данные изменены"))
            return redirect('/' + to_lang(''))
    params = generate_params(to_lang("Добавить"), name=to_lang("Доход"), form=form)
    return render_template('category.html', **params)


@app.route('/expenses_category', methods=['GET', 'POST'])
def expenses_category():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

    form = ExpensesCategory()
    if form.validate_on_submit():
        if form.categories.data == 'Новая категория':
            alert.put(add_category(form.name.data, form.comment.data))
        else:
            category = 0
            for i in form.categories_data:
                if i[1] == form.categories.data:
                    category = i[0]
            alert.put(edit_category(category, form.name.data, form.comment.data))
        if alert.read() == "Данные изменены":
            alert.put(to_lang("Данные изменены"))
            return redirect('/' + to_lang(''))
    params = generate_params(to_lang("Добавить"), name=to_lang("Расход"), form=form)
    return render_template('category.html', **params)


@app.route('/bank_account', methods=['GET', 'POST'])
def bank_account():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

    form = BankAccounts()
    if form.validate_on_submit():
        if form.bank_accounts.data == 'Новый счет':
            alert.put(add_bank_account(form.name.data, form.sum.data, form.comment.data))
        else:
            bank_account = 0
            for i in form.bank_accounts_data:
                if i[1] == form.bank_accounts.data:
                    bank_account = i[0]
            alert.put(edit_bank_account(bank_account, form.name.data, form.sum.data, form.comment.data))
        if alert.read() == "Данные изменены":
            alert.put(to_lang("Данные изменены"))
            return redirect('/' + to_lang(''))
    params = generate_params(to_lang("Добавить"), form=form)
    return render_template('bank_account.html', **params)


@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))

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
        type = False if form.mode.data == to_lang("Доходам") else True
        charts(type, mode, form.date_start.data, form.date_end.data)
        image = url_for('static', filename='images/saved_figure.png')
        params = generate_params(to_lang("Аналитика"), form=form, image=image)
        return render_template('analytics.html', **params)
    params = generate_params(to_lang("Аналитика"), form=form)
    return render_template('analytics.html', **params)


@app.route('/export_xlsx')
def export_xlsx_web():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))
    export_xlsx()
    return redirect(url_for('static', filename='export/export_data_FinUp.xlsx'))


@app.route('/export_csv')
def export_csv_web():
    if am_i_not_login():
        return redirect('/login' + to_lang(''))
    export_csv()
    return redirect(url_for('static', filename='export/export_data_FinUp.zip'))


@app.errorhandler(404)
def web404(error):
    return render_template('404.html', to_lang=to_lang)


@app.errorhandler(500)
def web500(error):
    return render_template('500.html', to_lang=to_lang)
