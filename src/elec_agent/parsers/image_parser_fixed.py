# ⚡ elec-agent — Vision LLM Parser
# Takes a schematic image → returns structured component list via vision LLM

import base64
import json
import re
from pathlib import Path
import pdfplumber
from PIL import Image
import io


# Human-readable prompt for the vision LLM
EXTRACTION_PROMPT = """
You are an expert in industrial and commercial electrical systems (NF C 15-100 standard).
Analyze this electrical schematic (single-line or multi-line diagram) and extract ALL visible components.

Return ONLY valid JSON (no text before or after) with this structure:
{
  "components": [
    {
      "id": "CB1",
      "type": "circuit_breaker",
      "rating_A": 16,
      "poles": 2,
      "curve": "C",
      "position": "main_board",
      "downstream_load": "office_outlets",
      "cable_section_mm2": 2.5,
      "cable_length_m": 15,
      "load_power_W": 3000
    }
  ]
}

Valid component types:
- circuit_breaker (thermal-magnetic breaker)
- differential (differential switch)
- rcd (differential breaker)
- fuse
- contactor
- cable
- motor
- socket (outlet)
- lighting
- main_switch
- busbar
- transformer
- other

If a value is unreadable or missing, use null.
Be exhaustive — list every component you see.
"""


class ImageParser:
    """
    Vision LLM parser for electrical schematics.

    Supports:
        - Image files (PNG, JPG, JPEG)
        - PDF scans (extracts first page as image)
        - LLM providers: Ollama (local), OpenAI, Anthropic
    """

    def __init__(self, llm_config: dict):
        """
        Initialize parser with LLM configuration.

        Args:
            llm_config: Dict with keys:
                - provider: "ollama" | "openai" | "anthropic"
                - model: model name (e.g., "llama3.2-vision", "gpt-4.1")
                - api_key: required for OpenAI/Anthropic
        """
        self.provider = llm_config.get("provider", "ollama")
        self.model    = llm_config.get("model", "llama3.2-vision")
        self.api_key  = llm_config.get("api_key")

    def parse(self, path: Path) -> list[dict]:
        """
        Main parsing method.

        Args:
            path: Path to schematic file (image or PDF)

        Returns:
            List of extracted component dictionaries
        """
        image_bytes = self._load_image(path)
        raw = self._call_llm(image_bytes)
        return self._parse_response(raw)

    def _load_image(self, path: Path) -> bytes:
        """
        Load image from file (PNG/JPG) or extract from PDF.

        Args:
            path: File path

        Returns:
            Image bytes as PNG
        """
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            # Extract first page from PDF as image
            with pdfplumber.open(path) as pdf:
                page = pdf.pages[0]
                img = page.to_image(resolution=200).original
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return buf.getvalue()
        else:
            # Load image file directly
            img = Image.open(path).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()

    def _call_llm(self, image_bytes: bytes) -> str:
        """
        Call vision LLM with image and prompt.

        Args:
            image_bytes: Image as PNG bytes

        Returns:
            Raw LLM response (JSON string)
        """
        if self.provider == "ollama":
            return self._call_ollama(image_bytes)
        elif self.provider == "openai":
            return self._call_openai(image_bytes)
        elif self.provider == "anthropic":
            return self._call_anthropic(image_bytes)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _call_ollama(self, image_bytes: bytes) -> str:
        """
        Call Ollama local server (free, no API key).

        Requires:
            - Ollama installed: https://ollama.com
            - Model pulled: ollama pull llama3.2-vision
        """
        import ollama
        b64 = base64.b64encode(image_bytes).decode()
        response = ollama.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT,
                "images": [b64],
            }]
        )
        return response["message"]["content"]

    def _call_openai(self, image_bytes: bytes) -> str:
        """
        Call OpenAI API (GPT-4 with vision).

        Requires:
            - API key from: https://platform.openai.com
        """
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        b64 = base64.b64encode(image_bytes).decode()
        response = client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": EXTRACTION_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            }],
            max_tokens=2000,
        )
        return response.choices[0].message.content

    def _call_anthropic(self, image_bytes: bytes) -> str:
        """
        Call Anthropic API (Claude with vision).

        Requires:
            - API key from: https://console.anthropic.com
        """
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        b64 = base64.b64encode(image_bytes).decode()
        response = client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64}},
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }]
        )
        return response.content[0].text

    def _parse_response(self, raw: str) -> list[dict]:
        """
        Extract JSON from raw LLM response.

        Args:
            raw: Raw LLM output (may include text before/after JSON)

        Returns:
            List of components from JSON
        """
        # Find JSON object in response (LLM may add chatter)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return valid JSON.
Raw output:
{raw}")

        data = json.loads(match.group())
        return data.get("components", [])
