"""Contract tests for the OpenAI vision adapter (mocked transport)."""

import json

import httpx
import pytest

from app.providers.base import DiagnosisRequest
from app.providers.vision.openai_like import OpenAIVisionProvider

PNG_1PX = bytes.fromhex(
    "89504e470d0a1a0a0000000d494844520000000100000001080600000"
    "01f15c4890000000d49444154789c626001000000ffff030000060005"
    "57bfabd40000000049454e44ae426082"
)


def _provider(content: str | Exception, status_code: int = 200) -> OpenAIVisionProvider:
    def handler(request: httpx.Request) -> httpx.Response:
        if isinstance(content, Exception):
            raise content
        auth = request.headers.get("Authorization", "")
        assert auth.startswith("Bearer ")
        body = json.loads(request.content.decode())
        assert body["messages"][1]["content"][1]["image_url"]["url"].startswith("data:image/")
        return httpx.Response(
            status_code,
            json={"choices": [{"message": {"content": content}}]},
        )

    return OpenAIVisionProvider("k", transport=httpx.MockTransport(handler))


def _req(**kw) -> DiagnosisRequest:
    return DiagnosisRequest(crop_key="tomato", image_bytes=PNG_1PX, **kw)


@pytest.mark.asyncio
async def test_good_json_parsed_with_alternatives():
    answer = json.dumps(
        {
            "disease_key": "Early Blight",
            "confidence": 0.87,
            "alternatives": [
                {"disease_key": "late_blight", "confidence": 0.10},
                {"disease_key": "Early Blight", "confidence": 0.9},
            ],
            "is_healthy": False,
        }
    )
    result = await _provider(answer).diagnose(_req())
    assert result.status == "completed"
    assert result.prediction is not None
    assert result.prediction.disease_key == "early_blight"
    assert result.prediction.confidence == 0.87
    assert result.prediction.alternatives == [{"disease_key": "late_blight", "confidence": 0.10}]
    assert result.prediction.model_version == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_null_key_maps_to_unusable_completed():
    answer = json.dumps({"disease_key": None, "confidence": 0.2, "alternatives": []})
    result = await _provider(answer).diagnose(_req())
    assert result.status == "completed"
    assert result.prediction is not None
    assert result.prediction.disease_key is None


@pytest.mark.asyncio
async def test_non_json_answer_is_failed_not_crash():
    result = await _provider("I think it's leaf curl!!").diagnose(_req())
    assert result.status == "failed"
    assert result.error_message == "provider returned non-JSON answer"


@pytest.mark.asyncio
async def test_http_error_is_failed():
    result = await _provider(httpx.ConnectError("offline")).diagnose(_req())
    assert result.status == "failed"


@pytest.mark.asyncio
async def test_confidence_clamped():
    answer = json.dumps({"disease_key": "rust", "confidence": 4.2, "alternatives": []})
    result = await _provider(answer).diagnose(_req())
    assert result.prediction is not None
    assert result.prediction.confidence == 1.0


@pytest.mark.asyncio
async def test_crop_key_in_prompt():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"choices": [{"message": {"content": "{}"}}]})

    p = OpenAIVisionProvider("k", transport=httpx.MockTransport(handler))
    await p.diagnose(_req())
    assert "tomato" in seen["body"]["messages"][1]["content"][0]["text"]
