import os
import json
import subprocess
import requests
from pydub import AudioSegment
from PIL import Image, UnidentifiedImageError
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline


##########################################
# Download Audio from YouTube
##########################################

def download_youtube_audio(youtube_url, output_path="podcast.mp3"):
    """
    Download audio from a YouTube URL using yt-dlp.
    """
    command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", output_path,
        youtube_url
    ]
    try:
        subprocess.run(command, check=True)
        print(f"[OK] Downloaded YouTube audio: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] yt-dlp failed: {e}")
        return None


##########################################
# URL Downloader for Images / Audio
##########################################

def download_file(url, target_path, expected_content_types):
    """
    Download a file from a URL if it matches an expected content type.
    """
    try:
        head = requests.head(url, allow_redirects=True, timeout=5)
        content_type = head.headers.get("Content-Type", "").lower()

        if not any(ct in content_type for ct in expected_content_types):
            print(f"[WARNING] Skipping download: Content-Type {content_type} does not match {expected_content_types}")
            return None

        response = requests.get(url, stream=True, timeout=10)
        if response.status_code != 200:
            print(f"[ERROR] Failed to download: HTTP {response.status_code}")
            return None

        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] Downloaded {target_path}")
        return target_path

    except Exception as e:
        print(f"[ERROR] Could not download from {url}. Error: {e}")
        return None


##########################################
# Image Captioning
##########################################

def caption_image(image_path):
    """
    Generate caption for the image at image_path
    """
    print(f"-- Generating caption for image: {image_path}")

    if not os.path.exists(image_path):
        print(f"[ERROR] Image file does not exist: {image_path}")
        return None

    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    try:
        image = Image.open(image_path).convert("RGB")
    except UnidentifiedImageError:
        print(f"[ERROR] Unrecognized image format: {image_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Error opening image: {e}")
        return None

    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    print(f"[OK] Image Caption: {caption}")
    return caption


##########################################
# Audio Conversion + Transcription
##########################################

def convert_audio(audio_path):
    """
    Convert any audio file to WAV mono 16kHz for Whisper compatibility.
    """
    converted_path = "converted.wav"

    if not os.path.exists(audio_path):
        print(f"[ERROR] Audio file does not exist: {audio_path}")
        return None

    ext = os.path.splitext(audio_path)[-1].lower()

    try:
        print("-- Converting audio to WAV, mono, 16kHz...")
        audio = AudioSegment.from_file(audio_path, format=ext[1:] if ext else None)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio.export(converted_path, format="wav")
        print(f"[OK] Audio converted: {converted_path}")
        return converted_path
    except Exception as e:
        print(f"[ERROR] Could not convert audio file. Error: {e}")
        return None


def transcribe_audio(audio_path):
    """
    Transcribe audio file using Whisper.
    """
    print(f"-- Transcribing audio: {audio_path}")
    converted_path = convert_audio(audio_path)
    if converted_path is None:
        print("[ERROR] Skipping transcription.")
        return None

    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base")

    try:
        result = transcriber(converted_path, chunk_length_s=30)
        transcription = result["text"]
        print(f"[OK] Audio Transcription: {transcription}")
        return transcription
    except Exception as e:
        print(f"[ERROR] Error during transcription: {e}")
        return None


##########################################
# Ad Removal using Ollama LLM
##########################################

def remove_ads_with_ollama(transcript, model_name="llama3"):
    """
    Use the LLM to remove advertisements from a transcript.
    """
    print("-- Sending transcript to Ollama for ad removal...")
    url = "http://localhost:11434/api/generate"
    prompt = f"""
Remove all advertisement, sponsorship, and promotional content from the following podcast transcript. 
Return ONLY the spoken content unrelated to advertising, preserving the original discussion and context:

{transcript}
"""

    payload = {
        "model": model_name,
        "prompt": prompt
    }

    try:
        response = requests.post(url, json=payload, timeout=120, stream=True)
        cleaned_chunks = []
        for line in response.iter_lines():
            if line:
                json_data = json.loads(line.decode("utf-8"))
                chunk_text = json_data.get("response", "")
                cleaned_chunks.append(chunk_text)

        cleaned_transcript = "".join(cleaned_chunks)
        print(f"[OK] Transcript with ads removed:\n{cleaned_transcript}")
        return cleaned_transcript
    except Exception as e:
        print(f"[ERROR] Ollama ad removal failed: {e}")
        return transcript  # fallback: return original transcript if LLM fails


##########################################
# Summarization via Ollama
##########################################

def summarize_with_ollama(text, model_name="llama3"):
    """
    Summarize text using local Ollama LLM.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": f"""Summarize the following satirical podcast transcript into concise bullet points. 
Exclude any advertisement or promotional content. Focus only on the core discussions and key points:

{text}
"""
    }

    try:
        response = requests.post(url, json=payload, timeout=120, stream=True)
        summary_chunks = []
        for line in response.iter_lines():
            if line:
                json_data = json.loads(line.decode("utf-8"))
                chunk_text = json_data.get("response", "")
                summary_chunks.append(chunk_text)

        summary = "".join(summary_chunks)
        print(f"[OK] Summary from Ollama:\n{summary}")
        return summary
    except Exception as e:
        print(f"[ERROR] Ollama summarization failed: {e}")
        return None


##########################################
# Main Processing Pipeline
##########################################

def analyze_media(
    image_url=None,
    youtube_url=None,
    audio_url=None
):
    print("========== STARTING MEDIA ANALYSIS ==========")

    # IMAGE PROCESSING
    caption = None
    if image_url:
        downloaded_image = download_file(
            url=image_url,
            target_path="downloaded_image.jpg",
            expected_content_types=["image/"]
        )
        if downloaded_image:
            caption = caption_image(downloaded_image)

    # AUDIO PROCESSING (via YouTube OR direct link)
    transcription = None
    audio_file = None

    if youtube_url:
        audio_file = download_youtube_audio(youtube_url, output_path="podcast.mp3")
    elif audio_url:
        audio_file = download_file(
            url=audio_url,
            target_path="downloaded_audio.mp3",
            expected_content_types=["audio/"]
        )

    if audio_file:
        raw_transcript = transcribe_audio(audio_file)
        if raw_transcript:
            cleaned_transcript = remove_ads_with_ollama(raw_transcript)
            transcription = cleaned_transcript

    # COMBINE RESULTS
    if caption is None and transcription is None:
        print("[ERROR] Nothing to process.")
        return

    combined_text = f"Image caption: {caption}\nPodcast transcript: {transcription}"
    print("\nCombined Text:\n", combined_text)

    # Summarize with Ollama
    summary = summarize_with_ollama(combined_text)
    print("\n==== FINAL SUMMARY ====\n", summary)
    return summary


##########################################
# Example Usage
##########################################

if __name__ == "__main__":
    analyze_media(
        image_url="https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
        youtube_url="https://www.youtube.com/watch?v=bMou1qUMHC4&t"
    )
