import pandas as pd


def exposure_ok(exposures: dict[str, float], max_single_asset: float = 0.4) -> bool:
    return all(abs(v) <= max_single_asset for v in exposures.values())


def correlation_matrix(price_df: pd.DataFrame) -> pd.DataFrame:
    return price_df.pct_change().corr()
