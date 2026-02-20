from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import msal
import requests as http_requests
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes
import asyncio
from aiohttp import web

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

# Bot Framework Adapter
settings = BotFrameworkAdapterSettings(TEAMS_CLIENT_ID, TEAMS_CLIENT_SECRET)
adapter = BotFrameworkAdapter(settings)

call_transcripts = {}

class TeamsCallBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            text = turn_context.activity.text
            call_id = turn_context.activity.conversation.id
            
            if call_id not in call_transcripts:
                call_transcripts[call_id] = []
            call_transcripts[call_id].append(text)
            
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            await turn_context.send_activity("Recording bot joined")

bot = TeamsCallBot()

def get_teams_token():
    authority = f'https://login.microsoftonline.com/{TEAMS_TENANT_ID}'
    app_msal = msal.ConfidentialClientApplication(
        TEAMS_CLIENT_ID, 
        authority=authority, 
        client_credential=TEAMS_CLIENT_SECRET
    )
    result = app_msal.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
    
    if 'access_token' in result:
        return result['access_token']
    else:
        raise Exception(f"Failed to get token: {result.get('error_description', 'Unknown error')}")

def get_azure_client():
    return TextAnalyticsClient(endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY))

def summarize_text(text):
    client = get_azure_client()
    response = client.extract_summary([text], max_sentence_count=5)
    return ' '.join([sentence.text for doc in response for sentence in doc.sentences])

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

@app.route('/api/messages', methods=['POST'])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        body = request.json
    else:
        return jsonify({"error": "Invalid content type"}), 415

    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def call_func(turn_context):
        await bot.on_turn(turn_context)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(adapter.process_activity(activity, auth_header, call_func))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

@app.route('/join-call', methods=['POST'])
def join_call():
    try:
        print("=== Join Call Request ===")
        print(f"Content-Type: {request.headers.get('Content-Type')}")
        print(f"Request data: {request.data}")
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        meeting_url = data.get('meeting_url')
        if not meeting_url:
            return jsonify({'error': 'meeting_url is required'}), 400
        
        print(f"Meeting URL: {meeting_url}")
        print("Getting Teams token...")
        
        token = get_teams_token()
        print(f"Token obtained: {token[:20]}...")
        
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
        
        print(f"Calling Graph API...")
        response = http_requests.post(
            'https://graph.microsoft.com/v1.0/communications/calls',
            headers=headers,
            json=payload
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code in [200, 201]:
            return jsonify({'status': 'joined', 'message': 'Bot joining call'}), 200
        else:
            return jsonify({'error': f'Graph API error: {response.text}'}), 400
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/calling', methods=['POST'])
def calling_webhook():
    data = request.json
    return jsonify({"status": "ok"}), 200

@app.route('/webhook/teams', methods=['POST'])
def teams_webhook():
    try:
        data = request.json
        transcript = data.get('transcript', '')
        meeting_id = data.get('meeting_id', 'N/A')
        participants = data.get('participants', [])
        
        summary = summarize_text(transcript)
        
        email_body = f"""
        <h2>Teams Call Summary</h2>
        <p><strong>Meeting ID:</strong> {meeting_id}</p>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p><strong>Participants:</strong> {', '.join(participants)}</p>
        <h3>Summary:</h3>
        <p>{summary}</p>
        <h3>Full Transcript:</h3>
        <p>{transcript}</p>
        """
        
        send_email(data.get('recipient_email'), f'Call Summary - {meeting_id}', email_body)
        
        return jsonify({'status': 'success', 'summary': summary}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        text = data.get('text', '')
        summary = summarize_text(text)
        return jsonify({'summary': summary}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
