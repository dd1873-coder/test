from flask import Flask, request, render_template, jsonify
import os
import json
import base64
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# உலகளாவிய வேரியபிளாக அறிவிக்கவும்
sheet = None

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Render-ல் உள்ள Base64 குறியீட்டை எடுக்கிறது
    base64_creds = os.environ.get('GOOGLE_CREDS_JSON')
    
    if base64_creds:
        try:
            # Base64-ஐ மீண்டும் அசல் JSON-ஆக மாற்றுகிறது
            decoded_creds = base64.b64decode(base64_creds).decode('utf-8')
            info = json.loads(decoded_creds)
            return ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        except Exception as e:
            print(f"Auth Error: {e}")
            return None
    else:
        # Local testing (கணினியில் credentials.json இருந்தால்)
        try:
            return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        except Exception as e:
            print(f"Local Auth Error: {e}")
            return None

def initialize_sheet():
    global sheet
    try:
        creds = get_gspread_client()
        if creds:
            client = gspread.authorize(creds)
            # உங்கள் Google Sheet பெயர் சரியாக இருப்பதை உறுதி செய்யவும்
            # 'PM_Data_Collection' என்பது உங்கள் Sheet-ன் பெயராக இருக்க வேண்டும்
            sheet = client.open("PM Data_2026-2027").sheet1
            print("Connected to Google Sheets successfully!")
        else:
            print("Credentials not found!")
    except Exception as e:
        print(f"Initialization Error: {e}")
        sheet = None

# ஆப் தொடங்கும்போதே ஒருமுறை இயக்கவும்
initialize_sheet()

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global sheet
    
    # ஒருவேளை ஷீட் கனெக்ட் ஆகவில்லை என்றால் மீண்டும் ஒருமுறை முயற்சிக்கும்
    if sheet is None:
        initialize_sheet()
        if sheet is None:
            return jsonify({'success': False, 'message': 'Database connection failed! Check logs.'})

    try:
        # Form-ல் இருந்து தகவல்களை எடுத்தல்
        data = [
            request.form.get('report_no', ''),
            f"{request.form.get('pm_start_date', '')} {request.form.get('pm_start_time', '')}",
            f"{request.form.get('pm_end_date', '')} {request.form.get('pm_end_time', '')}",
            request.form.get('customer') or request.form.get('customer_other', ''),
            request.form.get('machine_type', ''),
            request.form.get('machine_model', ''),
            request.form.get('machine_serial', ''),
            request.form.get('controller', ''),
            request.form.get('abnormalities', ''),
            request.form.get('first_engineer', ''),
            request.form.get('backup_status', ''),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]

        sheet.append_row(data)
        return jsonify({'success': True, 'message': 'Data saved to Google Sheets successfully!'})
    except Exception as e:
        print(f"Submit Error: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

if __name__ == "__main__":
    # Render-ல் போர்ட் தானாக அமையும், லோக்கலில் 5000-ல் இயங்கும்
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
