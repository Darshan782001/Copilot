# Teams Recording Webhook Setup (Simplified Approach)

## How It Works

1. Users manually record Teams calls (built-in Teams recording)
2. After call ends, recording is saved to SharePoint/OneDrive
3. User or automated process sends recording details to your webhook
4. Your app processes transcript, generates AI summary, and emails report

## Setup Steps

### 1. Enable Teams Cloud Recording
- Teams Admin Center → Meetings → Meeting policies
- Enable "Cloud recording"
- Recordings auto-save to OneDrive/SharePoint

### 2. Get Recording Transcript
Teams automatically generates transcripts for recorded meetings.

**To access:**
- Open Teams → Calendar → Past meeting
- Click "Recording" → "View transcript"
- Copy transcript text

### 3. Use the App

**Option A: Manual UI**
1. Go to http://localhost:5000
2. Click "Process Recording" tab
3. Fill in:
   - Meeting ID
   - Recording URL (from SharePoint/OneDrive)
   - Transcript (paste from Teams)
   - Participants
   - Recipient email
4. Click "Process & Send Summary"

**Option B: Automated Webhook**
Send POST request to `/webhook/recording`:
```json
{
  "meetingId": "MEET-123",
  "recordingUrl": "https://sharepoint.com/recording.mp4",
  "transcript": "Full transcript text...",
  "participants": ["user1@example.com", "user2@example.com"],
  "recipientEmail": "manager@example.com"
}
```

### 4. Automate with Power Automate (Optional)

Create Power Automate flow:
1. Trigger: "When a file is created" (SharePoint - Recordings folder)
2. Action: "Get file content"
3. Action: "HTTP POST" to your webhook endpoint

## Benefits of This Approach

✅ No complex bot infrastructure needed
✅ Uses native Teams recording (reliable)
✅ Works immediately
✅ Transcripts included automatically
✅ Recordings stored in SharePoint (compliance)

## Next Steps

1. Update `.env` with your email credentials
2. Run: `python app.py`
3. Test with a recorded Teams meeting
