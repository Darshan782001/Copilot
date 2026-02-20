from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv('TEAMS_CLIENT_ID')
APP_PASSWORD = os.getenv('TEAMS_CLIENT_SECRET')

settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(settings)

class TeamsBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            await turn_context.send_activity(f"Echo: {turn_context.activity.text}")
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            await turn_context.send_activity("Bot joined the call")

bot = TeamsBot()

async def messages(req):
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    
    async def call_func(turn_context):
        await bot.on_turn(turn_context)
    
    await adapter.process_activity(activity, auth_header, call_func)
    return {"status": "ok"}
