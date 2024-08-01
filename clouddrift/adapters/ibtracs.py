import os
import tempfile
from typing import Literal, TypeAlias

import numpy as np
import xarray as xr

from clouddrift.adapters.utils import download_with_progress
from clouddrift.raggedarray import RaggedArray

_DEFAULT_FILE_PATH = os.path.join(tempfile.gettempdir(), "clouddrift", "ibtracs")

_SOURCE_BASE_URI = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs"

_SOURCE_URL_FMT = "{base_uri}/{version}/access/netcdf/IBTrACS.{kind}.{version}.nc"

_Version: TypeAlias = Literal["v03r09"] | Literal["v04r00"] | Literal["v04r01"]

_Kind: TypeAlias = (
    Literal["ACTIVE"]
    | Literal["ALL"]
    | Literal["EP"]
    | Literal["NA"]
    | Literal["NI"]
    | Literal["SA"]
    | Literal["SI"]
    | Literal["SP"]
    | Literal["WP"]
    | Literal["LAST_3_YEARS"]
    | Literal["SINCE_1980"]
)


def _rowsize(idx: int, **kwargs):
    ds: xr.Dataset | None = kwargs.get("dataset")
    if ds is None:
        raise ValueError("kwargs dataset missing")
    return len(ds.isel(storm=idx)["time"].data)


def _preprocess(idx: int, **kwargs):
    ds: xr.Dataset | None = kwargs.get("dataset")
    data_vars: list[str] | None = kwargs.get("data_vars")
    md_vars: list[str] | None = kwargs.get("md_vars")

    if ds is not None and data_vars is not None and md_vars is not None:
        ds = ds.isel(storm=idx)
        vars = dict()

        for var in data_vars + list(ds.coords):
            if var != "time":
                vars.update({var: (ds[var].dims, ds[var].data)})

        for var in md_vars:
            vars.update({var: (("storm",), np.array([ds[var].data]))})

        return xr.Dataset(
            vars,
            {
                "id": (("storm",), np.array([idx])),
                "time": (("date_time",), np.array(ds["time"].data)),
            },
        )
    else:
        raise ValueError("kwargs dataset, data vars and md_vars missing")


def _kind_map(kind: _Kind):
    return {"LAST_3_YEARS": "last3years", "SINCE_1980": "since1980"}.get(kind, kind)


def _get_source_url(version: _Version, kind: _Kind):
    return _SOURCE_URL_FMT.format(
        base_uri=_SOURCE_BASE_URI, version=version, kind=_kind_map(kind)
    )


def to_raggedarray(
    version: _Version, kind: _Kind, tmp_path: str = _DEFAULT_FILE_PATH
) -> xr.Dataset:
    os.makedirs(tmp_path, exist_ok=True)
    src_url = _get_source_url(version, kind)

    filename = src_url.split("/")[-1]
    dst_path = os.path.join(tmp_path, filename)
    download_with_progress([(src_url, dst_path, None)])

    ds = xr.open_dataset(dst_path, engine="netcdf4")

    data_vars = list()
    md_vars = list()

    for var_name in ds.variables:
        # time variable shouldn't be considered a data or metadata variable
        if var_name in ["time"]:
            continue

        var: xr.DataArray = ds[var_name]

        # Avoid loading the data variables that also utilize the quadrant dimension for now
        if "date_time" in var.dims and len(var.dims) == 2:
            data_vars.append(var_name)
        elif len(var.dims) == 1 and var.dims[0] == "storm":
            md_vars.append(var_name)

    ra = RaggedArray.from_files(
        indices=list(range(0, len(ds["sid"]))),
        name_coords=["id", "time"],
        name_meta=md_vars,
        name_data=data_vars,
        name_dims={"storm": "rows", "date_time": "obs"},
        rowsize_func=_rowsize,
        preprocess_func=_preprocess,
        attrs_global=ds.attrs,
        attrs_variables={
            var_name: ds[var_name].attrs for var_name in data_vars + md_vars
        },
        dataset=ds,
        data_vars=data_vars,
        md_vars=md_vars,
    )
    return ra.to_xarray()