from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for demo purposes
# In a real application, use a database
messages = []
next_id = 1

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the API",
        "endpoints": {
            "GET /api/messages": "Retrieve all messages",
            "POST /api/messages": "Create a new message"
        }
    })

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@app.route('/api/messages', methods=['POST'])
def create_message():
    global next_id
    
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'message' not in data:
            return jsonify({"error": "Name and message are required"}), 400
        
        new_message = {
            "id": next_id,
            "name": data['name'],
            "message": data['message'],
            "timestamp": datetime.now().isoformat()
        }
        
        messages.append(new_message)
        next_id += 1
        
        return jsonify(new_message), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
