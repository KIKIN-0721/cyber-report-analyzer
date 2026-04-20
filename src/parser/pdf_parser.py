from __future__ import annotations

import base64
import argparse
import json
import re
import zlib
from pathlib import Path
from typing import Dict, List


STREAM_OBJECT_RE = re.compile(
    rb"(?s)(\d+)\s+(\d+)\s+obj\s*(<<.*?>>)\s*stream\r?\n(.*?)\r?\nendstream\s*endobj"
)
TEXT_SECTION_RE = re.compile(rb"BT(.*?)ET", re.DOTALL)


def extract_text_and_images(pdf_path: Path) -> Dict[str, List[str]]:
    """Extract text blocks and image files from one PDF.

    S1 目标不是完整 PDF 引擎，而是实现“单个原生 PDF 的最小可运行链路”：
    - 提取可直接读取的文本流
    - 提取图片对象并写成独立文件，供后续 OCR 使用
    """
    if not isinstance(pdf_path, Path):
        raise TypeError("pdf_path must be a pathlib.Path")
    if not pdf_path.exists():
        raise FileNotFoundError(f"pdf not found: {pdf_path}")
    if not pdf_path.is_file():
        raise ValueError(f"pdf_path must be a file: {pdf_path}")

    pdf_bytes = pdf_path.read_bytes()
    text_blocks = _extract_text_blocks(pdf_bytes)
    image_paths = _extract_images(pdf_bytes, pdf_path)
    return {"text_blocks": text_blocks, "image_paths": image_paths}


def _extract_text_blocks(pdf_bytes: bytes) -> List[str]:
    text_blocks: List[str] = []

    for stream in _iter_stream_objects(pdf_bytes):
        if _is_image_stream(stream["dictionary"]):
            continue

        decoded_stream = _decode_stream(stream["dictionary"], stream["stream"])
        if decoded_stream is None:
            continue

        for section in TEXT_SECTION_RE.findall(decoded_stream):
            strings = _collect_pdf_strings(section)
            block = "\n".join(part for part in strings if part.strip()).strip()
            if block:
                text_blocks.append(block)

    return text_blocks


def _extract_images(pdf_bytes: bytes, pdf_path: Path) -> List[str]:
    image_paths: List[str] = []
    output_dir: Path | None = None

    for index, stream in enumerate(_iter_stream_objects(pdf_bytes), start=1):
        dictionary = stream["dictionary"]
        if not _is_image_stream(dictionary):
            continue

        image_data = _build_image_file(dictionary, stream["stream"])
        if image_data is None:
            continue

        if output_dir is None:
            output_dir = pdf_path.parent / "tmp" / f"{pdf_path.stem}_images"
            output_dir.mkdir(parents=True, exist_ok=True)

        extension, binary = image_data
        object_id = stream["object_id"]
        image_path = output_dir / f"image_{index:03d}_obj_{object_id}.{extension}"
        image_path.write_bytes(binary)
        image_paths.append(str(image_path))

    return image_paths


def _iter_stream_objects(pdf_bytes: bytes) -> List[Dict[str, bytes | str]]:
    objects: List[Dict[str, bytes | str]] = []
    for match in STREAM_OBJECT_RE.finditer(pdf_bytes):
        objects.append(
            {
                "object_id": match.group(1).decode("ascii", errors="ignore"),
                "dictionary": match.group(3),
                "stream": match.group(4),
            }
        )
    return objects


def _is_image_stream(dictionary: bytes) -> bool:
    subtype = _extract_name_value(dictionary, b"Subtype")
    return subtype == "Image"


def _decode_stream(dictionary: bytes, raw_stream: bytes) -> bytes | None:
    filters = _extract_filter_names(dictionary)
    try:
        return _apply_filters(raw_stream, filters)
    except Exception:
        return None


def _build_image_file(dictionary: bytes, raw_stream: bytes) -> tuple[str, bytes] | None:
    filters = _extract_filter_names(dictionary)

    if "DCTDecode" in filters:
        return ("jpg", raw_stream)
    if "JPXDecode" in filters:
        return ("jp2", raw_stream)

    try:
        decoded = _apply_filters(raw_stream, filters)
    except Exception:
        return None

    width = _extract_int_value(dictionary, b"Width")
    height = _extract_int_value(dictionary, b"Height")
    bits = _extract_int_value(dictionary, b"BitsPerComponent")
    color_space = _extract_name_value(dictionary, b"ColorSpace")

    if not width or not height or bits != 8:
        return None

    if color_space == "DeviceGray":
        if len(decoded) < width * height:
            return None
        header = f"P5\n{width} {height}\n255\n".encode("ascii")
        return ("pgm", header + decoded[: width * height])

    if color_space == "DeviceRGB":
        expected = width * height * 3
        if len(decoded) < expected:
            return None
        header = f"P6\n{width} {height}\n255\n".encode("ascii")
        return ("ppm", header + decoded[:expected])

    return None


def _apply_filters(data: bytes, filters: List[str]) -> bytes:
    current = data
    for name in filters:
        if name == "FlateDecode":
            current = zlib.decompress(current)
        elif name == "ASCIIHexDecode":
            current = _decode_ascii_hex(current)
        elif name == "ASCII85Decode":
            current = _decode_ascii85(current)
        elif name in {"DCTDecode", "JPXDecode"}:
            # 图片原始编码交由调用方处理
            current = current
        else:
            raise ValueError(f"unsupported filter: {name}")
    return current


