#!/usr/bin/env python3
"""Spanish *insertion-only* labels for Cladun's fixed-size database fields.

The full-length literary draft remains untouched. These are compact technical
labels for fixed 14/16/20/... byte slots, not dialogue boxes. No arbitrary
truncation, no automatic machine summaries. Fails closed on unknown labels.

Two damaged-at-source labels are explicitly isolated by ID and raw SHA-bound
byte sequences, not silently 'restored' as though the original were complete.
"""
from __future__ import annotations

from collections import Counter
import re
from charset_es import encode_spanish

# One-to-one manual semantic adaptation of names/effects/environment labels.
EXACT = {
    "Skill Rise 2": "Mejora hab. 2",
    "Hiking Gear": "Equipo de marcha",
    "Fighter Garb": "Traje de lucha",
    "Hunter Garb": "Traje de caza",
    "Lapis Mail": "Cota de lapisl.",
    "地球姫": "Princesa Tierra",
    "闘志不要": "Sin bravura",
    "英知不要": "Sin ingenio",
    "羽の軽さ": "Pluma ligera",
    "DEFアップ": "DEF aumenta",
    "SPDアップ": "VEL aumenta",
    "剣防ぎ": "Bloq. espada",
    "槍防ぎ": "Bloq. lanza",
    "斧防ぎ": "Bloq. hacha",
    "炎防ぎ": "Prot. fuego",
    "氷防ぎ": "Prot. hielo",
    "心防ぎ": "Prot. mente",
    "闘志ボーナス5　速度-10": "Bravura +5 VEL -10",
    "闘志守護英知ボーナス2　ALL耐性-10": "Brav/Guard/Sab +2 RES -10",
    "魔力の胎動": "Pulso arcano",
    "ATK+10　速度+10　ALL耐性-50": "ATK+10 VEL+10 RES-50",
    "風斬り": "Tajo viento",
    "鬼封じ": "Sello oni",
    "ATK+5　クリティカル＆ブレイク発生+10": "ATK+5 CRIT/RUP +10",
    "Delay Burn": "Retardo fuego",
    "Delay Cool": "Retardo hielo",
    "S) W Slash": "S) Tajo doble W",
    "Dungeon Mastery": "Dom. mazmorra",
    "Novice Monster Area": "Zona de monstruos novatos",
    "炎出るブロック低": "Bloque de fuego bajo",
    "炎出るブロック高": "Bloque de fuego alto",
    "氷出るブロック低": "Bloque de hielo bajo",
    "氷出るブロック高": "Bloque de hielo alto",
    "炎出るブロック": "Bloq. fuego",
    "氷出るブロック": "Bloq. hielo",
    "宝箱　復活する": "Cofre reaparece",
    "宝箱　フラグ効果": "Efecto de cofre",
    "宝箱　だめ": "Cofre inactivo",
    "宝箱　いい": "Cofre válido",
    "宝箱　レア": "Cofre raro",
    "デスナイト": "Cab. de muerte",
    "ラガーマン": "Rugbista",
    "マッスルボンバー": "Bomb. muscular",
    "ラガー(練習用)": "Rugby (prác.)",
    "セルフ(練習用)": "Self (prác.)",
    "ペイン(練習用)": "Pain (prác.)",
    "プラス(練習用)": "Plus (prác.)",
    "コクオ(練習用)": "Kokuo (prác.)",
    "ラオウ(練習用)": "Raoh (prác.)",
    "(拠点用）通行可": "Base: acceso",
    "(拠点用）通禁止": "Base: sin paso",
    "(拠点用）おそい": "Base: lento",
    "迷宮カベ": "Muro laberinto",
    "砂漠カベ": "Muro desierto",
    "荒野レンガ": "Ladr. yermo",
    "城かべ": "Muro castillo",
    "城はしら": "Pilar castillo",
    "研究所かべ": "Muro laborat.",
    "不気味カベ": "Muro siniestro",
    "豪華絨毯面": "Suelo alfombra",
    "迷宮地面": "Suelo laberinto",
    "砂漠地面": "Suelo desierto",
    "城絨毯": "Tapiz castillo",
    "研究所床": "Suelo laborat.",
    "不気味ゆか": "Suelo siniestro",
    "OP木A外-A": "OP árbol ext A",
    "OP木A外-B": "OP árbol ext B",
    "OP壁下A": "OP muro bajo A",
    "OP壁下B": "OP muro bajo B",
    "OP石畳左A": "OP losas izq A",
    "OP石畳右A": "OP losas der A",
    "OP石畳左B": "OP losas izq B",
    "OPくさ薄い": "OP hierba clara",
    "OPくさ薄薄": "OP hierba fina",
    "OP木（緑一色）": "OP árbol verde",
    "光（通常）": "Luz normal",
    "噴水2-32": "Fuente 2-32",
    "噴水3-64": "Fuente 3-64",
    "噴水4-96": "Fuente 4-96",
    "ピヨ小 普通": "Piyo peq normal",
    "ピヨ小 知性": "Piyo peq. sabio",
    "ピヨ小 やかまし": "Piyo peq. ruido",
    "ワープゾーン": "Teletransporte",
    "ワープ出口": "Salida portal",
    "左いす2": "Silla izq. 2",
    "右いす": "Silla derecha",
    "トイレかべ": "Muro aseo",
    "カウンタ皿1": "Plato mostr. 1",
    "カウンタ皿2": "Plato mostr. 2",
    "商店テーブル": "Mesa tienda",
    "大木(左上": "Árbol sup izq",
    "転移の扉": "Puerta portal",
    "通信の扉": "Puerta enlace",
    "左の木の目": "Veta izq.",
    "ルート設定(下)": "Ruta: abajo",
    "ルート設定(左)": "Ruta: izq.",
    "ルート設定(右)": "Ruta: der.",
    "ルート設定(上)": "Ruta: arriba",
    "ルート設定(直線": "Ruta: recta",
    "普通階段(ランダ": "Escalera normal",
    "博打階段(ランダ": "Escalera azar",
    "天使階段(ランダ": "Escalera ángel",
    "悪魔階段(ランダ": "Escalera diablo",
    "地獄階段(ランダ": "Escalera inf.",
    "Monster Den": "Nido monstruos",
}

