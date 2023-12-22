from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import *


def format(string, *args):
    for i in args:
        ind1 = string.index('{')
        ind2 = string.index('}')
        string = string[:ind1] + str(i) + string[ind2 + 1:]
    return string


request_cookies = {'id_user': 0, 'full_name': None, 'email': None}


def write_request_cookies(object):
    global request_cookies
    request_cookies = object


def get_id_user():
    return int(request_cookies.get('id_user'))


def get_full_name():
    return request_cookies.get('full_name')


def get_username_email():
    return request_cookies.get('email')


def to_line_list(arr, cut=None):
    ans = []
    for i in arr:
        if cut is not None:
            i = i[:cut]
        ans.extend(map(str, i))
    return ans


def get_all_data():
    return [get_bank_accounts(), get_purchase(), get_categories(), get_deposits(),
            get_deposit_categories()]


def login(username_email, password):
    ans = Users.query.filter_by(username_email=username_email).first()
    if ans and check_password_hash(ans.password_hash, password):
        id_user = ans.id_user
        full_name = ans.full_name
        return id_user, username_email, full_name
    return "Неверный логин или пароль"


default = ["Автомобиль", "Отдых и развлечения", "Продукты", "Кафе и растораны", "Одежда",
           "Здоровье и фитнес", "Подарки", "Поездки"]
default1 = ["Зарплата", "Аренда", "Родственники"]


def register(username_email, password, full_name):
    ans = Users.query.filter_by(username_email=username_email).first()
    if ans:
        return "Аккаунт на эту почту уже зарегистрирован"
    new_user = Users(full_name, username_email, generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()

    message = login(username_email, password)
    if message != "Неверный логин или пароль":
        write_request_cookies({'id_user': message[0], 'email': message[1], 'full_name': message[2]})
        for i in default:
            add_category(i, "")
        for j in default1:
            add_deposit_category(j, "")
        add_bank_account("Наличные", 0, "")
    return message


def add_category(name, description=""):
    if Categories.query.filter_by(id_user=get_id_user(), name=name).first():
        return "Категория с таким названием уже существует"
    new_category = Categories(get_id_user(), name, description)
    db.session.add(new_category)
    db.session.commit()
    return "Данные изменены"


def get_categories():
    return Categories.query.filter_by(id_user=get_id_user())


def edit_category(id_category, name, description):
    ans = Categories.query.filter_by(id_user=get_id_user(), name=name).first()
    if ans and ans.id_category != id_category:
        return "Категория с таким названием уже существует"
    category = Categories.query.filter_by(id_category=id_category).first()
    category.name = name
    category.description = description
    db.session.commit()
    return "Данные изменены"


def add_deposit_category(name, description=""):
    if DepositCategories.query.filter_by(id_user=get_id_user(), name=name).first():
        return "Категория с таким названием уже существует"
    new_category = DepositCategories(get_id_user(), name, description)
    db.session.add(new_category)
    db.session.commit()
    return "Данные изменены"


def get_deposit_categories():
    return DepositCategories.query.filter_by(id_user=get_id_user())


def edit_deposit_category(id_deposit_category, name, description):
    ans = DepositCategories.query.filter_by(id_user=get_id_user(), name=name).first()
    if ans and ans != id_deposit_category:
        return "Категория с таким названием уже существует"
    category = DepositCategories.query.filter_by(id_deposit_category=id_deposit_category).first()
    category.name = name
    category.description = description
    db.session.commit()
    return "Данные изменены"


def add_bank_account(name, current_sum, description=""):
    if BankAccounts.query.filter_by(id_user=get_id_user(), name=name).first():
        return "Счет с таким названием уже существует"
    new_category = BankAccounts(get_id_user(), name, current_sum, description)
    db.session.add(new_category)
    db.session.commit()
    return "Данные изменены"


def get_bank_accounts():
    return BankAccounts.query.filter_by(id_user=get_id_user())


def edit_bank_account(id_bank_account, name, sum, description=""):
    ans = BankAccounts.query.filter_by(id_user=get_id_user(), name=name).first()
    if ans and ans.id_bank_account != id_bank_account:
        return "Счет с таким названием уже существует"
    bank_account = BankAccounts.query.filter_by(id_bank_account=id_bank_account).first()
    bank_account.name = name
    bank_account.current_sum = sum
    bank_account.description = description
    db.session.commit()
    return "Данные изменены"


def add_purchase(id_category, id_bank_account, sum, date, comment):
    ans = BankAccounts.query.filter_by(id_bank_account=id_bank_account).first()
    if ans.current_sum < int(sum):
        return "Средств недостаточно"
    ans.current_sum -= int(sum)
    new_purchase = Purchases(id_category, id_bank_account, int(sum), date, comment,
                             dt.now().strftime("%Y.%m.%d %H:%M:%S"))
    db.session.add(new_purchase)
    db.session.commit()
    return "Данные изменены"


def get_purchase():
    return Purchases.query.outerjoin(Categories, Categories.id_category == Purchases.id_category
                                     and Categories.id_user == get_id_user())


def add_deposit(id_deposit_category, id_bank_account, sum, date, comment):
    ans = BankAccounts.query.filter_by(id_bank_account=id_bank_account).first()
    ans.current_sum += int(sum)
    new_purchase = Deposits(id_deposit_category, id_bank_account, int(sum), date, comment,
                            dt.now().strftime("%Y.%m.%d %H:%M:%S"))
    db.session.add(new_purchase)
    db.session.commit()
    return "Данные изменены"


def get_deposits():
    return Deposits.query.outerjoin(DepositCategories, DepositCategories.id_deposit_category ==
                                    Deposits.id_deposit_category and
                                    DepositCategories.id_user == get_id_user())


def get_purchase_deposit(type, elem):
    if type:
        return Purchases.query.filter_by(id_category=elem.id_category)
    else:
        return Deposits.query.filter_by(id_deposit_category=elem.id_deposit_category)


def get_sum():
    sum = 0
    for elem in get_bank_accounts():
        sum += elem.current_sum
    return str(sum) + ' ₽'


def get_sum_deposits():
    sum = 0
    now = [int(i) for i in dt.now().strftime("%m.%Y").split(".")]
    for elem in get_deposits():
        dd = [int(i) for i in elem.date.split(".")][1:]
        if dd == now:
            sum += elem.sum
    return str(sum) + ' ₽'


def get_sum_purchases():
    sum = 0
    now = [int(i) for i in dt.now().strftime("%m.%Y").split(".")]
    for elem in get_purchase():
        dd = [int(i) for i in elem.date.split(".")][1:]
        if dd == now:
            sum += elem.sum
    return str(sum) + ' ₽'


def get_category_name(id_category):
    return Categories.query.filter_by(id_category=id_category).first().name


def get_deposit_category_name(id_deposit_category):
    return DepositCategories.query.filter_by(id_deposit_category=id_deposit_category).first().name


def get_bank_acc_name(id_bank_account):
    return BankAccounts.query.filter_by(id_bank_account=id_bank_account).first().name


def get_all():
    ans = []
    for i in get_deposits():
        ans.append([get_deposit_category_name(i.id_deposit_category),
                    get_bank_acc_name(i.id_bank_account), i.sum, i.date, i.comment])
    for i in get_purchase():
        ans.append([get_category_name(i.id_category),  get_bank_acc_name(i.id_bank_account),
                    i.sum, i.date, i.comment])
    ans = sorted(ans, key=lambda x: [int(i) for i in x[3].split('.')[::-1]], reverse=True)
    for i in range(len(ans)):
        ans[i].append(i)
    return ans
