from flask import Flask, request, render_template, jsonify
import os
import json
import base64
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# உலகளாவிய வேரியபிளாக (Global Variable) அறிவிக்கவும்
sheet = None

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    base64_creds = os.environ.get('GOOGLE_CREDS_JSON')
    
    if base64_creds:
        try:
            decoded_creds = base64.b64decode(base64_creds).decode('utf-8')
            info = json.loads(decoded_creds)
            return ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        except Exception as e:
            print(f"Auth Error: {e}")
            return None
    else:
        try:
            return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        except Exception:
            return None

# Google Sheet-ஐத் தொடங்கும் பங்க்ஷன்
def initialize_google_sheet():
    global sheet # 'sheet' வேரியபிளை உலகளாவியதாக மாற்றுகிறது
    try:
        creds = get_gspread_client()
        if creds:
            client = gspread.authorize(creds)
            # உங்கள் Google Sheet பெயர் சரியாக இருப்பதை உறுதி செய்யவும்
            sheet = client.open("PM_Data_Collection").sheet1
            print("Successfully connected to Google Sheets!")
        else:
            print("Credentials initialization failed!")
    except Exception as e:
        print(f"Failed to open Google Sheet: {e}")

# ஆப் தொடங்கும்போதே ஷீட்டை கனெக்ட் செய்யவும்
initialize_google_sheet()

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global sheet # பங்க்ஷனுக்குள் வெளியே உள்ள 'sheet'-ஐப் பயன்படுத்த இது அவசியம்
    
    # ஒருவேளை ஷீட் கனெக்ட் ஆகவில்லை என்றால் மீண்டும் முயற்சிக்கும்
    if sheet is None:
        initialize_google_sheet()
        if sheet is None:
            return jsonify({'success': False, 'message': 'Database connection failed!'})

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
        print(f"Submit Error: {e}")
        return jsonify({'success': False, 'message': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
