import io
import pandas as pd
from google.cloud import storage


def convert_xls_to_csv(request):
    file = request.files.get('file')

    if file and file.filename.endswith('.xls'):
        try:
            # Load the xls file into a Pandas DataFrame
            xls_df = pd.read_excel(file, sheet_name=None)

            # Prepare a buffer for the csv output
            output = io.BytesIO()
            for sheet_name, sheet_data in xls_df.items():
                csv_data = sheet_data.to_csv(index=False)
                output.write(csv_data.encode('utf-8'))

            output.seek(0)

            return output.read(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename="converted_file.csv"'
            }
        except Exception as e:
            return f"Error processing file: {str(e)}", 500

    return "Invalid file format, expecting .xls", 400
