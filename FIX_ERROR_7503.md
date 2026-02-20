# FIX: Application is not registered in our store

## The Problem
Your app `cd454696-161c-4266-9212-6a787fa58145` is NOT registered as a Teams Bot.
You only have an App Registration, but you need an Azure Bot Service.

## THE FIX - Do These Steps NOW:

### Step 1: Create Azure Bot Service
1. Open: https://portal.azure.com/#create/Microsoft.AzureBot
2. Fill in:
   - **Resource group**: Select or create one
   - **Bot handle**: `teamsrecordingbot` (must be unique)
   - **Pricing tier**: F0 (Free)
   - **Type of App**: Multi Tenant
   - **Creation type**: "Use existing app registration"
   - **App ID**: `cd454696-161c-4266-9212-6a787fa58145`
   - **App tenant ID**: `b6ad3b74-02d8-4bab-a4fb-1b6607a159b9`
3. Click "Review + Create"
4. Click "Create"
5. Wait for deployment to complete

### Step 2: Enable Teams Channel
1. Go to your new Azure Bot resource
2. Click "Channels" (left menu)
3. Click the Microsoft Teams icon
4. Click "Save"

### Step 3: Configure Calling (CRITICAL)
1. In the Teams channel settings
2. Click "Calling" tab
3. Enable "Calling"
4. You'll need a public HTTPS endpoint - use ngrok:

### Step 4: Setup ngrok
```bash
# Download ngrok from https://ngrok.com/download
# Then run:
ngrok http 5000
```

Copy the HTTPS URL (like `https://abc123.ngrok-free.app`)

### Step 5: Set Bot Endpoints
1. Go to Azure Bot → Configuration
2. Set **Messaging endpoint**: `https://YOUR-NGROK-URL/api/messages`
3. Click "Apply"

4. Go to Channels → Teams → Calling tab
5. Set **Webhook (for calling)**: `https://YOUR-NGROK-URL/api/calling`
6. Click "Save"

### Step 6: Grant Permissions
1. Go to: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/CallAnAPI/appId/cd454696-161c-4266-9212-6a787fa58145
2. Click "Add a permission"
3. Select "Microsoft Graph" → "Application permissions"
4. Add:
   - Calls.JoinGroupCall.All
   - Calls.JoinGroupCallAsGuest.All
   - Calls.AccessMedia.All
   - Calls.Initiate.All
5. Click "Grant admin consent for [Your Tenant]"
6. Wait 10 minutes

### Step 7: Test
1. Keep ngrok running
2. Run: `python app.py`
3. Go to http://localhost:5000
4. Try joining a Teams call

## Why This Error Happens
Microsoft Teams requires bots to be registered in their platform store.
Simply having an App Registration is NOT enough.
You MUST create an Azure Bot Service resource.

## If You Don't Want to Do This
Use the webhook approach instead - users manually record calls and paste transcripts.
No bot infrastructure needed.
