"""JSON serialization for transactions and alerts.

JSON, not Avro/protobuf: at a few hundred messages per second the encoding
overhead is irrelevant and human-readable messages make the pipeline
debuggable. Python floats round-trip exactly through json (repr-based), so
streaming scores can be compared bit-for-bit with offline scores.
"""

import json

from src.data.load import FEATURE_COLUMNS


def encode_transaction(tx_id: int, row: dict, produced_at_ns: int) -> bytes:
    return json.dumps(
        {
            "tx_id": tx_id,
            "time": row["Time"],
            "features": [row[c] for c in FEATURE_COLUMNS],
            "class": int(row["Class"]),  # carried for offline reconciliation only
            "produced_at_ns": produced_at_ns,
        }
    ).encode()


def decode_transaction(payload: bytes) -> dict:
    return json.loads(payload)


def encode_alert(alert: dict) -> bytes:
    return json.dumps(alert).encode()


def decode_alert(payload: bytes) -> dict:
    return json.loads(payload)


END_OF_STREAM = b'{"end_of_stream": true}'


def is_end_of_stream(msg: dict) -> bool:
    return bool(msg.get("end_of_stream"))