def _extract_filter_names(dictionary: bytes) -> List[str]:
    array_match = re.search(rb"/Filter\s*\[(.*?)\]", dictionary, re.DOTALL)
    if array_match:
        return [
            item.decode("ascii", errors="ignore")
            for item in re.findall(rb"/([A-Za-z0-9]+)", array_match.group(1))
        ]

    single_match = re.search(rb"/Filter\s*/([A-Za-z0-9]+)", dictionary)
    if single_match:
        return [single_match.group(1).decode("ascii", errors="ignore")]

    return []


def _extract_name_value(dictionary: bytes, key: bytes) -> str | None:
    match = re.search(rb"/" + re.escape(key) + rb"\s*/([A-Za-z0-9]+)", dictionary)
    if not match:
        return None
    return match.group(1).decode("ascii", errors="ignore")


def _extract_int_value(dictionary: bytes, key: bytes) -> int | None:
    match = re.search(rb"/" + re.escape(key) + rb"\s+(\d+)", dictionary)
    if not match:
        return None
    return int(match.group(1))


def _collect_pdf_strings(section: bytes) -> List[str]:
    values: List[str] = []
    index = 0

    while index < len(section):
        byte = section[index]

        if byte == 0x28:  # (
            literal, index = _parse_literal_string(section, index)
            decoded = _decode_pdf_literal(literal)
            if decoded.strip():
                values.append(decoded)
            continue

        if byte == 0x3C and index + 1 < len(section) and section[index + 1] != 0x3C:
            hex_string, index = _parse_hex_string(section, index)
            decoded = _decode_hex_string(hex_string)
            if decoded.strip():
                values.append(decoded)
            continue

        index += 1

    return values


def _parse_literal_string(data: bytes, start_index: int) -> tuple[bytes, int]:
    depth = 0
    result = bytearray()
    index = start_index

    while index < len(data):
        byte = data[index]

        if byte == 0x28 and (index == start_index or data[index - 1] != 0x5C):
            depth += 1
            if depth > 1:
                result.append(byte)
        elif byte == 0x29 and data[index - 1] != 0x5C:
            depth -= 1
            if depth == 0:
                return bytes(result), index + 1
            result.append(byte)
        else:
            result.append(byte)

        index += 1

    return bytes(result), len(data)


def _parse_hex_string(data: bytes, start_index: int) -> tuple[bytes, int]:
    end_index = data.find(b">", start_index + 1)
    if end_index == -1:
        return b"", len(data)
    return data[start_index + 1 : end_index], end_index + 1


def _decode_pdf_literal(raw: bytes) -> str:
    result = bytearray()
    index = 0

    while index < len(raw):
        byte = raw[index]

        if byte != 0x5C:  # backslash
            result.append(byte)
            index += 1
            continue

        index += 1
        if index >= len(raw):
            break

        escaped = raw[index]
        escape_map = {
            ord(b"n"): b"\n",
            ord(b"r"): b"\r",
            ord(b"t"): b"\t",
            ord(b"b"): b"\b",
            ord(b"f"): b"\f",
            ord(b"("): b"(",
            ord(b")"): b")",
            ord(b"\\"): b"\\",
        }

        if escaped in escape_map:
            result.extend(escape_map[escaped])
            index += 1
            continue

        if 48 <= escaped <= 55:
            octal_digits = bytearray([escaped])
            index += 1
            for _ in range(2):
                if index < len(raw) and 48 <= raw[index] <= 55:
                    octal_digits.append(raw[index])
                    index += 1
                else:
                    break
            result.append(int(octal_digits.decode("ascii"), 8))
            continue

        result.append(escaped)
        index += 1

    return result.decode("utf-8", errors="ignore")


def _decode_hex_string(raw: bytes) -> str:
    hex_text = re.sub(rb"\s+", b"", raw)
    if len(hex_text) % 2 == 1:
        hex_text += b"0"
    try:
        return bytes.fromhex(hex_text.decode("ascii")).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _decode_ascii_hex(data: bytes) -> bytes:
    cleaned = re.sub(rb"\s+", b"", data).rstrip(b">")
    if len(cleaned) % 2 == 1:
        cleaned += b"0"
    return bytes.fromhex(cleaned.decode("ascii"))


def _decode_ascii85(data: bytes) -> bytes:
    cleaned = data.strip()
    if cleaned.startswith(b"<~") and cleaned.endswith(b"~>"):
        return base64.a85decode(cleaned, adobe=True)
    return base64.a85decode(cleaned)


def _build_cli_payload(pdf_path: Path) -> Dict[str, object]:
    exists = pdf_path.exists()
    is_file = pdf_path.is_file() if exists else False
    if exists and is_file:
        result = extract_text_and_images(pdf_path)
        text_blocks = result.get("text_blocks", [])
        image_paths = result.get("image_paths", [])
        size_bytes = pdf_path.stat().st_size
    else:
        text_blocks = []
        image_paths = []
        size_bytes = None
    return {
        "input_pdf": str(pdf_path),
        "file_name": pdf_path.name,
        "exists": exists,
        "is_file": is_file,
        "size_bytes": size_bytes,
        "parser_text_block_count": len(text_blocks),
        "image_count": len(image_paths),
        "parser_text_blocks_full": text_blocks,
        "image_paths": image_paths,
    }


def _main() -> None:
    parser = argparse.ArgumentParser(description="Parse one PDF with the S1 parser MVP.")
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    payload = _build_cli_payload(args.pdf_path)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    _main()
