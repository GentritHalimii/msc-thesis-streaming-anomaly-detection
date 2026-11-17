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


def test_saved_tables_are_rounded_only_when_printed():
    """The default LaTeX format has four decimals, but the CSV must not: the
    thesis rounds to three, and 0.04748 stored as 0.0475 would print 0.048."""
    import pandas as pd

    from src.evaluation.report import save_table

    frame = pd.DataFrame({"ap": [0.04747625, 0.15046625]})
    with tempfile.TemporaryDirectory() as tmp:
        back = pd.read_csv(save_table(frame, tmp, "summary"))
    assert back["ap"].round(3).tolist() == [0.047, 0.150]
