import base64
from functools import lru_cache
from pathlib import Path

import httpx

from src.config.settings import Settings, get_settings
from src.models.dto import ImageAnalysisResult


class BailianVisionAnalyzer:
    """Vision analyzer using Aliyun Bailian Qwen-VL via OpenAI-compatible chat API."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.api_key = self.settings.vision_api_key or self.settings.llm_api_key
        self.base_url = (self.settings.vision_base_url or self.settings.llm_base_url).rstrip("/")
        self.model = self.settings.vision_model

    def _encode_image(self, image_path: str) -> str:
        with Path(image_path).open("rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    async def analyze(self, image_path: str) -> ImageAnalysisResult:
        if not self.api_key:
            raise ValueError("VISION_API_KEY or LLM_API_KEY is not configured")

        b64_image = self._encode_image(image_path)
        mime = (
            "image/jpeg"
            if image_path.lower().endswith((".jpg", ".jpeg"))
            else "image/png"
        )
        data_url = f"data:{mime};base64,{b64_image}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                        {
                            "type": "text",
                            "text": (
                                "请详细分析这张图片，输出 JSON 格式：\n"
                                "{"
                                '"caption": "简短描述", '
                                '"dense_caption": "详细描述", '
                                '"objects": ["物体1", "物体2"], '
                                '"scene": ["场景1"], '
                                '"actions": ["动作1"], '
                                '"emotion": ["情感1"], '
                                '"context": ["上下文1"], '
                                '"ocr_text": "图片中的文字，如果没有则为空", '
                                '"ocr_blocks": []'
                                "}"
                            ),
                        },
                    ],
                }
            ],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]

        # Parse JSON from content
        raw = content.strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]

        import json

        result = json.loads(raw.strip())
        return ImageAnalysisResult(
            caption=result.get("caption", ""),
            dense_caption=result.get("dense_caption", ""),
            objects=result.get("objects", []),
            scene=result.get("scene", []),
            actions=result.get("actions", []),
            emotion=result.get("emotion", []),
            context=result.get("context", []),
            ocr_text=result.get("ocr_text", ""),
            ocr_blocks=result.get("ocr_blocks", []),
            raw_analysis=result,
        )


# Compatibility alias
QwenVLImageAnalyzer = BailianVisionAnalyzer


@lru_cache
def get_vision_analyzer() -> BailianVisionAnalyzer:
    return BailianVisionAnalyzer()
