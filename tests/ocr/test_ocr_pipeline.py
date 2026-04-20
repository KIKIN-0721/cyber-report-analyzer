from pathlib import Path

try:
    import pytest
except Exception:  # pragma: no cover
    pytest = None  # type: ignore

from src.ocr.ocr_pipeline import run_ocr, run_batch_ocr


def _skip_if_no_image(test_img: Path) -> None:
    if not test_img.exists():
        if pytest is not None:
            pytest.skip("test.png not found")
        else:
            raise AssertionError("test.png not found")


def test_run_ocr_returns_shape() -> None:
    test_img = Path("../../code/test.png")
    _skip_if_no_image(test_img)

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


def test_run_ocr_missing_file() -> None:
    try:
        run_ocr(Path("nonexistent.png"))
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_run_ocr_wrong_type() -> None:
    try:
        run_ocr("not_a_path")  # type: ignore[arg-type]
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_run_batch_ocr_with_paths() -> None:
    test_img = Path("../../code/test.png")
    _skip_if_no_image(test_img)

    results = run_batch_ocr([test_img])
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["image_id"] == "img-0001"
    assert results[0]["page"] == 1


def test_run_batch_ocr_with_dicts() -> None:
    test_img = Path("../../code/test.png")
    _skip_if_no_image(test_img)

    items = [{"path": str(test_img), "image_id": "img-0001", "page": 3}]
    results = run_batch_ocr(items)
    assert len(results) == 1
    assert results[0]["image_id"] == "img-0001"
    assert results[0]["page"] == 3
