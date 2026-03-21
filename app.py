from flask import Flask, request, render_template, jsonify
import os
from datetime import datetime
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# 'credentials.json' கோப்பு உங்கள் மெயின் ஃபோல்டரில் இருக்க வேண்டும்
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
# உங்கள் Google Sheet பெயரைக் கீழே கொடுக்கவும்
sheet = client.open("PM_Data_Collection").sheet1 

ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEOS = {'mp4', 'mov', 'avi'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Form Data சேகரிப்பு
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

        # Google Sheet-ல் தரவைச் சேர்த்தல்
        sheet.append_row(data)
        
        return jsonify({'success': True, 'message': 'Data saved to Google Sheets successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
