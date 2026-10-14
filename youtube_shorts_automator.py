import os
import requests
import json
import subprocess
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

# --- CONFIGURATION & API KEYS ---
# Replace these with your actual API keys or set them as environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "YOUR_PEXELS_API_KEY")

# YouTube API settings
YOUTUBE_CLIENT_SECRETS_FILE = "client_secret.json" # Downloaded from Google Cloud Console
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def generate_script_and_keywords(prompt):
    """Generates a short script and a search keyword using Gemini API."""
    print("[1/5] Generating script with Gemini API...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    system_instruction = (
        "You are an automated YouTube Shorts script writer. Respond strictly in valid JSON format. "
        "Do not include markdown blocks like ```json ... ```. Just raw JSON. "
        "Format: {\"script\": \"A concise narration text less than 150 words\", \"keyword\": \"one single specific search term for stock video\", \"title\": \"Catchy title\"}"
    )
    
    data = {
        "contents": [{"parts": [{"text": f"Create a short video script about: {prompt}"}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    result_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    return json.loads(result_text)

def generate_voiceover(text, output_audio="voiceover.mp3"):
    """Uses a free public/alternative gTTS or an accessible TTS method to create audio."""
    print("[2/5] Generating text-to-speech voiceover...")
    # Using an alternative lightweight approach for the pipeline template
    # (In production, replace with Google Cloud TTS or ElevenLabs)
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en')
        tts.save(output_audio)
    except ImportError:
        # Fallback using standard system or quick API alternative if package missing
        print("Install 'gtts' via pip for local text-to-speech generation.")
        raise Exception("gTTS package not found.")
    return output_audio

def fetch_stock_video(keyword, output_video="stock_video.mp4"):
    """Fetches a relevant vertical video from Pexels API."""
    print(f"[3/5] Fetching vertical stock video for keyword: '{keyword}'...")
    url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=5&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    videos = response.json().get("videos", [])
    if not videos:
        raise Exception(f"No videos found on Pexels for keyword: {keyword}")
        
    # Get the link to the highest quality progressive MP4 file available
    video_files = videos[0]["video_files"]
    mp4_files = [f for f in video_files if f["file_type"] == "video/mp4"]
    download_url = mp4_files[0]["link"]
    
    print("Downloading video asset...")
    video_data = requests.get(download_url).content
    with open(output_video, 'wb') as f:
        f.write(video_data)
    return output_video

def edit_and_render_video(video_path, audio_path, output_path="final_shorts.mp4"):
    """Uses FFmpeg to combine video and audio, trimming the video to fit the audio length."""
    print("[4/5] Running FFmpeg to stitch video and audio together...")
    
    # FFmpeg command: loops/cuts video to match audio length, adds video/audio streams together
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path
    ]
    
    # Execute the FFmpeg sub-process
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr.decode('utf-8')}")
    print(f"Video compiled successfully: {output_path}")
    return output_path

def upload_to_youtube(video_path, metadata):
    """Uploads the final video to YouTube via Data API v3."""
    print("[5/5] Authenticating and uploading video to YouTube...")
    
    flow = InstalledAppFlow.from_client_secrets_file(YOUTUBE_CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    youtube = build('youtube', 'v3', credentials=credentials)
    
    body = {
        'snippet': {
            'title': metadata['title'][:100],
            'description': f"{metadata['script']}\n\n#shorts #ai #automation",
            'tags': [metadata['keyword'], 'shorts', 'aiautomation'],
            'categoryId': '22' # People & Blogs
        },
        'status': {
            'privacyStatus': 'private', # Kept private for review safety
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
            
    print(f"Successfully uploaded! Video ID: {response['id']}")
    return response['id']

def run_pipeline(topic_prompt):
    try:
        # Step 1: AI Ideation
        meta = generate_script_and_keywords(topic_prompt)
        
        # Step 2: Voiceover Generation
        audio = generate_voiceover(meta['script'])
        
        # Step 3: Stock Assets
        video_asset = fetch_stock_video(meta['keyword'])
        
        # Step 4: FFmpeg Editing
        final_video = edit_and_render_video(video_asset, audio)
        
        # Step 5: Auto-Publish
        upload_to_youtube(final_video, meta)
        
        print("\nPipeline execution completed successfully!")
        
    except Exception as e:
        print(f"\nPipeline failed: {e}")

if __name__ == "__main__":
    # Test topic for the automated automation script
    run_pipeline("Top 3 mind-blowing space facts")
