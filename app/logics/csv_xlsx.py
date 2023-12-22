from flask import url_for

from app.logics.sql import get_all_data

import xlsxwriter
from zipfile import ZipFile

headers2 = {
    "incomes_categories": ("id_incomes_category", "name", "description"),
    "expenses_categories": ("id_expenses_category", "name", "description"),
    "bank_accounts": ("id_bank_account", "name", "current_sum", "description"),
    "incomes": ("id_income", "id_incomes_categories", "id_bank_account", "sum", "date", "comment"),
    "expenses": ("id_expense", "id_expenses_category", "id_bank_account", "sum", "date", "comment")
}


def export_xlsx():
    workbook = xlsxwriter.Workbook('app' +
                                   url_for('static', filename='export/export_data_FinUp.xlsx'))
    for name, cur_list in zip(sorted(headers2), get_all_data()):
        headers = headers2[name]
        worksheet = workbook.add_worksheet(name=name)
        for column, i in enumerate(headers):
            worksheet.write(0, column, i)
        for row, i in enumerate(cur_list):
            for column, j in enumerate(i.as_list()):
                worksheet.write(row + 1, column, j)
    workbook.close()
    return "Осуществлен экспорт"


def export_csv():
    with ZipFile('app' + url_for('static', filename='export/export_data_FinUp.zip'), 'w') as myzip:
        for name, cur_list in zip(sorted(headers2), get_all_data()):
            headers = headers2[name]
            string = ';'.join(headers) + '\n'
            for i in cur_list:
                string += ';'.join(map(str, i.as_list())) + '\n'
            myzip.writestr(f'export_data_FinUp_{name}.csv', string.encode('windows-1251'))
    return "Осуществлен экспорт"
