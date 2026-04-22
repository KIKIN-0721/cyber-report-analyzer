from __future__ import annotations

import base64
import re
import zlib
from pathlib import Path

import pytest

from src.parser.pdf_parser import extract_text_and_images


ONE_BY_ONE_JPEG_BASE64 = (
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAQEBUQEBAVFRUVFRUVFRUVFRUVFRUVFRUWFhUV"
    "FRUYHSggGBolHRUVITEhJSkrLi4uFx8zODMsNygtLisBCgoKDg0OGxAQGi0lHyUtLS0tLS0tLS0t"
    "LS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAAEAAgMBIgACEQEDEQH/"
    "xAAbAAABBQEBAAAAAAAAAAAAAAAFAQIDBAYAB//EADQQAAEDAgQDBgUEAwAAAAAAAAEAAgMEEQUS"
    "ITFBBhMiUWFxgZGhFDJCscHR8BVCYnKCorL/xAAaAQEBAQEBAQEAAAAAAAAAAAAAAQIDBAUG/8QAJh"
    "EBAQEAAgICAgMBAAAAAAAAAAECEQMhEjEEQVEiMmEFcYGRof/aAAwDAQACEQMRAD8A9wREQEREBERA"
    "REQEREBERAREQf/Z"
)


def test_extract_text_and_images_requires_path_instance() -> None:
    with pytest.raises(TypeError):
        extract_text_and_images("sample.pdf")  # type: ignore[arg-type]


def test_extract_text_and_images_raises_for_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_text_and_images(tmp_path / "missing.pdf")


def test_extract_text_and_images_extracts_flate_text_blocks(tmp_path: Path) -> None:
    content_stream = b"BT\n/F1 12 Tf\n72 720 Td\n(Hello S1 MVP) Tj\n(TLS 1.2 Enabled) Tj\nET"
    pdf_bytes = _build_pdf_with_text_stream(zlib.compress(content_stream), flate=True)
    pdf_path = tmp_path / "text-only.pdf"
    pdf_path.write_bytes(pdf_bytes)

    result = extract_text_and_images(pdf_path)

    assert result["image_paths"] == []
    assert result["text_blocks"] == ["Hello S1 MVP\nTLS 1.2 Enabled"]


def test_extract_text_and_images_exports_embedded_jpeg(tmp_path: Path) -> None:
    jpeg_bytes = base64.b64decode(ONE_BY_ONE_JPEG_BASE64)
    pdf_bytes = _build_pdf_with_image_stream(jpeg_bytes)
    pdf_path = tmp_path / "image-only.pdf"
    pdf_path.write_bytes(pdf_bytes)

    result = extract_text_and_images(pdf_path)

    assert result["text_blocks"] == []
    assert len(result["image_paths"]) == 1

    exported_image = Path(result["image_paths"][0])
    assert exported_image.exists()
    assert exported_image.suffix.lower() == ".jpg"
    assert exported_image.read_bytes() == jpeg_bytes


def test_extract_text_and_images_real_pdf_has_chinese_text() -> None:
    real_pdf = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "网络空间安全基地+南昌大学学工一体化平台垂直越权+攻击报告.pdf"
    )
    if not real_pdf.exists():
        pytest.skip("real PDF fixture not found")

    result = extract_text_and_images(real_pdf)
    joined_text = "\n".join(result["text_blocks"])
    assert re.search(r"[\u4e00-\u9fff]", joined_text)


def _build_pdf_with_text_stream(stream_bytes: bytes, *, flate: bool) -> bytes:
    dictionary = f"<< /Length {len(stream_bytes)}".encode("ascii")
    if flate:
        dictionary += b" /Filter /FlateDecode"
    dictionary += b" >>"

    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        + dictionary
        + b"\nstream\n"
        + stream_bytes
        + b"\nendstream\nendobj\n%%EOF\n"
    )


def _build_pdf_with_image_stream(jpeg_bytes: bytes) -> bytes:
    dictionary = (
        b"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 "
        b"/ColorSpace /DeviceRGB /BitsPerComponent 8 "
        b"/Filter /DCTDecode /Length "
        + str(len(jpeg_bytes)).encode("ascii")
        + b" >>"
    )

    return (
        b"%PDF-1.4\n"
        b"2 0 obj\n"
        + dictionary
        + b"\nstream\n"
        + jpeg_bytes
        + b"\nendstream\nendobj\n%%EOF\n"
    )
