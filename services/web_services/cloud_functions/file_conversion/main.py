from convert_xls_to_xlsx import convert_xls_to_xlsx as cnv_xls2xlsx
from convert_xls_to_csv import convert_xls_to_csv as cnv_xls2csv
from convert_xls_to_ods import convert_xls_to_ods as cnv_xls2ods
from convert_xlsx_to_xls import convert_xlsx_to_xls as cnv_xlsx2xls
from convert_xlsx_to_csv import convert_xlsx_to_csv as cnv_xlsx2csv
from convert_xlsx_to_ods import convert_xlsx_to_ods as cnv_xlsx2ods
from convert_csv_to_xls import convert_csv_to_xls as cnv_csv2xls
from convert_csv_to_xlsx import convert_csv_to_xlsx as cnv_csv2xlsx
from convert_csv_to_ods import convert_csv_to_ods as cnv_csv2ods

# Entry point for convert_xls_to_xlsx
def convert_xls_to_xlsx(request):
    return cnv_xls2xlsx(request)

# Entry point for convert_xls_to_csv
def convert_xls_to_csv(request):
    return cnv_xls2csv(request)

# Entry point for convert_xls_to_ods
def convert_xls_to_ods(request):
    return cnv_xls2ods(request)

# Entry point for convert_xlsx_to_xls
def convert_xlsx_to_xls(request):
    return cnv_xlsx2xls(request)

# Entry point for convert_xlsx_to_csv
def convert_xlsx_to_csv(request):
    return cnv_xlsx2csv(request)

# Entry point for convert_xlsx_to_ods
def convert_xlsx_to_ods(request):
    return cnv_xlsx2ods(request)

# Entry point for convert_csv_to_xls
def convert_csv_to_xls(request):
    return cnv_csv2xls(request)

# Entry point for convert_csv_to_xlsx
def convert_csv_to_xlsx(request):
    return cnv_csv2xlsx(request)

# Entry point for convert_csv_to_ods
def convert_csv_to_ods(request):
    return cnv_csv2ods(request)
