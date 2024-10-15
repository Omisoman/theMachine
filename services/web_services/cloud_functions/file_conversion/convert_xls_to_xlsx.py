import io
import pandas as pd
from google.cloud import storage


def convert_xls_to_xlsx(request):
    # Expect the xls file as binary from the request
    file = request.files.get('file')

    if file and file.filename.endswith('.xls'):
        try:
            # Load the xls file into a Pandas DataFrame
            xls_df = pd.read_excel(file, sheet_name=None)

            # Prepare a buffer for the xlsx output
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for sheet_name, sheet_data in xls_df.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)

            # Rewind the buffer
            output.seek(0)

            # Return the buffer as an xlsx file in binary
            return output.read(), 200, {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename="converted_file.xlsx"'
            }
        except Exception as e:
            return f"Error processing file: {str(e)}", 500

    return "Invalid file format, expecting .xls", 400
