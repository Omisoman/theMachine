import io
import pandas as pd
from google.cloud import storage


def convert_csv_to_ods(request):
    file = request.files.get('file')

    if file and file.filename.endswith('.csv'):
        try:
            csv_df = pd.read_csv(file)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='odf') as writer:
                csv_df.to_excel(writer, index=False)

            output.seek(0)

            return output.read(), 200, {
                'Content-Type': 'application/vnd.oasis.opendocument.spreadsheet',
                'Content-Disposition': 'attachment; filename="converted_file.ods"'
            }
        except Exception as e:
            return f"Error processing file: {str(e)}", 500

    return "Invalid file format, expecting .csv", 400
