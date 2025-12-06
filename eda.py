import io
import os
import tempfile
from typing import Dict

import numpy as np
import pandas as pd
from scipy import stats


def _try_excel_bytes(bio, engines):
    for eng in engines:
        try:
            bio.seek(0)
            return pd.read_excel(bio, engine=eng)
        except Exception:
            continue
    # final generic try without engine
    try:
        bio.seek(0)
        return pd.read_excel(bio)
    except Exception:
        return None


def _try_csv(source, low_memory=True):
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1", "iso-8859-1"]
    last_err = None

    # Debug: check file size
    file_size = 0
    if isinstance(source, (str, os.PathLike)):
        try:
            file_size = os.path.getsize(source)
            if file_size == 0:
                raise ValueError("File is empty (0 bytes)")
        except Exception as e:
            pass

    for enc in encodings:
        try:
            if isinstance(source, (str, os.PathLike)):
                df = pd.read_csv(
                    source, encoding=enc, low_memory=low_memory, on_bad_lines="skip"
                )
            else:
                source.seek(0)
                df = pd.read_csv(
                    source, encoding=enc, low_memory=low_memory, on_bad_lines="skip"
                )

            # Check if DataFrame is valid
            if df is not None and len(df.columns) > 0:
                return df
            else:
                raise ValueError("No columns found in file")
        except Exception as e:
            last_err = e
            continue

    # If all encodings fail, try with different delimiters
    for enc in ["utf-8", "cp1252", "latin1"]:
        for delimiter in [",", ";", "\t", "|"]:
            try:
                if isinstance(source, (str, os.PathLike)):
                    df = pd.read_csv(
                        source,
                        encoding=enc,
                        delimiter=delimiter,
                        low_memory=low_memory,
                        on_bad_lines="skip",
                    )
                else:
                    source.seek(0)
                    df = pd.read_csv(
                        source,
                        encoding=enc,
                        delimiter=delimiter,
                        low_memory=low_memory,
                        on_bad_lines="skip",
                    )

                if df is not None and len(df.columns) > 0:
                    return df
            except Exception:
                continue

    raise ValueError(
        f"Failed to read CSV. File size: {file_size} bytes. Last error: {last_err}. "
        "Please check if the file contains valid data and is not empty."
    )


def _read_path(path: str) -> pd.DataFrame:
    lower = path.lower()
    if lower.endswith((".csv", ".txt")):
        return _try_csv(path, low_memory=False)
    if lower.endswith(".xlsx"):
        try:
            return pd.read_excel(path, engine="openpyxl")
        except Exception:
            return pd.read_excel(path)
    if lower.endswith(".xls"):
        try:
            return pd.read_excel(path, engine="xlrd")
        except Exception:
            raise ValueError(
                "Failed to read .xls file. Install 'xlrd==1.2.0' or convert to CSV."
            )
    if lower.endswith(".xlsb"):
        try:
            return pd.read_excel(path, engine="pyxlsb")
        except Exception:
            raise ValueError(
                "Failed to read .xlsb file. Install 'pyxlsb' or convert to CSV."
            )
    # fallback
    try:
        return _try_csv(path, low_memory=False)
    except Exception:
        return pd.read_excel(path)


