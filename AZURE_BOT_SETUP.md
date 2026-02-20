# Azure Bot Service Setup for Teams Call Recording

## Problem
Your app needs to be registered as a Teams Bot to join calls. Regular app registration is not enough.

## Solution: Create Azure Bot Service

### Step 1: Create Bot in Azure Portal
1. Go to Azure Portal
2. Search for "Azure Bot" and click "Create"
3. Fill in:
   - Bot handle: `teamsrecordingbot` (unique name)
   - Subscription: Your subscription
   - Resource group: Create new or use existing
   - Pricing tier: F0 (Free)
   - Microsoft App ID: Select "Use existing app registration"
   - App ID: `e864c097-1bf4-4d27-8fb0-d6fcc2aceea1`
4. Click "Create"

### Step 2: Configure Bot
1. Go to your Bot resource
2. Click "Configuration" (left menu)
3. Set Messaging endpoint: `https://your-domain.com/api/messages` (use ngrok for local testing)
4. Enable "Microsoft Teams" channel
5. Click "Save"

### Step 3: Enable Teams Channel
1. In Bot resource, click "Channels"
2. Click "Microsoft Teams" icon
3. Enable "Calling" tab
4. Set Webhook for calling: `https://your-domain.com/api/calling`
5. Click "Apply"

### Step 4: Grant Permissions
1. Go to App Registrations → Your App
2. API Permissions → Add:
   - `Calls.JoinGroupCallAsGuest.All`
   - `Calls.AccessMedia.All`
   - `OnlineMeetings.Read.All`
3. Grant admin consent

### Step 5: Use ngrok for Local Testing
```bash
ngrok http 5000
```
Copy the https URL and update bot messaging endpoint.

### Step 6: Update .env
```
TEAMS_BOT_ID=e864c097-1bf4-4d27-8fb0-d6fcc2aceea1
TEAMS_BOT_PASSWORD=your_client_secret_value
```

## Alternative: Simplified Approach (No Bot Join)

Since joining calls as a bot requires complex infrastructure (media servers, webhooks, etc.), consider these alternatives:

### Option A: Teams Recording Policy
Enable automatic cloud recording in Teams admin center - recordings go to OneDrive/SharePoint.

### Option B: Manual Recording + Webhook
1. Users manually record calls in Teams
2. Teams sends recording URL to your webhook
3. Your app downloads, transcribes, and summarizes

### Option C: Graph API - Get Existing Recordings
Use Graph API to fetch recordings after calls end:
```
GET /users/{userId}/onlineMeetings/{meetingId}/recordings
```

Would you like me to implement Option B or C instead? These are much simpler and don't require bot infrastructure.
