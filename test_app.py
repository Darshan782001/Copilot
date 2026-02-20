import requests
import json

BASE_URL = 'http://localhost:5000'

# Test 1: Health check
response = requests.get(f'{BASE_URL}/health')
print('Health Check:', response.json())

# Test 2: Summarize text
test_data = {
    'text': 'This is a sample meeting transcript. We discussed the project timeline and agreed on deliverables. The team will focus on implementing the new features by next week. Budget approval is pending from management.'
}
response = requests.post(f'{BASE_URL}/summarize', json=test_data)
print('Summary:', response.json())

# Test 3: Teams webhook simulation
teams_data = {
    'meeting_id': 'MEET-12345',
    'transcript': 'Meeting started at 10 AM. Discussed Q4 goals, budget allocation, and team expansion. Action items: Submit proposal by Friday, schedule follow-up meeting.',
    'participants': ['John Doe', 'Jane Smith', 'Bob Johnson'],
    'recipient_email': 'recipient@example.com'
}
response = requests.post(f'{BASE_URL}/webhook/teams', json=teams_data)
print('Teams Webhook:', response.json())
