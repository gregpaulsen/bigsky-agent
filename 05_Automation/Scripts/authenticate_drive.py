from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying scopes, delete your existing token.json file
SCOPES = ['https://www.googleapis.com/auth/drive.file']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)

creds = flow.run_local_server(port=0)

# Save the credentials for future use
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print("✅ Google Drive authentication complete. Token saved as token.json")

