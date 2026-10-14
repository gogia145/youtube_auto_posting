# Automated YouTube Shorts Pipeline (100% Free Stack)

This repository contains a fully automated script to generate, edit, and publish YouTube Shorts using free AI models and public media APIs.

## 🛠️ The Architecture
1. **Scripting:** Google Gemini 1.5 Flash API (Highly generous free tier)
2. **Voiceover:** `gTTS` library (Free Google Text-to-Speech wrapper)
3. **Visuals:** Pexels API (Free vertical stock video clips matching the topic)
4. **Editing:** FFmpeg (Open-source CLI tool to merge audio, loop video, and export)
5. **Publishing:** YouTube Data API v3 (Free developer platform tokens)

## 🗂️ Project Directory Structure
```text
youtube-shorts-automator/
│
├── youtube_shorts_automator.py   # Main pipeline execution script
├── requirements.txt              # Required python dependencies
├── client_secret.json            # Your YouTube OAuth credentials 
└── README.md                     # Setup instructions
```

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.8+** and **FFmpeg** installed on your system.
* **Mac:** `brew install ffmpeg`
* **Windows:** Download from the official website and add it to your system PATH.

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Obtain API Keys & Credentials
1. **Gemini API Key:** Get it from [Google AI Studio](https://aistudio.google.com/).
2. **Pexels API Key:** Sign up and grab a free key from the [Pexels Developer Portal](https://www.pexels.com/api/).
3. **YouTube OAuth JSON:** 
   * Go to the [Google Cloud Console](https://console.cloud.google.com/).
   * Create a new project, enable the **YouTube Data API v3**.
   * Go to **Credentials**, create an **OAuth 2.0 Client ID** (Desktop Application), download the JSON file, and rename it to `client_secret.json` in this root folder.

### 4. Run the Pipeline
Set your keys in your terminal environment variables and execute the automation:
```bash
export GEMINI_API_KEY="your_gemini_key_here"
export PEXELS_API_KEY="your_pexels_key_here"

python youtube_shorts_automator.py
```
