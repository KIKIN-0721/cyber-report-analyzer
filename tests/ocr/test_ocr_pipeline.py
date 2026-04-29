from pathlib import Path

import pytest
from PIL import Image

from src.ocr.ocr_pipeline import build_ocr_image_items, run_ocr, run_batch_ocr, run_ocr_for_parse_result


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

    items = [
        {
            "path": str(test_img),
            "image_id": "img-0001",
            "page": 3,
            "section_id": "1.2",
            "paragraph_id": "1.2-P04",
            "input_type": "pdf",
        }
    ]
    results = run_batch_ocr(items)
    assert len(results) == 1
    assert results[0]["image_id"] == "img-0001"
    assert results[0]["page"] == 3
    assert results[0]["source_type"] == "image_ocr"
    assert results[0]["section_id"] == "1.2"
    assert results[0]["paragraph_id"] == "1.2-P04"


def test_build_ocr_image_items_supports_parse_result_v2() -> None:
    parse_result = {
        "input_type": "word",
        "images": [
            {
                "image_id": "img-x",
                "path": "tmp/image.png",
                "page": 5,
                "section_id": "2",
                "paragraph_id": "2-P01",
            }
        ],
    }

    items = build_ocr_image_items(parse_result)

    assert items == [
        {
            "path": "tmp/image.png",
            "image_id": "img-x",
            "page": 5,
            "section_id": "2",
            "paragraph_id": "2-P01",
            "input_type": "word",
        }
    ]


def test_run_ocr_for_parse_result_returns_structured_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    test_img = _make_test_image(tmp_path)
    monkeypatch.setattr("src.ocr.ocr_pipeline._get_ocr_engine", lambda: _DummyOCR())
    parse_result = {
        "schema_version": "2.1",
        "input_type": "pdf",
        "images": [
            {
                "image_id": "img-0007",
                "path": str(test_img),
                "page": 7,
                "section_id": "3",
                "paragraph_id": "3-P02",
            }
        ],
    }

    payload = run_ocr_for_parse_result(parse_result)

    assert payload["schema_version"] == "2.1"
    fields = payload["structured_fields"]
    assert len(fields) == 2
    assert fields[0]["source_type"] == "image_ocr"
    assert fields[0]["input_type"] == "pdf"
    assert fields[0]["page"] == 7
    assert fields[0]["section_id"] == "3"
    assert fields[0]["paragraph_id"] == "3-P02"
    assert fields[0]["source_ref"] == "img-0007"
