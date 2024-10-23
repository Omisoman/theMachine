import os
import pandas as pd
from flask import jsonify, request
from utils import get_encryption_key, decrypt_data, encrypt_data
import io  # Import io for StringIO

def convert_csv_to_xlsx(request):
    """Converts a CSV file to XLSX"""
    try:
        print("Starting to process the request.")

        # Get the encryption key
        key = get_encryption_key()
        print("Encryption key retrieved successfully.")

        # Get the file from the request
        if 'file' not in request.files:
            print("No file part in the request.")
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        print("File received:", file.filename)

        try:
            # Decrypt the file content
            decrypted_file_data = decrypt_data(file.read(), key)
            print("Decryption completed successfully.")
        except Exception as decryption_error:
            print("Error during decryption:", str(decryption_error))
            return jsonify({"error": "Decryption failed", "details": str(decryption_error)}), 400

        try:
            # Load CSV into a pandas dataframe using io.StringIO
            df = pd.read_csv(io.StringIO(decrypted_file_data.decode('utf-8')))
            print("CSV loaded into pandas dataframe.")
        except Exception as csv_error:
            print("Error loading CSV:", str(csv_error))
            return jsonify({"error": "Loading CSV failed", "details": str(csv_error)}), 400

        try:
            # Convert to XLSX format
            output_file = "/tmp/output.xlsx"
            df.to_excel(output_file, index=False)
            print("Dataframe saved as XLSX.")

            # Read the XLSX file and encrypt the content
            with open(output_file, 'rb') as f:
                encrypted_data = encrypt_data(f.read(), key)
            print("File encryption completed successfully.")

            # Return the encrypted file as the response
            return encrypted_data, 200, {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
        except Exception as conversion_error:
            print("Error during file conversion or encryption:", str(conversion_error))
            return jsonify({"error": "File conversion or encryption failed", "details": str(conversion_error)}), 500
    except Exception as e:
        print("An error occurred in the main process:", str(e))
        return jsonify({"error": str(e)}), 500
