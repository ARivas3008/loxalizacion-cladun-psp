#!/usr/bin/env python3
"""IMY PSP codec for safe text-container re-encoding (never images by default).

Conserves the original block geometry, extending only the final text block.
Every result is decoded with the independent extraction decoder.
"""
from __future__ import annotations
import struct

from extract_cladun import decompress


def require(value, message):
    if not value:
        raise ValueError(message)


def u16(blob, off):
    return struct.unpack_from("<H", blob, off)[0]


def u32(blob, off):
    return struct.unpack_from("<I", blob, off)[0]


def compress_block(raw: bytes, header: bytes) -> bytes:
    """Encode IMY word references; preserve first 32 bytes of PSP block header."""
    require(header[:4] == b"IMY\x00", "Invalid IMY header")
    stride, rows = u16(header, 8), u16(header, 12)
    require(len(raw) == stride * rows and len(raw) % 2 == 0, "IMY block geometry mismatch")
    count = len(raw) // 2
    gaps = (2, stride, stride + 2, stride - 2)
    require(all(x > 0 and x % 2 == 0 for x in gaps), "Unsupported IMY stride")
    matches = []
    for gap in gaps:
        distance = gap // 2
        values = [0] * (count + 17)
        for i in range(count - 1, distance - 1, -1):
            if raw[2 * i:2 * i + 2] == raw[2 * (i - distance):2 * (i - distance) + 2]:
                values[i] = min(16, values[i + 1] + 1)
        matches.append(values)

    flags, literals, pending, recent = bytearray(), bytearray(), bytearray(), {}

    def flush():
        nonlocal pending
        for at in range(0, len(pending), 32):
            piece = pending[at:at + 32]
            flags.append(len(piece) // 2 - 1)
            old = len(literals)
            literals.extend(piece)
            for index in range(0, len(piece), 2):
                recent[bytes(piece[index:index + 2])] = old + index
        pending = bytearray()

    i = 0
    while i < count:
        size, kind = 0, -1
        for candidate in range(4):
            if matches[candidate][i] > size:
                size, kind = matches[candidate][i], candidate
        if size:
            if pending:
                flush()
            flags.append(0xC0 + (kind << 4) + size - 1)
            i += size
            continue
        word = raw[2 * i:2 * i + 2]
        previous = recent.get(word)
        if previous is not None:
            delta = len(literals) + len(pending) - previous
            if 2 <= delta <= 352 and delta % 2 == 0:
                if pending:
                    flush()
                flags.append(0x10 + (delta - 2) // 2)
                i += 1
                continue
        pending.extend(word)
        i += 1
        if len(pending) == 32:
            flush()
    if pending:
        flush()
    require(len(flags) <= 65535, "IMY flags exceed 16-bit size")
    return header[:32] + struct.pack("<H", len(flags)) + flags + literals


def recompress(original_stored: bytes, new_decoded: bytes) -> bytes:
    """Recompress same number of IMY chunks, resizing the last chunk only."""
    require(len(original_stored) >= 32, "Compressed resource too small")
    blocks = u32(original_stored, 0)
    require(1 <= blocks <= 512, "Unsupported number of IMY blocks")
    offsets = struct.unpack_from("<" + "I" * blocks, original_stored, 8)
    require(list(offsets) == sorted(offsets) and offsets[0] >= 8 + 4 * blocks,
            "Invalid IMY directory")
    headers = [original_stored[off:off + 32] for off in offsets]
    require(all(len(h) == 32 and h[:4] == b"IMY\x00" for h in headers),
            "Unrecognized IMY chunk header")
    earlier = sum(u16(h, 8) * u16(h, 12) for h in headers[:-1])
    last = bytearray(headers[-1])
    stride = u16(last, 8)
    remaining = len(new_decoded) - earlier
    require(stride >= 2 and stride % 2 == 0 and remaining > 0 and remaining % (stride * 2) == 0,
            "Invalid final IMY block size")
    new_rows = remaining // stride
    require(new_rows <= 1024, "Final IMY block would exceed observed format")
    struct.pack_into("<H", last, 12, new_rows)
    # PSP IMY encodes 0x20 header bytes and rowcount/2 in the same dword.
    struct.pack_into("<I", last, 4, 0x20 | ((new_rows // 2) << 8))
    headers[-1] = bytes(last)

    result = bytearray(struct.pack("<II", blocks, len(new_decoded)) + b"\0" * (4 * blocks))
    cursor = 0
    for index, header in enumerate(headers):
        length = u16(header, 8) * u16(header, 12)
        chunk = compress_block(new_decoded[cursor:cursor + length], header)
        result.extend(b"\0" * (-len(result) % 4))
        struct.pack_into("<I", result, 8 + index * 4, len(result))
        result.extend(chunk)
        cursor += length
    require(cursor == len(new_decoded), "IMY final size mismatch")
    decoded, codec = decompress(bytes(result), len(new_decoded))
    require(codec.startswith("IMY") and decoded == new_decoded, "IMY independent roundtrip FAILED")
    return bytes(result)
