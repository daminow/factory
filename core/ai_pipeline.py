from typing import Tuple, List
from core.scraper import scrape_product
from core.ai import gpt4o_mini, elevenlabs_tts, heygen_video, whisper_transcribe, capcut_compose


def generate_video_pipeline(url: str, lang: str = "RU") -> Tuple[bytes, str, List[str]]:
    product = scrape_product(url)
    # Prompt на английском, контент на русском допускается через lang
    prompt = (
        "You are a direct-response ad copywriter. Write a concise video script in the target language.\n"
        f"Target language: {lang}.\n"
        f"Product title: {product['title']}.\n"
        "Structure: Hook, Problem, Solution (product), 3-5 key benefits, Call-To-Action."
    )
    script = gpt4o_mini(prompt)
    audio = elevenlabs_tts(script, lang)
    video_raw = heygen_video(audio, product["images"])
    captions = whisper_transcribe(audio)
    video_final = capcut_compose(video_raw, captions)
    return video_final, captions, product["images"]

