from enum import Enum


class Scoring(float, Enum):
    AGREEMENT_HIT_BONUS = 1.0  # 70% of models agree, and model was in that 70%
    AGREEMENT_MISS_PENALTY = -0.5  # 70% of models agree, but model was in the 30%
    HALLUCINATION_PENALTY = -1.0  # Tag not in master pool (invalid)


IMAGES_CAPTIONS = {
    "images/image1.jpg": "Mui..♡",
    "images/image2.jpg": "🩶⌨️🎧💿",
    "images/image3.jpg": "Alternative elf",
    "images/image4.jpg": "💫",
    "images/image5.jpg": "Fashion inspo - crochet maxi skirt",
    "images/image6.jpg": "death by thrifting",
}

MODEL_LIST = [
    "google/gemini-3-pro-preview",
    "google/gemini-3-flash-preview",
    "google/gemini-2.5-pro",
    "anthropic/claude-sonnet-4.5",
    "anthropic/claude-opus-4.5",
    "x-ai/grok-4",
    "openai/gpt-5",
    "openai/gpt-5.2",
    "openai/o4-mini-high",
    "deepseek/deepseek-v3.2",
    "deepseek/deepseek-chat-v3-0324",
]
