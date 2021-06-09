import asyncio
import os
import unittest

import geojson

from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.indicators.mapping_saturation.indicator import (
    MappingSaturation,
)

from .utils import oqt_vcr


class TestIndicatorMappingSaturation(unittest.TestCase):
    def test(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )

        with open(infile, "r") as f:
            bpolys = geojson.load(f)
        layer_name = "major_roads_length"

        indicator = MappingSaturation(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())

        indicator.calculate()
        self.assertIsNotNone(indicator.result.label)
        self.assertIsNotNone(indicator.result.value)
        self.assertIsNotNone(indicator.result.description)

        indicator.create_figure()
        self.assertIsNotNone(indicator.result.svg)

    @oqt_vcr.use_cassette()
    def test_float_division_by_zero_error(self):
        layer_name = "building_count"
        dataset = "regions"
        feature_id = 31
        bpolys = asyncio.run(
            db_client.get_bpolys_from_db(dataset, feature_id, "ogc_fid")
        )

        indicator = MappingSaturation(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()

    @oqt_vcr.use_cassette()
    def test_cannot_convert_nan_error(self):
        layer_name = "building_count"
        dataset = "regions"
        feature_id = 28
        bpolys = asyncio.run(
            db_client.get_bpolys_from_db(dataset, feature_id, "ogc_fid")
        )

        indicator = MappingSaturation(layer_name=layer_name, bpolys=bpolys)
        asyncio.run(indicator.preprocess())
        indicator.calculate()
        indicator.create_figure()


if __name__ == "__main__":
    unittest.main()
