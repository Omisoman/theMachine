import io
import pandas as pd
from google.cloud import storage


def convert_xls_to_ods(request):
    file = request.files.get('file')

    if file and file.filename.endswith('.xls'):
        try:
            xls_df = pd.read_excel(file, sheet_name=None)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='odf') as writer:  # Use ODS writer
                for sheet_name, sheet_data in xls_df.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

            output.seek(0)

            return output.read(), 200, {
                'Content-Type': 'application/vnd.oasis.opendocument.spreadsheet',
                'Content-Disposition': 'attachment; filename="converted_file.ods"'
            }
        except Exception as e:
            return f"Error processing file: {str(e)}", 500

    return "Invalid file format, expecting .xls", 400