def read_dataset(uploaded_file) -> pd.DataFrame:
    """Read uploaded file (streamlit UploadedFile or path-like) into DataFrame.

    Attempts to choose the right engine for Excel files, tries multiple common
    CSV encodings, and for large uploads writes a temporary file to disk
    before reading to avoid BytesIO/engine detection issues.
    """

    if hasattr(uploaded_file, "read"):
        content = uploaded_file.read()
        size = getattr(uploaded_file, "size", None)
        if size is None:
            try:
                size = len(content)
            except Exception:
                size = None

        name = getattr(uploaded_file, "name", "") or ""

        # For large uploads, write to a temp file and read from disk
        if size is not None and size > 5_000_000:
            suffix = ""
            lower = name.lower()
            if lower.endswith(".csv") or lower.endswith(".txt"):
                suffix = ".csv"
            elif lower.endswith(".xlsx"):
                suffix = ".xlsx"
            elif lower.endswith(".xls"):
                suffix = ".xls"
            elif lower.endswith(".xlsb"):
                suffix = ".xlsb"
            else:
                suffix = ".bin"

            tmp = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                    f.write(content)
                    tmp = f.name
                return _read_path(tmp)
            finally:
                try:
                    if tmp and os.path.exists(tmp):
                        os.remove(tmp)
                except Exception:
                    pass

        # For smaller files, use BytesIO
        bio = io.BytesIO(content)
        lower = name.lower()
        if lower.endswith(".csv") or lower.endswith(".txt"):
            bio.seek(0)
            return _try_csv(bio, low_memory=False)
        if lower.endswith(".xlsx"):
            df = _try_excel_bytes(bio, engines=["openpyxl"])
            if df is not None:
                return df
            raise ValueError(
                "Failed to read .xlsx file. Ensure 'openpyxl' is installed (pip install openpyxl)."
            )
        if lower.endswith(".xls"):
            df = _try_excel_bytes(bio, engines=["xlrd"])
            if df is not None:
                return df
            raise ValueError(
                "Failed to read .xls file. Install 'xlrd==1.2.0' or convert the file to .xlsx/CSV."
            )
        if lower.endswith(".xlsb"):
            df = _try_excel_bytes(bio, engines=["pyxlsb"])
            if df is not None:
                return df
            raise ValueError(
                "Failed to read .xlsb file. Install 'pyxlsb' or convert the file to .xlsx/CSV."
            )

        # Unknown extension: try CSV then Excel
        bio.seek(0)
        try:
            return _try_csv(bio)
        except Exception:
            df = _try_excel_bytes(bio, engines=["openpyxl", "xlrd", "pyxlsb"])
            if df is not None:
                return df
            raise ValueError(
                "Excel file format cannot be determined; please provide a valid CSV or Excel file.\n"
                "For .xlsx install 'openpyxl', for .xls install 'xlrd==1.2.0', for .xlsb install 'pyxlsb'."
            )

    else:
        path = str(uploaded_file)
        return _read_path(path)


def basic_profile(df: pd.DataFrame) -> Dict:
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isna().sum().to_dict(),
    }


def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    return df.describe(include="all").transpose()


