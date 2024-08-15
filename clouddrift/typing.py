from datetime import timedelta

import numpy as np
import pandas as pd
import xarray as xr

_SupportedArrayTypes = list | np.ndarray | xr.DataArray | pd.Series
_ArrayTypes = _SupportedArrayTypes

_SupportedTimeDeltaTypes = pd.Timedelta | timedelta | np.timedelta64
_TimeDeltaTypes = _SupportedTimeDeltaTypes

__all__ = ["_ArrayTypes", "_TimeDeltaTypes"]
