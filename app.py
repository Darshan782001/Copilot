from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

app = Flask(__name__)

# Azure credentials
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
AZURE_KEY = os.getenv('AZURE_KEY')

# Microsoft Teams credentials
TEAMS_CLIENT_ID = os.getenv('TEAMS_CLIENT_ID')
TEAMS_CLIENT_SECRET = os.getenv('TEAMS_CLIENT_SECRET')
TEAMS_TENANT_ID = os.getenv('TEAMS_TENANT_ID')

# Email credentials
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({'error': str(e)}), 500

@app.route('/join-call', methods=['POST'])
def join_call():
    try:
        import msal
        import requests as http_requests
        
        data = request.get_json(force=True)
        meeting_url = data.get('meeting_url')
        
        if not meeting_url:
            return jsonify({'error': 'meeting_url is required'}), 400
        
        # Get token
        authority = f'https://login.microsoftonline.com/{TEAMS_TENANT_ID}'
        app_msal = msal.ConfidentialClientApplication(
            TEAMS_CLIENT_ID, 
            authority=authority, 
            client_credential=TEAMS_CLIENT_SECRET
        )
        result = app_msal.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
        
        if 'access_token' not in result:
            return jsonify({'error': f"Token error: {result.get('error_description', 'Unknown')}"}), 400
        
        token = result['access_token']
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        payload = {
            "source": {
                "identity": {
                    "application": {
                        "displayName": "Recording Bot",
                        "id": TEAMS_CLIENT_ID
                    }
                }
            },
            "callbackUri": f"{request.url_root}api/calling",
            "requestedModalities": ["audio"],
            "mediaConfig": {
                "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
            }
        }
        
        response = http_requests.post(
            'https://graph.microsoft.com/v1.0/communications/calls',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            return jsonify({'status': 'joined', 'message': 'Bot joining call'}), 200
        else:
            return jsonify({'error': response.text}), 400
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/calling', methods=['POST'])
def calling_webhook():
    return jsonify({"status": "ok"}), 200

@app.route('/webhook/teams', methods=['POST'])
def teams_webhook():
    try:
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from datetime import datetime
        
        data = request.get_json(force=True)
        transcript = data.get('transcript', '')
        meeting_id = data.get('meeting_id', 'N/A')
        participants = data.get('participants', [])
        
        # Summarize
        client = TextAnalyticsClient(endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY))
        response = client.extract_summary([transcript], max_sentence_count=5)
        summary = ' '.join([sentence.text for doc in response for sentence in doc.sentences])
        
        # Email
        email_body = f"""
        <h2>Teams Call Summary</h2>
        <p><strong>Meeting ID:</strong> {meeting_id}</p>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p><strong>Participants:</strong> {', '.join(participants)}</p>
        <h3>Summary:</h3>
        <p>{summary}</p>
        """
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = data.get('recipient_email')
        msg['Subject'] = f'Call Summary - {meeting_id}'
        msg.attach(MIMEText(email_body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        
        return jsonify({'status': 'success', 'summary': summary}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential
        
        data = request.get_json(force=True)
        text = data.get('text', '')
        
        client = TextAnalyticsClient(endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY))
        response = client.extract_summary([text], max_sentence_count=5)
        summary = ' '.join([sentence.text for doc in response for sentence in doc.sentences])
        
        return jsonify({'summary': summary}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
