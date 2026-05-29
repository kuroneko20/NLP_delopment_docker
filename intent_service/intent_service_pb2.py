# -*- coding: utf-8 -*-
"""Lightweight protobuf-compatible messages for intent_service.proto.

This file is intentionally committed so the project can be inspected without
running code generation. The Makefile can regenerate official grpc_tools files
from intent_service.proto inside the intent_service container.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass


class DecodeError(ValueError):
    """Raised when a protobuf payload cannot be decoded."""


def _encode_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("varint cannot encode negative values")
    out = bytearray()
    while True:
        to_write = value & 0x7F
        value >>= 7
        if value:
            out.append(to_write | 0x80)
        else:
            out.append(to_write)
            break
    return bytes(out)


def _decode_varint(data: bytes, index: int) -> tuple[int, int]:
    shift = 0
    result = 0
    while index < len(data):
        byte = data[index]
        index += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, index
        shift += 7
        if shift >= 64:
            raise DecodeError("varint is too long")
    raise DecodeError("truncated varint")


def _encode_string(field_number: int, value: str) -> bytes:
    encoded = value.encode("utf-8")
    return _encode_varint((field_number << 3) | 2) + _encode_varint(len(encoded)) + encoded


def _skip_unknown(data: bytes, index: int, wire_type: int) -> int:
    if wire_type == 0:
        _, index = _decode_varint(data, index)
        return index
    if wire_type == 1:
        return index + 8
    if wire_type == 2:
        length, index = _decode_varint(data, index)
        return index + length
    if wire_type == 5:
        return index + 4
    raise DecodeError(f"unsupported wire type: {wire_type}")


@dataclass
class IntentRequest:
    message: str = ""

    def SerializeToString(self) -> bytes:
        payload = bytearray()
        if self.message:
            payload.extend(_encode_string(1, self.message))
        return bytes(payload)

    @classmethod
    def FromString(cls, data: bytes) -> "IntentRequest":
        message = ""
        index = 0
        while index < len(data):
            tag, index = _decode_varint(data, index)
            field_number = tag >> 3
            wire_type = tag & 0x07
            if field_number == 1 and wire_type == 2:
                length, index = _decode_varint(data, index)
                message = data[index:index + length].decode("utf-8")
                index += length
            else:
                index = _skip_unknown(data, index, wire_type)
        return cls(message=message)


@dataclass
class IntentResponse:
    intent: str = "unknown"
    confidence: float = 0.0
    reason: str = ""

    def SerializeToString(self) -> bytes:
        payload = bytearray()
        if self.intent:
            payload.extend(_encode_string(1, self.intent))
        payload.extend(_encode_varint((2 << 3) | 5))
        payload.extend(struct.pack("<f", float(self.confidence)))
        if self.reason:
            payload.extend(_encode_string(3, self.reason))
        return bytes(payload)

    @classmethod
    def FromString(cls, data: bytes) -> "IntentResponse":
        intent = "unknown"
        confidence = 0.0
        reason = ""
        index = 0
        while index < len(data):
            tag, index = _decode_varint(data, index)
            field_number = tag >> 3
            wire_type = tag & 0x07
            if field_number == 1 and wire_type == 2:
                length, index = _decode_varint(data, index)
                intent = data[index:index + length].decode("utf-8")
                index += length
            elif field_number == 2 and wire_type == 5:
                if index + 4 > len(data):
                    raise DecodeError("truncated float field")
                confidence = struct.unpack("<f", data[index:index + 4])[0]
                index += 4
            elif field_number == 3 and wire_type == 2:
                length, index = _decode_varint(data, index)
                reason = data[index:index + length].decode("utf-8")
                index += length
            else:
                index = _skip_unknown(data, index, wire_type)
        return cls(intent=intent, confidence=confidence, reason=reason)
