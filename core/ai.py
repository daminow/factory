import os
from dotenv import load_dotenv
import openai
import requests
import base64
from elevenlabs.client import ElevenLabs

# Load .env
load_dotenv()

# Initialize API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
HEYGEN_TOKEN = os.getenv("HEYGEN_TOKEN")
CAPCUT_TOKEN = os.getenv("CAPCUT_TOKEN")

# Init OpenAI
openai.api_key = OPENAI_API_KEY

# Init ElevenLabs client
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Default voice and model for ElevenLabs
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
DEFAULT_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")


def gpt4o_mini(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def elevenlabs_tts(text: str, lang: str) -> bytes:
    # Generate speech with ElevenLabs
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=DEFAULT_VOICE_ID,
        model_id=DEFAULT_MODEL_ID,
        output_format="mp3_44100_128"
    )
    return audio


def whisper_transcribe(audio_bytes: bytes) -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"model": "whisper-1", "language": "auto"}
    resp = requests.post(url, headers=headers, files=files, data=data)
    resp.raise_for_status()
    return resp.json().get("text", "").strip()


def heygen_video(audio_bytes: bytes, images: list[str]) -> bytes:
    url = "https://api.heygen.com/v1/videos"
    headers = {"Authorization": f"Bearer {HEYGEN_TOKEN}"}
    files = {"audio": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"resolution": "720p"}
    for idx, img_url in enumerate(images[:3], start=1):
        data[f"image_url_{idx}"] = img_url
    resp = requests.post(url, data=data, files=files, headers=headers)
    resp.raise_for_status()
    job_id = resp.json().get("job_id")
    status_url = f"{url}/{job_id}/status"
    while True:
        status = requests.get(status_url, headers=headers).json()
        if status.get("status") == "completed":
            break
    video_url = status.get("result_url")
    resp_video = requests.get(video_url)
    resp_video.raise_for_status()
    return resp_video.content


def capcut_compose(video_bytes: bytes, captions: str) -> bytes:
    url = "https://api.capcut.com/v1/projects/compose"
    headers = {"Authorization": f"Bearer {CAPCUT_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "video_base64": base64.b64encode(video_bytes).decode(),
        "captions": captions
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    result_url = resp.json().get("result_url")
    resp_play = requests.get(result_url)
    resp_play.raise_for_status()
    return resp_play.content
```python
import os
import openai
import requests
import base64

# Initialize API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_KEY   = os.getenv("ELEVENLABS_KEY")
HEYGEN_TOKEN     = os.getenv("HEYGEN_TOKEN")
CAPCUT_TOKEN     = os.getenv("CAPCUT_TOKEN")

openai.api_key = OPENAI_API_KEY

def gpt4o_mini(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def elevenlabs_tts(text: str, lang: str) -> bytes:
    url = "https://api.elevenlabs.io/v1/text-to-speech/generic"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.75},
        "model_id": f"text_to_speech_{lang.lower()}"
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.content


def whisper_transcribe(audio_bytes: bytes) -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"model": "whisper-1", "language": "auto"}
    resp = requests.post(url, headers=headers, files=files, data=data)
    resp.raise_for_status()
    return resp.json().get("text", "").strip()


def heygen_video(audio_bytes: bytes, images: list[str]) -> bytes:
    url = "https://api.heygen.com/v1/videos"
    headers = {"Authorization": f"Bearer {HEYGEN_TOKEN}"}
    files = {"audio": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"resolution": "720p"}
    for idx, img_url in enumerate(images[:3], start=1):
        data[f"image_url_{idx}"] = img_url
    resp = requests.post(url, data=data, files=files, headers=headers)
    resp.raise_for_status()
    job_id = resp.json().get("job_id")
    status_url = f"{url}/{job_id}/status"
    while True:
        status = requests.get(status_url, headers=headers).json()
        if status.get("status") == "completed":
            break
    video_url = status.get("result_url")
    resp_video = requests.get(video_url)
    resp_video.raise_for_status()
    return resp_video.content


def capcut_compose(video_bytes: bytes, captions: str) -> bytes:
    url = "https://api.capcut.com/v1/projects/compose"
    headers = {"Authorization": f"Bearer {CAPCUT_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "video_base64": base64.b64encode(video_bytes).decode(),
        "captions": captions
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    result_url = resp.json().get("result_url")
    resp_play = requests.get(result_url)
    resp_play.raise_for_status()
    return resp_play.content
```python
import os
import openai
import requests
import base64

# Initialize API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_KEY   = os.getenv("ELEVENLABS_KEY")
HEYGEN_TOKEN     = os.getenv("HEYGEN_TOKEN")
CAPCUT_TOKEN     = os.getenv("CAPCUT_TOKEN")

openai.api_key = OPENAI_API_KEY

def gpt4o_mini(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def elevenlabs_tts(text: str, lang: str) -> bytes:
    url = "https://api.elevenlabs.io/v1/text-to-speech/generic"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.75},
        "model_id": f"text_to_speech_{lang.lower()}"
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.content


def whisper_transcribe(audio_bytes: bytes) -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"model": "whisper-1", "language": "auto"}
    resp = requests.post(url, headers=headers, files=files, data=data)
    resp.raise_for_status()
    return resp.json().get("text", "").strip()


def heygen_video(audio_bytes: bytes, images: list[str]) -> bytes:
    url = "https://api.heygen.com/v1/videos"
    headers = {"Authorization": f"Bearer {HEYGEN_TOKEN}"}
    # Upload audio and request composition
    files = {"audio": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"resolution": "720p"}
    for idx, img_url in enumerate(images[:3], start=1):
        data[f"image_url_{idx}"] = img_url
    resp = requests.post(url, data=data, files=files, headers=headers)
    resp.raise_for_status()
    job_id = resp.json().get("job_id")
    # Poll until ready
    status_url = f"{url}/{job_id}/status"
    while True:
        status = requests.get(status_url, headers=headers).json()
        if status.get("status") == "completed":
            break
    video_url = status.get("result_url")
    video_resp = requests.get(video_url)
    video_resp.raise_for_status()
    return video_resp.content


def capcut_compose(video_bytes: bytes, captions: str) -> bytes:
    url = "https://api.capcut.com/v1/projects/compose"
    headers = {"Authorization": f"Bearer {CAPCUT_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "video_base64": base64.b64encode(video_bytes).decode(),
        "captions": captions
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    result_url = resp.json().get("result_url")
    result_resp = requests.get(result_url)
    result_resp.raise_for_status()
    return result_resp.content
```python
import os
import openai
import requests
from core.config import ALLOWED_LANGS

openai.api_key = os.getenv("OPENAI_API_KEY")


def gpt4o_mini(prompt: str) -> str:
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini", messages=[{"role":"user","content":prompt}]
    )
    return resp.choices[0].message.content


def elevenlabs_tts(text: str, lang: str) -> bytes:
    # TODO: integrate ElevenLabs API
    return b"AUDIO_BYTES"


def whisper_transcribe(audio: bytes) -> str:
    # TODO: integrate Whisper API
    return "transcribed captions"


def heygen_video(audio: bytes, images: list[str]) -> bytes:
    # TODO: integrate HeyGen or Pika
    return b"VIDEO_BYTES"


def capcut_compose(video: bytes, captions: str) -> bytes:
    # TODO: integrate CapCut Creator API
    return video  # return composed video