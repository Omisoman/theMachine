import io
import pandas as pd
from google.cloud import storage


def convert_csv_to_xlsx(request):
    file = request.files.get('file')

    if file and file.filename.endswith('.csv'):
        try:
            csv_df = pd.read_csv(file)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                csv_df.to_excel(writer, index=False)

            output.seek(0)

            return output.read(), 200, {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename="converted_file.xlsx"'
            }
        except Exception as e:
            return f"Error processing file: {str(e)}", 500

    return "Invalid file format, expecting .csv", 400
