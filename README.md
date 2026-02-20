# Teams Call Recording & AI Summarization

Flask app for Microsoft Teams call recording with Azure AI summarization and automated email reporting.

## Quick Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
- Copy `.env.example` to `.env`
- Add your Azure AI credentials
- Add email SMTP credentials

3. **Run the app:**
```bash
python app.py
```

## API Endpoints

### POST /webhook/teams
Receives Teams call data, summarizes, and emails report.

**Request:**
```json
{
  "meeting_id": "MEET-123",
  "transcript": "Full meeting transcript...",
  "participants": ["user1@example.com", "user2@example.com"],
  "recipient_email": "manager@example.com"
}
```

### POST /summarize
Summarizes any text using Azure AI.

**Request:**
```json
{
  "text": "Long text to summarize..."
}
```

### GET /health
Health check endpoint.

## Azure Setup

1. Create Azure Cognitive Services resource
2. Get endpoint and key from Azure Portal
3. Add to `.env` file

## Email Setup (Gmail)

1. Enable 2-Factor Authentication
2. Generate App Password at: https://myaccount.google.com/apppasswords
3. Use app password in `.env`

## Testing

```bash
python test_app.py
```
