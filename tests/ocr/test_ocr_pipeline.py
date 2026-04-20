from pathlib import Path

import pytest
from PIL import Image

from src.ocr.ocr_pipeline import run_ocr, run_batch_ocr


class _DummyOCR:
    def ocr(self, _image_path: str):
        return [
            [
                [[[0, 0], [10, 0], [10, 10], [0, 10]], ("RSA 2048", 0.99)],
                [[[0, 12], [10, 12], [10, 22], [0, 22]], ("TLS 1.2", 0.98)],
            ]
        ]


def _make_test_image(tmp_path: Path) -> Path:
    image_path = tmp_path / "test.png"
    Image.new("RGB", (16, 16), color="white").save(image_path)
    return image_path


def test_run_ocr_returns_shape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    test_img = _make_test_image(tmp_path)
    monkeypatch.setattr("src.ocr.ocr_pipeline._get_ocr_engine", lambda: _DummyOCR())

    result = run_ocr(test_img, image_id="img-test", page=1)

    assert "raw_text" in result
    assert "normalized_text" in result
    assert "confidence" in result
    assert "tokens" in result
    assert "image_id" in result
    assert "page" in result
    assert result["image_id"] == "img-test"
    assert result["page"] == 1
    assert isinstance(result["fields"], list)
    assert result["raw_text"]


def test_run_ocr_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        run_ocr(Path("nonexistent.png"))


def test_run_ocr_wrong_type() -> None:
    with pytest.raises(TypeError):
        run_ocr("not_a_path")  # type: ignore[arg-type]


def test_run_batch_ocr_with_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    test_img = _make_test_image(tmp_path)
    monkeypatch.setattr("src.ocr.ocr_pipeline._get_ocr_engine", lambda: _DummyOCR())

    results = run_batch_ocr([test_img])
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["image_id"] == "img-0001"
    assert results[0]["page"] == 1


def test_run_batch_ocr_with_dicts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    test_img = _make_test_image(tmp_path)
    monkeypatch.setattr("src.ocr.ocr_pipeline._get_ocr_engine", lambda: _DummyOCR())

    items = [{"path": str(test_img), "image_id": "img-0001", "page": 3}]
    results = run_batch_ocr(items)
    assert len(results) == 1
    assert results[0]["image_id"] == "img-0001"
    assert results[0]["page"] == 3
