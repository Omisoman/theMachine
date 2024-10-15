import io
import pandas as pd
from google.cloud import storage


def convert_xlsx_to_xls(request):
    file = request.files.get('file')

    if file and file.filename.endswith('.xlsx'):
        try:
            xlsx_df = pd.read_excel(file, sheet_name=None)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlrd') as writer:  # Use the 'xls' writer
                for sheet_name, sheet_data in xlsx_df.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

            output.seek(0)

            return output.read(), 200, {
                'Content-Type': 'application/vnd.ms-excel',
                'Content-Disposition': 'attachment; filename="converted_file.xls"'
            }
        except Exception as e:
            return f"Error processing file: {str(e)}", 500

    return "Invalid file format, expecting .xlsx", 400
