import os
import time
import base64
from typing import List
from gtts import gTTS
from io import BytesIO
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, ColorClip
import tempfile
import requests
from tenacity import retry, wait_exponential, stop_after_attempt


def gpt4o_mini(prompt: str) -> str:
    # Простая синтезация скрипта: расширяем prompt формализованным шаблоном
    return (
        f"Вступление: кратко представь товар.\n"
        f"Проблема: что болит у клиента.\n"
        f"Решение: как товар решает проблему.\n"
        f"Детали: 3-5 ключевых преимуществ.\n"
        f"Призыв: переходи по ссылке в описании.\n\n"
        f"Контекст: {prompt[:300]}"
    )


@retry(wait=wait_exponential(multiplier=0.5, min=1, max=8), stop=stop_after_attempt(3))
def elevenlabs_tts(text: str, lang: str) -> bytes:
    # Если есть ключ ElevenLabs — используем, иначе fallback на gTTS
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    if api_key:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        payload = {"text": text, "model_id": model_id}
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.content
    # gTTS fallback
    lang_map = {"RU": "ru", "KZ": "ru", "UZ": "ru", "EN": "en"}
    voice_lang = lang_map.get(lang.upper(), "ru")
    buf = BytesIO()
    gTTS(text=text, lang=voice_lang).write_to_fp(buf)
    return buf.getvalue()


def whisper_transcribe(audio_bytes: bytes) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"file": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"model": "whisper-1", "language": "ru"}
    try:
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
        resp.raise_for_status()
        return resp.json().get("text", "").strip() or ""
    except Exception:
        return ""


def heygen_video(audio_bytes: bytes, images: List[str]) -> bytes:
    # Если есть HEYGEN_TOKEN — пробуем удалённую генерацию, иначе локально
    heygen_token = os.getenv("HEYGEN_TOKEN")
    if heygen_token:
        base = "https://api.heygen.com/v1/videos"
        headers = {"Authorization": f"Bearer {heygen_token}"}
        files = {"audio": ("audio.mp3", audio_bytes, "audio/mpeg")}
        data = {"resolution": "720p"}
        for idx, img_url in enumerate(images[:3], start=1):
            data[f"image_url_{idx}"] = img_url
        try:
            resp = requests.post(base, data=data, files=files, headers=headers, timeout=60)
            resp.raise_for_status()
            job_id = resp.json().get("job_id")
            if not job_id:
                raise RuntimeError("HeyGen: no job_id")
            status_url = f"{base}/{job_id}/status"
            deadline = time.time() + 240
            while time.time() < deadline:
                st_resp = requests.get(status_url, headers=headers, timeout=30)
                st_resp.raise_for_status()
                st = st_resp.json()
                if st.get("status") == "completed" and st.get("result_url"):
                    video_url = st.get("result_url")
                    # allow only http(s) to public endpoints
                    if not video_url.startswith("http"):
                        raise RuntimeError("HeyGen invalid result_url")
                    video_resp = requests.get(video_url, timeout=120)
                    video_resp.raise_for_status()
                    return video_resp.content
                if st.get("status") in {"failed", "canceled"}:
                    raise RuntimeError(f"HeyGen {st.get('status')}")
                time.sleep(2)
        except Exception:
            # Fallback to local assembly below
            pass

    # Локальная сборка: слайд-шоу из изображений под длительность аудио
    audio_path = None
    temp_paths: List[str] = []
    clips = []
    video = None
    audio_clip = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as a:
            a.write(audio_bytes)
            audio_path = a.name
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration or float(os.getenv("VIDEO_DURATION_DEFAULT", 15))
        num_images = max(1, len(images))
        per_image = max(2, duration / num_images)

        # Скачиваем картинки в темп-файлы
        for url in images[:10]:
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as imgf:
                    imgf.write(resp.content)
                    temp_paths.append(imgf.name)
            except Exception:
                continue

        if temp_paths:
            for p in temp_paths:
                clip = ImageClip(p).set_duration(per_image).resize(newsize=(720, 1280))
                clips.append(clip)
        else:
            clips.append(ColorClip(size=(720, 1280), color=(0, 0, 0)).set_duration(duration))

        video = concatenate_videoclips(clips, method="compose").set_audio(audio_clip)
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as v:
            fps = int(os.getenv("VIDEO_FPS", 24))
            video.write_videofile(v.name, fps=fps, codec="libx264", audio_codec="aac")
            with open(v.name, "rb") as f:
                out = f.read()
        return out
    finally:
        # Чистка ресурсов
        try:
            if video is not None:
                video.close()
        except Exception:
            pass
        if audio_clip is not None:
            try:
                audio_clip.close()
            except Exception:
                pass
        for c in clips:
            try:
                c.close()
            except Exception:
                pass
        for p in temp_paths:
            try:
                os.remove(p)
            except Exception:
                pass
        if audio_path:
            try:
                os.remove(audio_path)
            except Exception:
                pass


def capcut_compose(video_bytes: bytes, captions: str) -> bytes:
    token = os.getenv("CAPCUT_TOKEN")
    if not token:
        return video_bytes
    url = "https://api.capcut.com/v1/projects/compose"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"video_base64": base64.b64encode(video_bytes).decode(), "captions": captions}
    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    result_url = resp.json().get("result_url")
    if not result_url:
        return video_bytes
    out = requests.get(result_url, timeout=120)
    out.raise_for_status()
    return out.content

