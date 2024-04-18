import os
import random
from pyrogram import Client, filters
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import asyncio

# Google Drive configuration
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 't.json'  # Replace with your service account file
DRIVE_FOLDER_ID = '1Cr62BFmkpRKy1ykewjirX2Q1bQfQlFs8'  # Replace with your Google Drive folder ID

# Function to authenticate with Google Drive
def authenticate():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

# Function to upload file to Google Drive
async def upload_to_drive(file_path, message, app):
    try:
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [DRIVE_FOLDER_ID]
        }

        media_body = MediaFileUpload(file_path, chunksize=1024*1024, resumable=True)

        request = service.files().create(body=file_metadata, media_body=media_body)
        response = None

        # Upload progress
        progress_message = await message.reply_text("Uploading file...")

        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 10)
                progress_bar = "🔵" * progress + "⚪" * (10 - progress)
                await progress_message.edit_text(f"Uploading file... \n{progress_bar}")
        
        file_link = f"https://drive.google.com/uc?export=download&id={response.get('id')}"
        await progress_message.edit_text(f"File uploaded successfully!\n\nLink: `{file_link}`")

        # Delete file after upload
        os.remove(file_path)
    except Exception as e:
        print(f"Error uploading file: {e}")

# Create a Pyrogram client
app = Client("my_bot", api_id=28662850, api_hash="b1d399223315796334cc3c80770e7108", bot_token="6498988097:AAEWg7_-ooUb1eykeGTxRQXfQOX4PIHkb3k")

# Define the download and upload handler function
@app.on_message(filters.document | filters.video | filters.audio | filters.photo)
async def handle_file(client, message):
    # Check if the message has a file
    if message.media:
        try:
            # Generate a random filename
            random_filename = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6)) + ".mp4"
            # Download media
            file_path = await client.download_media(message, file_name=random_filename)

            # Upload file to Google Drive
            await upload_to_drive(file_path, message, app)

            # Example: Print confirmation message
            print(f"File '{file_path}' uploaded to Google Drive")
        except Exception as e:
            print(f"Error handling file: {e}")

if __name__ == "__main__":
    try:
        print("Bot running 💨")
        app.run()
    except Exception as e:
        print(f"Error starting bot: {e}")