NUMBERED = (
    (r"ワープゾーン(\d+)", "Portal {}"),
    (r"ワープ出口(\d+)", "Salida p. {}"),
    (r"炎硬い壁　(\d+)", "Muro ígneo {}"),
    (r"草の壁(\d+)", "Muro hierba {}"),
    (r"板壁(\d+)", "Muro madera {}"),
    (r"恐怖壁(\d+)", "Muro terror {}"),
    (r"サイバー壁(\d+)", "Muro cíber {}"),
    (r"石壁(\d+)", "Muro piedra {}"),
    (r"炎の床　(\d+)", "Suelo fuego {}"),
    (r"土地面　(\d+)", "Suelo tierra {}"),
    (r"タイル地面　(\d+)", "Suelo losa {}"),
    (r"つた地面　(\d+)", "Suelo hiedra {}"),
    (r"氷地面　(\d+)", "Suelo hielo {}"),
    (r"怪しい地面　(\d+)", "Suelo raro {}"),
    (r"石畳地面　(\d+)", "Suelo losas {}"),
    (r"壊れる壁　(\d+)", "Muro romp. {}"),
    (r"壊れる炎壁　(\d+)", "M. fuego rot. {}"),
)

# Explicit byte-level source rescue; decoded originals are truncated by the
# original game's own 16-byte fixed-size fields. This is provisional semantics.
INCOMPLETE_RAW = {
    "008723": ("83498343838B81698341836A838196", "Aceite animado"),
    "008724": ("908581698341836A8381974C82E881", "Agua animada"),
}

# A few original Japanese labels occur in both a 32-byte monster record and
# a 16-byte upgrade-monster record; the second requires an even shorter form.
TIGHTER = {
    "炎出るブロック低": "Bloq. fuego b.",
    "炎出るブロック高": "Bloq. fuego a.",
    "氷出るブロック低": "Bloq. hielo b.",
    "氷出るブロック高": "Bloq. hielo a.",
}

def compact_text(original: str) -> str | None:
    if original in EXACT:
        return EXACT[original]
    for pattern, fmt in NUMBERED:
        match = re.fullmatch(pattern, original)
        if match:
            return fmt.format(match.group(1))
    return None


def is_fixed(row):
    return row["origen"].startswith("DATABASE.DAT/") and row["origen"] != "DATABASE.DAT/STRTBL.DAT"


def effective(row: dict, translated: dict) -> tuple[str, str]:
    """Return text for binary insertion and reason; never mutate the draft."""
    value = translated["espanol"]
    if not is_fixed(row):
        return value, "original_draft"
    if row["grupo_id"] in INCOMPLETE_RAW:
        raw, replacement = INCOMPLETE_RAW[row["grupo_id"]]
        if (row["bytes_hex"].upper() != raw or
                row["estado"] != "requiere_reconstruccion" or
                int(row["capacidad_campo"]) != 16 or len(bytes.fromhex(raw)) != 15 or
                value):
            raise ValueError("Inconsistent incomplete field at " + row["grupo_id"])
        value, why = replacement, "original_truncado_verificado_por_bytes"
    elif value and len(encode_spanish(value)) + 1 > int(row["capacidad_campo"]):
        compact = compact_text(row["original"])
        if compact is None:
            raise ValueError("No approved compact equivalent for " + row["grupo_id"])
        if len(encode_spanish(compact)) + 1 > int(row["capacidad_campo"]):
            compact = TIGHTER.get(row["original"], compact)
        value, why = compact, "etiqueta_compacta_para_campo_fijo"
    else:
        return value, "original_draft"

    if not value or "\0" in value or len(encode_spanish(value)) + 1 > int(row["capacidad_campo"]):
        raise ValueError("Compact text does not fit its fixed field at " + row["grupo_id"])
    return value, why


def audit_effective(source, draft):
    if len(source) != len(draft):
        raise ValueError("Corpus length mismatch")
    adjusted, reasons = [], Counter()
    seen_special = set()
    for row, translation in zip(source, draft):
        if row["grupo_id"] != translation["grupo_id"]:
            raise ValueError("Corpus misaligned")
        text, reason = effective(row, translation)
        changed = dict(translation)
        changed["espanol"] = text
        adjusted.append(changed)
        reasons[reason] += 1
        if reason == "original_truncado_verificado_por_bytes":
            seen_special.add(row["grupo_id"])
    if seen_special != set(INCOMPLETE_RAW):
        raise ValueError("Missing damaged source entries")
    return adjusted, dict(reasons)
