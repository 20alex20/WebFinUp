from app import db


class Users(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50))
    username_email = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(150))

    def __init__(self, full_name, username_email, password_hash):
        self.full_name = full_name
        self.username_email = username_email
        self.password_hash = password_hash

    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns]


class DepositCategories(db.Model):
    id_deposit_category = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))

    def __init__(self, id_user, name, description):
        self.id_user = id_user
        self.name = name
        self.description = description

    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns]


class Categories(db.Model):
    id_category = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))

    def __init__(self, id_user, name, description):
        self.id_user = id_user
        self.name = name
        self.description = description

    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns]


class BankAccounts(db.Model):
    id_bank_account = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    name = db.Column(db.String(20))
    current_sum = db.Column(db.Integer)
    description = db.Column(db.String(200))

    def __init__(self, id_user, name, current_sum, description):
        self.id_user = id_user
        self.name = name
        self.current_sum = current_sum
        self.description = description

    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns]


class Deposits(db.Model):
    id_deposit = db.Column(db.Integer, primary_key=True)
    id_deposit_category = db.Column(db.Integer,
                                    db.ForeignKey('deposit_categories.id_deposit_category'))
    id_bank_account = db.Column(db.Integer, db.ForeignKey('bank_accounts.id_bank_account'))
    sum = db.Column(db.Integer)
    date = db.Column(db.String(20))
    comment = db.Column(db.String(200))
    date_time_add = db.Column(db.String(20))

    def __init__(self, id_deposit_category, id_bank_account, sum, date, comment, date_time_add):
        self.id_deposit_category = id_deposit_category
        self.id_bank_account = id_bank_account
        self.sum = sum
        self.date = date
        self.comment = comment
        self.date_time_add = date_time_add

    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns]


class Purchases(db.Model):
    id_purchase = db.Column(db.Integer, primary_key=True)
    id_category = db.Column(db.Integer, db.ForeignKey('categories.id_category'))
    id_bank_account = db.Column(db.Integer, db.ForeignKey('bank_accounts.id_bank_account'))
    sum = db.Column(db.Integer)
    date = db.Column(db.String(20))
    comment = db.Column(db.String(200))
    date_time_add = db.Column(db.String(20))

    def __init__(self, id_category, id_bank_account, sum, date, comment, date_time_add):
        self.id_category = id_category
        self.id_bank_account = id_bank_account
        self.sum = sum
        self.date = date
        self.comment = comment
        self.date_time_add = date_time_add

    def as_list(self):
        return [getattr(self, c.name) for c in self.__table__.columns]
