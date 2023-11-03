import json
import os

from helpers import find_string_in_stream

DATA_DIR = "tests/fixtures"
test_zarr_store = os.path.join(DATA_DIR, "test_zarr_store.zarr")
test_reference_store = os.path.join(DATA_DIR, "reference.json")
test_netcdf_store = os.path.join(DATA_DIR, "testfile.nc")
test_remote_netcdf_store = "https://nex-gddp-cmip6.s3-us-west-2.amazonaws.com/NEX-GDDP-CMIP6/GISS-E2-1-G/historical/r1i1p1f2/pr/pr_day_GISS-E2-1-G_historical_r1i1p1f2_gn_1950.nc"
test_unconsolidated_store = os.path.join(DATA_DIR, "unconsolidated.zarr")
test_pyramid_store = os.path.join(DATA_DIR, "pyramid.zarr")

test_zarr_store_params = {
    "params": {"url": test_zarr_store, "variable": "CDD0", "decode_times": False},
    "variables": ["CDD0", "DISPH", "FROST_DAYS", "GWETPROF"],
}

test_reference_store_params = {
    "params": {
        "url": test_reference_store,
        "variable": "value",
        "reference": True,
        "decode_times": False,
    },
    "variables": ["value"],
}
test_netcdf_store_params = {
    "params": {"url": test_netcdf_store, "variable": "data", "decode_times": False},
    "variables": ["data"],
}
test_remote_netcdf_store_params = {
    "params": {
        "url": test_remote_netcdf_store,
        "variable": "pr",
        "decode_times": False,
    },
    "variables": ["pr"],
}
test_unconsolidated_store_params = {
    "params": {
        "url": test_unconsolidated_store,
        "variable": "var1",
        "decode_times": False,
        "consolidated": False,
    },
    "variables": ["var1", "var2"],
}
test_pyramid_store_params = {
    "params": {
        "url": test_pyramid_store,
        "variable": "value",
        "decode_times": False,
        "multiscale": True,
        "group": "2",
        "consolidated": False,
    },
    "variables": ["value"],
}


def get_variables_test(app, ds_params):
    response = app.get("/variables", params=ds_params["params"])
    assert response.status_code == 200
    assert response.json() == ds_params["variables"]
    assert response.headers["server-timing"]
    timings = response.headers["server-timing"].split(",")
    assert len(timings) == 2
    assert timings[0].startswith("total;dur=")
    assert timings[1].lstrip().startswith("1-xarray-open_dataset;dur=")


def test_get_variables_test(app):
    return get_variables_test(app, test_zarr_store_params)


def test_get_variables_reference(app):
    return get_variables_test(app, test_reference_store_params)


def test_get_variables_netcdf(app):
    return get_variables_test(app, test_netcdf_store_params)


def test_get_variables_remote_netcdf(app):
    return get_variables_test(app, test_remote_netcdf_store_params)


def test_get_variables_unconsolidated(app):
    return get_variables_test(app, test_unconsolidated_store_params)


def test_get_variables_pyramid(app):
    return get_variables_test(app, test_pyramid_store_params)


def get_info_test(app, ds_params):
    response = app.get(
        "/info",
        params=ds_params["params"],
    )
    assert response.status_code == 200
    with open(
        f"{ds_params['params']['url'].replace(DATA_DIR, f'{DATA_DIR}/responses').replace('.', '_')}_info.json",
        "r",
    ) as f:
        assert response.json() == json.load(f)


def test_get_info_test(app):
    return get_info_test(app, test_zarr_store_params)


def test_get_info_reference(app):
    return get_info_test(app, test_reference_store_params)


def test_get_info_netcdf(app):
    return get_info_test(app, test_netcdf_store_params)


def test_get_info_unconsolidated(app):
    return get_info_test(app, test_unconsolidated_store_params)


def test_get_info_pyramid(app):
    return get_info_test(app, test_pyramid_store_params)


def get_tilejson_test(app, ds_params):
    response = app.get(
        "/tilejson.json",
        params=ds_params["params"],
    )
    assert response.status_code == 200
    with open(
        f"{ds_params['params']['url'].replace(DATA_DIR, f'{DATA_DIR}/responses').replace('.', '_')}_tilejson.json",
        "r",
    ) as f:
        assert response.json() == json.load(f)


def test_get_tilejson_test(app):
    return get_tilejson_test(app, test_zarr_store_params)


def test_get_tilejson_reference(app):
    return get_tilejson_test(app, test_reference_store_params)


def test_get_tilejson_netcdf(app):
    return get_tilejson_test(app, test_netcdf_store_params)


def test_get_tilejson_unconsolidated(app):
    return get_tilejson_test(app, test_unconsolidated_store_params)


def test_get_tilejson_pyramid(app):
    return get_tilejson_test(app, test_pyramid_store_params)


def get_tile_test(app, ds_params, zoom: int = 0):
    response = app.get(
        f"/tiles/{zoom}/0/0.png",
        params=ds_params["params"],
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["server-timing"]
    timings = response.headers["server-timing"].split(",")
    assert len(timings) == 3
    assert timings[1].lstrip().startswith("1-xarray-open_dataset;dur=")
    assert timings[2].lstrip().startswith("2-rioxarray-reproject;dur=")


def test_get_tile_test(app):
    return get_tile_test(app, test_zarr_store_params)


def test_get_tile_reference(app):
    return get_tile_test(app, test_reference_store_params)


def test_get_tile_netcdf(app):
    return get_tile_test(app, test_netcdf_store_params)


def test_get_tile_unconsolidated(app):
    return get_tile_test(app, test_unconsolidated_store_params)


def test_get_tile_pyramid(app):
    # test that even a group outside of the range will return a tile
    for z in range(3):
        get_tile_test(app, test_pyramid_store_params, zoom=z)


def test_get_tile_pyramid_error(app):
    response = app.get(
        "/tiles/3/0/0.png",
        params=test_pyramid_store_params["params"],
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "group not found at path '3'"}


def histogram_test(app, ds_params):
    response = app.get(
        "/histogram",
        params=ds_params["params"],
    )
    assert response.status_code == 200
    with open(
        f"{ds_params['params']['url'].replace(DATA_DIR, f'{DATA_DIR}/responses').replace('.', '_')}_histogram.json",
        "r",
    ) as f:
        assert response.json() == json.load(f)


def test_histogram_test(app):
    return histogram_test(app, test_zarr_store_params)


def test_histogram_reference(app):
    return histogram_test(app, test_reference_store_params)


def test_histogram_netcdf(app):
    return histogram_test(app, test_netcdf_store_params)


def test_histogram_unconsolidated(app):
    return histogram_test(app, test_unconsolidated_store_params)


def test_histogram_pyramid(app):
    return histogram_test(app, test_pyramid_store_params)


def test_histogram_error(app):
    response = app.get(
        "/histogram",
        params={"url": test_zarr_store},
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["query", "variable"],
                "msg": "Field required",
                "input": None,
                "url": "https://errors.pydantic.dev/2.1.2/v/missing",
            }
        ]
    }


def test_map_without_params(app):
    response = app.get("/map")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert find_string_in_stream(response, "Step 1: Enter the URL of your Zarr store")


def test_map_with_params(app):
    response = app.get("/map", params={"url": test_zarr_store, "variable": "CDD0"})
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert find_string_in_stream(response, "<div id='map' class=\"hidden\"></div>")
