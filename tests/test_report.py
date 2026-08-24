"""Reporting helpers: saved tables must survive the round trip."""

import tempfile


def test_saved_tables_round_trip_small_values():
    """A record written with fixed decimals collapses 1e-6 onto 0, which
    silently merges two configurations into one row when it is read back.
    Any table used as a record must survive the round trip."""
    import pandas as pd

    from src.evaluation.report import save_table

    frame = pd.DataFrame({"weight_decay": [0.0, 1e-6, 1e-4, 1e-2], "ap": [0.1, 0.2, 0.3, 0.4]})
    with tempfile.TemporaryDirectory() as tmp:
        path = save_table(frame, tmp, "record", float_fmt="%.10g")
        back = pd.read_csv(path)
    assert back["weight_decay"].nunique() == 4, "distinct settings must stay distinct"
    pd.testing.assert_frame_equal(back, frame, check_exact=False, rtol=1e-9)
