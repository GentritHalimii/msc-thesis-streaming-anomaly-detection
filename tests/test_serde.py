"""JSON round-trip must preserve feature values exactly — offline/streaming
score parity depends on it."""

import numpy as np

from src.data.load import FEATURE_COLUMNS
from src.streaming.serde import (
    END_OF_STREAM,
    decode_transaction,
    encode_transaction,
    is_end_of_stream,
)


def test_transaction_roundtrip_is_exact():
    rng = np.random.default_rng(0)
    row = {c: float(v) for c, v in zip(FEATURE_COLUMNS, rng.normal(size=29), strict=True)}
    row["Time"] = 12345.0
    row["Class"] = 0
    decoded = decode_transaction(encode_transaction(7, row, produced_at_ns=123))
    assert decoded["tx_id"] == 7
    assert decoded["produced_at_ns"] == 123
    # bit-exact float round-trip (json uses repr shortest round-trip)
    assert decoded["features"] == [row[c] for c in FEATURE_COLUMNS]


def test_end_of_stream_sentinel():
    assert is_end_of_stream(decode_transaction(END_OF_STREAM))
    assert not is_end_of_stream({"tx_id": 1})
