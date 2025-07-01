# analyze_image_audio.py

import argparse
import os
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
from PIL import Image, UnidentifiedImageError
from pydub import AudioSegment

def caption_image(image_path):
    """
    Generate caption for the image at image_path
    """
    print(f"-- Generating caption for image: {image_path}")

    # Validate file existence
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file does not exist: {image_path}")
        return None

    # Load BLIP model
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    try:
        image = Image.open(image_path).convert("RGB")
    except UnidentifiedImageError:
        print(f"[ERROR] Could not recognize image format: {image_path}")
        return None
    except Exception as e:
        print(f"[ERROR] Error opening image: {e}")
        return None

    inputs = processor(images=image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    print(f"[OK] Image Caption: {caption}")
    return caption

def convert_audio(audio_path):
    """
    Convert any audio file to WAV mono 16kHz for Whisper compatibility.
    Returns path to converted audio.
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
        print(f"[ERROR] Could not process audio file {audio_path}. Error: {e}")
        return None

def transcribe_audio(audio_path):
    """
    Transcribe audio file at audio_path
    """
    print(f"-- Transcribing audio: {audio_path}")

    converted_path = convert_audio(audio_path)
    if converted_path is None:
        print("[ERROR] Skipping transcription due to audio conversion failure.")
        return None

    # Load Whisper model
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base")

    try:
        result = transcriber(converted_path, chunk_length_s=30)
        transcription = result["text"]
        print(f"[OK] Audio Transcription: {transcription}")
        return transcription
    except Exception as e:
        print(f"[ERROR] Error during audio transcription: {e}")
        return None

def summarize_text(text):
    """
    Summarize the provided text
    """
    print("-- Summarizing combined text...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    try:
        summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
        summary_text = summary[0]["summary_text"]
        print(f"[OK] Summary: {summary_text}")
        return summary_text
    except Exception as e:
        print(f"[ERROR] Error during summarization: {e}")
        return None

def main(image_path, audio_path, summarize=False):
    print("========== IMAGE AND AUDIO ANALYZER ==========")

    # Process image
    caption = caption_image(image_path)

    # Process audio
    transcription = transcribe_audio(audio_path)

    if caption is None and transcription is None:
        print("[ERROR] No outputs to combine. Exiting.")
        return

    combined_text = f"Image description: {caption}. Audio transcription: {transcription}"
    print("\nCombined Text:\n", combined_text)

    if summarize:
        summary = summarize_text(combined_text)
        if summary:
            print("\nFinal Summary:\n", summary)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze image and audio files of any format.")
    parser.add_argument("--image", required=True, help="Path to image file (e.g. .jpg, .png, .webp, etc.)")
    parser.add_argument("--audio", required=True, help="Path to audio file (e.g. .mp3, .wav, .m4a, etc.)")
    parser.add_argument("--summarize", action="store_true", help="Enable summarization of results")

    args = parser.parse_args()

    main(args.image, args.audio, args.summarize)
