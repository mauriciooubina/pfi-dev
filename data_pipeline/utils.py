import os
import hashlib
import pandas as pd
import numpy as np

def get_crypto_salt(shop_id: str) -> str:
    """
    Get the cryptographic salt for the specified shop from environment variables,
    falling back to predefined defaults if not found.
    """
    shop_id_upper = shop_id.upper()
    if "HELLFISH" in shop_id_upper:
        return os.getenv("HELLFISH_SALT", "HF_2026_SALT")
    elif "HOOLIGANS" in shop_id_upper:
        return os.getenv("HOOLIGANS_SALT", "HL_2026_SALT")
    return os.getenv(f"{shop_id_upper}_SALT", "DEFAULT_2026_SALT")


def hash_sensitive_data(val: str, salt: str) -> str:
    """
    Compute a SHA-256 cryptographic hash of the input value concatenated with a salt,
    truncated to 16 characters. Safe against nuls and formatting errors.
    """
    try:
        if pd.isna(val) or not str(val).strip() or str(val).strip().lower() in ['nan', 'null', 'none']:
            return np.nan
        raw_str = f"{str(val).strip()}_{salt}"
        sha256_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
        return sha256_hash[:16]
    except Exception as e:
        print(f"[Warning] Failed to hash value '{val}' with error: {e}. Returning NaN.")
        return np.nan


def safe_parse_datetime(date_series: pd.Series, time_series: pd.Series = None) -> pd.Series:
    """
    Helper to parse datetime strings safely with try-except fallback.
    """
    try:
        if time_series is not None:
            # Combine date and time, replacing NaN string formats
            combined = date_series.astype(str) + ' ' + time_series.astype(str)
            clean_combined = combined.apply(
                lambda x: np.nan if any(t in str(x).lower() for t in ['nan', 'null', 'none', 'nat']) else str(x).strip()
            )
            return pd.to_datetime(clean_combined, errors='coerce')
        else:
            clean_dates = date_series.astype(str).apply(
                lambda x: np.nan if any(t in str(x).lower() for t in ['nan', 'null', 'none', 'nat']) else str(x).strip()
            )
            return pd.to_datetime(clean_dates, errors='coerce')
    except Exception as e:
        print(f"[Warning] Exception in safe_parse_datetime: {e}. Falling back to standard pandas coerce.")
        try:
            if time_series is not None:
                return pd.to_datetime(date_series.astype(str) + ' ' + time_series.astype(str), errors='coerce')
            return pd.to_datetime(date_series, errors='coerce')
        except Exception:
            return pd.Series([pd.NaT] * len(date_series))


def make_tz_naive(series: pd.Series) -> pd.Series:
    """
    Ensure a pandas datetime Series is timezone-naive so it can be subtracted.
    """
    try:
        if not pd.api.types.is_datetime64_any_dtype(series):
            series = pd.to_datetime(series, errors='coerce')
        if series.dt.tz is not None:
            return series.dt.tz_localize(None)
    except Exception as e:
        print(f"[Warning] Error converting to timezone-naive: {e}")
    return series
