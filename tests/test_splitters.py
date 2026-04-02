import pandas as pd

from app.research.splitters import in_out_split


def test_in_out_split() -> None:
    df = pd.DataFrame({"x": range(10)})
    ins, oos = in_out_split(df, ratio=0.6)
    assert len(ins) == 6
    assert len(oos) == 4
