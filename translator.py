import deepl
import requests


class DeepLTranslator:
    def __init__(self, api_key: str):
        self._t = deepl.Translator(api_key) if api_key else None

    def translate(self, text: str) -> str:
        if not self._t:
            raise ValueError("DeepL API Key 未设置")
        result = self._t.translate_text(text, target_lang="ZH")
        return result.text


class OllamaTranslator:
    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model

    def translate(self, text: str) -> str:
        prompt = f"请将以下文本翻译成中文，只输出译文，不要解释：\n{text}"
        resp = requests.post(
            f"{self.host}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()


def create_translator(cfg: dict):
    """根据配置创建翻译器"""
    if cfg.get("backend") == "ollama":
        return OllamaTranslator(
            cfg.get("ollama_host", "http://localhost:11434"),
            cfg.get("ollama_model", "qwen2.5:7b"),
        )
    return DeepLTranslator(cfg.get("deepl_api_key", ""))
