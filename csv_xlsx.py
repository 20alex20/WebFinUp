import xlsxwriter
from sql import get_all_data
from zipfile import ZipFile

headers2 = {
    "categories": ("id_category", "name", "description"),
    "deposit_categories": ("id_deposit_category", "name", "description"),
    "purchases": ("id_purchase", "id_category", "id_bank_account", "sum", "date", "comment"),
    "bank_accounts": ("id_bank_account", "name", "current_sum", "description"),
    "deposits": ("id_deposit", "id_category", "id_bank_account", "sum", "date", "comment"),
}
d = 'static/export'


def export_xlsx():
    workbook = xlsxwriter.Workbook(d + '/export_data_FinUp.xlsx')
    for name, cur_list in zip(sorted(headers2), get_all_data()):
        headers = headers2[name]
        worksheet = workbook.add_worksheet(name=name)
        for column, i in enumerate(headers):
            worksheet.write(0, column, i)
        for row, i in enumerate(cur_list):
            for column, j in enumerate(i):
                worksheet.write(row + 1, column, j)
    workbook.close()
    return "Осуществлен экспорт"


def export_csv():
    with ZipFile(d + '/export_data_FinUp.zip', 'w') as myzip:
        for name, cur_list in zip(sorted(headers2), get_all_data()):
            headers = headers2[name]
            string = ';'.join(headers) + '\n'
            for i in cur_list:
                string += ';'.join(map(str, i)) + '\n'
            myzip.writestr(f'export_data_FinUp_{name}.csv', string.encode('windows-1251'))
    return "Осуществлен экспорт"
