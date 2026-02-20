# Full Teams Bot Setup Guide

## Prerequisites
- Azure subscription
- Teams admin access
- Public HTTPS endpoint (use ngrok for testing)

## Step 1: Create Azure Bot Service

1. Go to Azure Portal (portal.azure.com)
2. Click "Create a resource" → Search "Azure Bot"
3. Click "Create"
4. Fill in:
   - **Bot handle**: `teamsrecordingbot` (unique name)
   - **Subscription**: Your subscription
   - **Resource group**: Create new or existing
   - **Pricing tier**: F0 (Free)
   - **Type of App**: Multi Tenant
   - **Creation type**: Use existing app registration
   - **App ID**: `e864c097-1bf4-4d27-8fb0-d6fcc2aceea1`
5. Click "Review + Create" → "Create"

## Step 2: Configure Bot Messaging Endpoint

1. Install ngrok: https://ngrok.com/download
2. Run ngrok:
   ```bash
   ngrok http 5000
   ```
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. In Azure Bot resource → Configuration:
   - **Messaging endpoint**: `https://abc123.ngrok.io/api/messages`
   - Click "Apply"

## Step 3: Enable Teams Channel

1. In Azure Bot → Channels
2. Click "Microsoft Teams" icon
3. Click "Calling" tab
4. Enable "Calling"
5. **Webhook for calling**: `https://abc123.ngrok.io/api/calling`
6. Click "Apply"

## Step 4: Grant API Permissions

1. Go to Azure Portal → App Registrations
2. Find app: `e864c097-1bf4-4d27-8fb0-d6fcc2aceea1`
3. Click "API permissions" → "Add a permission"
4. Select "Microsoft Graph" → "Application permissions"
5. Add these permissions:
   - `Calls.JoinGroupCall.All`
   - `Calls.JoinGroupCallAsGuest.All`
   - `Calls.AccessMedia.All`
   - `Calls.Initiate.All`
   - `Calls.InitiateGroupCall.All`
   - `OnlineMeetings.Read.All`
   - `OnlineMeetings.ReadWrite.All`
6. Click "Grant admin consent for [Tenant]" (CRITICAL!)
7. Wait 5-10 minutes for propagation

## Step 5: Update Environment Variables

Update `.env`:
```
TEAMS_CLIENT_ID=e864c097-1bf4-4d27-8fb0-d6fcc2aceea1
TEAMS_CLIENT_SECRET=<your_new_secret_value>
TEAMS_TENANT_ID=b6ad3b74-02d8-4bab-a4fb-1b6607a159b9
```

## Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 7: Run the Bot

```bash
python app_bot.py
```

Keep ngrok running in another terminal.

## Step 8: Test

1. Go to http://localhost:5000
2. Create a Teams meeting
3. Copy meeting URL
4. Paste in "Join Teams Call" tab
5. Click "Join Call as Bot"
6. Bot should appear in the meeting

## Troubleshooting

### Error: "Application is not registered in our store"
- Ensure Azure Bot Service is created (not just app registration)
- Verify Teams channel is enabled
- Check messaging endpoint is correct

### Error: "Invalid client secret"
- Create NEW client secret in App Registrations
- Copy the VALUE (not ID)
- Update .env file

### Error: "Forbidden" or "Unauthorized"
- Grant admin consent for API permissions
- Wait 10 minutes after granting consent
- Restart the app

### Bot doesn't join call
- Verify ngrok is running
- Check messaging endpoint matches ngrok URL
- Ensure calling webhook is configured
- Check bot has calling permissions

## Important Notes

⚠️ **ngrok URL changes** every time you restart it (free tier). Update bot endpoints each time.

⚠️ **Admin consent** is required - regular users cannot grant these permissions.

⚠️ **Media infrastructure** - For production, you need dedicated media servers. This setup is for testing only.

## Production Deployment

For production:
1. Deploy to Azure App Service with public HTTPS
2. Update bot endpoints to production URL
3. Set up proper media server infrastructure
4. Configure call recording storage
5. Implement proper authentication and security
