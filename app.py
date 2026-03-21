from flask import Flask, request, render_template, jsonify
import os
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Google Sheets Setup Scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_gspread_client():
    # Render Environment Variable-ல் இருந்து JSON-ஐ எடுக்கிறது
    creds_json = os.environ.get('GOOGLE_CREDS_JSON')
    
    if creds_json:
        # String-ஆக இருக்கும் தகவலை Dictionary-ஆக மாற்றுகிறது
        info = json.loads(creds_json)
        # Private Key-ல் உள்ள '\n' பிரச்சனையைச் சரிசெய்கிறது (இதுதான் முக்கியம்)
        if 'private_key' in info:
            info['private_key'] = info['private_key'].replace('\\n', '\n')
        return ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    else:
        # Local-ல் உங்கள் கணினியில் செக் செய்ய (credentials.json கோப்பு இருந்தால்)
        try:
            return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        except Exception:
            return None

# Auth Setup
creds = get_gspread_client()
if creds:
    client = gspread.authorize(creds)
    # உங்கள் Google Sheet பெயர் சரியாக இருப்பதை உறுதி செய்யவும்
    sheet = client.open("PM_Data_Collection").sheet1 
else:
    print("Error: Google Credentials not found!")

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = [
            request.form.get('report_no'),
            f"{request.form.get('pm_start_date')} {request.form.get('pm_start_time')}",
            f"{request.form.get('pm_end_date')} {request.form.get('pm_end_time')}",
            request.form.get('customer') or request.form.get('customer_other'),
            request.form.get('machine_type'),
            request.form.get('machine_model'),
            request.form.get('machine_serial'),
            request.form.get('controller'),
            request.form.get('abnormalities'),
            request.form.get('first_engineer'),
            request.form.get('backup_status'),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        sheet.append_row(data)
        return jsonify({'success': True, 'message': 'Data saved to Google Sheets successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