def column_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Return a consistent per-column profile table.

    Columns:
      column        : column name
      dtype         : pandas dtype (string)
      non_null      : count of non-null values
      missing       : count of missing values
      missing_pct   : percentage of missing values (0-100)
      unique        : number of unique non-null values
      sample_values : up to 3 representative non-null unique values
      min           : numeric min (blank if non-numeric)
      max           : numeric max (blank if non-numeric)
      mean          : numeric mean (blank if non-numeric)
      median        : numeric median (blank if non-numeric)
      memory_bytes  : estimated memory usage for the column
    """
    rows = []
    total_rows = len(df)
    for col in df.columns:
        series = df[col]
        non_null = series.notna().sum()
        missing = total_rows - non_null
        missing_pct = (missing / total_rows * 100.0) if total_rows else 0.0
        uniques = series.dropna().unique()
        unique_count = len(uniques)
        # Sample values (convert to string, limit length for very long entries)
        sample_vals = []
        for v in uniques[:10]:
            sv = str(v)
            if len(sv) > 30:
                sv = sv[:27] + "…"
            sample_vals.append(sv)
        sample_values = ", ".join(sample_vals)
        is_numeric = pd.api.types.is_numeric_dtype(series)
        if is_numeric:
            numeric_min = f"{series.min():.2f}" if not pd.isna(series.min()) else ""
            numeric_max = f"{series.max():.2f}" if not pd.isna(series.max()) else ""
            numeric_mean = f"{series.mean():.2f}" if not pd.isna(series.mean()) else ""
            numeric_median = (
                f"{series.median():.2f}" if not pd.isna(series.median()) else ""
            )
        else:
            numeric_min = ""
            numeric_max = ""
            numeric_mean = ""
            numeric_median = ""
        memory_bytes = series.memory_usage(deep=True)
        rows.append(
            {
                "column": col,
                "dtype": str(series.dtype),
                "non_null": int(non_null),
                "missing": int(missing),
                "missing_pct": round(missing_pct, 2),
                "unique": int(unique_count),
                "sample_values": sample_values,
                "min": numeric_min,
                "max": numeric_max,
                "mean": numeric_mean,
                "median": numeric_median,
                "memory_bytes": int(memory_bytes),
            }
        )
    return pd.DataFrame(rows)


def detect_outliers_iqr(series: pd.Series, factor: float = 1.5) -> pd.Series:
    if not np.issubdtype(series.dtype, np.number):
        return pd.Series([False] * len(series), index=series.index)
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - factor * iqr
    upper = q3 + factor * iqr
    return (series < lower) | (series > upper)


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    if not np.issubdtype(series.dtype, np.number):
        return pd.Series([False] * len(series), index=series.index)
    z = np.abs(stats.zscore(series.dropna()))
    mask = pd.Series(False, index=series.index)
    mask.loc[series.dropna().index] = z > threshold
    return mask


def outlier_summary(df: pd.DataFrame, method: str = "iqr", **kwargs) -> pd.DataFrame:
    methods = {
        "iqr": detect_outliers_iqr,
        "zscore": detect_outliers_zscore,
    }
    fn = methods.get(method)
    if fn is None:
        raise ValueError("Unsupported method")
    rows = []
    for col in df.columns:
        mask = fn(df[col], **kwargs)
        rows.append(
            {
                "column": col,
                "outlier_count": int(mask.sum()),
                "outlier_pct": float(mask.mean()),
            }
        )
    return pd.DataFrame(rows)


def apply_cleaning(df: pd.DataFrame, actions: Dict) -> pd.DataFrame:
    """
    actions: dict keyed by column name with values like:
      {'method': 'drop'|'cap'|'impute', 'impute': 'mean'|'median'|'mode', 'lower': val, 'upper': val}
    """
    result = df.copy()

    def _apply_single(col_name: str, act: Dict):
        nonlocal result
        if col_name not in result.columns:
            return
        method = act.get("method")
        if method == "drop":
            mask = act.get("mask")
            if mask is not None:
                # Align mask with current result index if possible
                try:
                    mask = mask.reindex(result.index).fillna(False)
                except Exception:
                    pass
                result = result.loc[~mask].reset_index(drop=True)
        elif method == "cap":
            lower = act.get("lower")
            upper = act.get("upper")
            # Only apply numeric capping — safely coerce to numeric first.
            series = result[col_name]
            numeric = pd.to_numeric(series, errors="coerce")
            if lower is not None and numeric.notna().any():
                # Use numeric mask to determine where to cap, preserve original values where non-numeric
                mask_lower = numeric < lower
                result.loc[mask_lower, col_name] = lower
            if upper is not None and numeric.notna().any():
                mask_upper = numeric > upper
                result.loc[mask_upper, col_name] = upper
        elif method == "impute":
            strategy = act.get("impute", "median")
            series = result[col_name]
            # Try numeric aggregation first; if not possible, fallback to mode
            if strategy == "mean":
                numeric = pd.to_numeric(series, errors="coerce")
                if numeric.dropna().empty:
                    val = series.mode().iloc[0] if not series.mode().empty else np.nan
                else:
                    val = numeric.mean()
            elif strategy == "median":
                numeric = pd.to_numeric(series, errors="coerce")
                if numeric.dropna().empty:
                    val = series.mode().iloc[0] if not series.mode().empty else np.nan
                else:
                    val = numeric.median()
            else:
                val = series.mode().iloc[0] if not series.mode().empty else np.nan

            result[col_name] = series.fillna(val)

    for col, act in actions.items():
        # Support either a single dict or a list of action dicts per column
        if isinstance(act, list):
            for subact in act:
                _apply_single(col, subact)
        else:
            _apply_single(col, act)

    return result
