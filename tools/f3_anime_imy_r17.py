"""Experimental ANIME000.IDT stream decoder. No texture exports or writes."""
from collections import Counter
import struct


def records(blob):
    if len(blob) < 16 or any(blob[4:16]):
        raise ValueError('Invalid IDT header')
    count = struct.unpack_from('<I', blob)[0]
    if not 0 < count <= 10000:
        raise ValueError('Invalid record count')
    pos = 16
    result = []
    for _ in range(count):
        if pos + 4 > len(blob):
            raise ValueError('Truncated record size')
        size = struct.unpack_from('<I', blob, pos)[0]
        if size < 60 or size % 4 or pos + size > len(blob):
            raise ValueError('Invalid record extent')
        result.append((pos, pos + size))
        pos += size
    if pos != len(blob):
        raise ValueError('Unaccounted IDT tail')
    return result


def decode_bounded(blob, start, limit, *, unit, literal_unit=None, row_half=False):
    """Candidate only. Return decoded bytes in memory, consumed offset and flag count."""
    if literal_unit is None:
        literal_unit = unit
    if unit not in (2, 4) or literal_unit not in (2, 4):
        raise ValueError('Invalid unit')
    if not 0 <= start < limit <= len(blob) or start + 34 > limit or blob[start:start+4] != b'IMY\0':
        raise ValueError('Invalid IMY extent')
    target_plus, stride, kind, _, rows = struct.unpack_from('<IHBBH', blob, start + 4)
    target = stride * rows
    count = struct.unpack_from('<H', blob, start + 32)[0]
    base = start + 34 + count
    if kind not in (0, 2) or not 0 < target <= 4 * 1024 * 1024 or target_plus != target + 32 or target % unit or not count or base > limit:
        raise ValueError('Invalid geometry or flags')
    row = stride // 2 if row_half else stride
    distances = (unit, row, row + unit, row - unit)
    rp = base
    out = bytearray()
    flags = blob[start+34:base]
    used = 0
    for fl in flags:
        if len(out) == target:
            break
        used += 1
        if fl >= 192:
            distance = distances[(fl >> 4) & 3]
            if distance < unit or distance > len(out):
                raise ValueError('Invalid output lookback')
            for _ in range((fl & 15) + 1):
                ix = len(out) - distance
                out.extend(out[ix:ix+unit])
        elif fl >= 16:
            distance = (fl - 15) * literal_unit
            if rp - distance < base:
                raise ValueError('Invalid literal lookback')
            token = blob[rp-distance:rp-distance+literal_unit]
            out.extend(token * (unit // literal_unit) if unit >= literal_unit else token[:unit])
        else:
            n = (fl + 1) * literal_unit
            if rp + n > limit:
                raise ValueError('Literal crosses boundary')
            for ix in range(rp, rp+n, literal_unit):
                token = blob[ix:ix+literal_unit]
                out.extend(token * (unit // literal_unit) if unit >= literal_unit else token[:unit])
            rp += n
        if len(out) > target:
            raise ValueError('Decoded size overflow')
    if len(out) != target or any(flags[used:]):
        raise ValueError('Wrong decoded size or nonzero unused flags')
    if any(blob[rp:limit]):
        raise ValueError('Nonzero bytes beyond stream')
    return bytes(out), rp, used


def analyze(blob):
    ranges = records(blob)
    types = Counter()
    per_record = Counter()
    tail = {0: Counter(), 2: Counter()}
    half_literal_rejected = 0
    half_stride_diff = 0
    half_stride_invalid = 0
    for lo, hi in ranges:
        offsets = []
        pos = lo
        while (pos := blob.find(b'IMY\0', pos, hi)) >= 0:
            offsets.append(pos)
            pos += 4
        per_record[len(offsets)] += 1
        for pos, limit in zip(offsets, offsets[1:] + [hi]):
            if pos + 34 > limit:
                raise ValueError('Truncated IMY header in record')
            kind = blob[pos+10]
            if kind not in (0, 2):
                raise ValueError('Unknown ANIME IMY kind')
            unit = 2 if kind == 0 else 4
            decoded, consumed, _ = decode_bounded(blob, pos, limit, unit=unit)
            types[kind] += 1
            tail[kind][limit-consumed] += 1
            if kind == 2:
                try:
                    decode_bounded(blob, pos, limit, unit=4, literal_unit=2)
                except ValueError:
                    half_literal_rejected += 1
                try:
                    other, _, _ = decode_bounded(blob, pos, limit, unit=4, row_half=True)
                    half_stride_diff += other != decoded
                except ValueError:
                    half_stride_invalid += 1
    return {'record_count':len(ranges), 'bytes_accounted':len(blob),
            'headers_per_record':dict(sorted(per_record.items())),
            'types_pass_bounded_candidate':dict(sorted(types.items())),
            'zero_tail_bytes_histogram':{k:dict(sorted(v.items())) for k,v in tail.items()},
            'type2_half_literal_rejected':half_literal_rejected,
            'type2_half_stride_different_output':half_stride_diff,
            'type2_half_stride_invalid':half_stride_invalid,
            'runtime_or_visual_proven':False, 'repacking_authorized':False}
