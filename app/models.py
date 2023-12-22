from app import db


class Users(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50))
    username_email = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(150))


class DepositCategories(db.Model):
    id_deposit_category = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))


class Categories(db.Model):
    id_category = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))


class BankAccounts(db.Model):
    id_bank_account = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id_user'))
    name = db.Column(db.String(20))
    current_sum = db.Column(db.Integer)
    description = db.Column(db.String(200))


class Deposits(db.Model):
    id_deposit = db.Column(db.Integer, primary_key=True)
    id_deposit_category = db.Column(db.Integer,
                                    db.ForeignKey('deposit_categories.id_deposit_category'))
    id_bank_account = db.Column(db.Integer, db.ForeignKey('bank_accounts.id_bank_account'))
    sum = db.Column(db.Integer)
    date = db.Column(db.String(20))
    comment = db.Column(db.String(200))
    date_time_add = db.Column(db.String(20))


class Purchases(db.Model):
    id_purchase = db.Column(db.Integer, primary_key=True)
    id_category = db.Column(db.Integer, db.ForeignKey('categories.id_category'))
    id_bank_account = db.Column(db.Integer, db.ForeignKey('bank_accounts.id_bank_account'))
    sum = db.Column(db.Integer)
    date = db.Column(db.String(20))
    comment = db.Column(db.String(200))
    date_time_add = db.Column(db.String(20))
