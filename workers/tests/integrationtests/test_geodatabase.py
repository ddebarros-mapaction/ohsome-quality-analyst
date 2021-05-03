import asyncio
import os
import unittest

import geojson
import vcr

import ohsome_quality_analyst.geodatabase.client as db_client
from ohsome_quality_analyst.indicators.ghs_pop_comparison_buildings.indicator import (
    GhsPopComparisonBuildings,
)

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_BASENAME = os.path.splitext(os.path.basename(__file__))[0]


class TestGeodatabase(unittest.TestCase):
    def setUp(self):
        infile = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg_altstadt.geojson",
        )
        with open(infile, "r") as f:
            self.bpolys = geojson.load(f)

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def test_save_and_load(self):
        # TODO: split tests by functionality (load and safe),
        # but load test needs a saved indicator.
        dataset = "test_regions"
        feature_id = 2
        bpolys = asyncio.run(db_client.get_bpolys_from_db(dataset, feature_id))

        # save
        self.indicator = GhsPopComparisonBuildings(
            layer_name="building_count",
            bpolys=bpolys,
        )
        asyncio.run(self.indicator.preprocess())
        self.indicator.calculate()
        self.indicator.create_figure()
        asyncio.run(
            db_client.save_indicator_results(self.indicator, dataset, feature_id)
        )

        # load
        self.indicator = GhsPopComparisonBuildings(
            layer_name="building_count", bpolys=bpolys
        )
        result = asyncio.run(
            db_client.load_indicator_results(self.indicator, dataset, feature_id)
        )
        self.assertTrue(result)
        self.assertIsNotNone(self.indicator.result.label)
        self.assertIsNotNone(self.indicator.result.value)
        self.assertIsNotNone(self.indicator.result.description)
        self.assertIsNotNone(self.indicator.result.svg)

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def test_get_fids(self):
        result = asyncio.run(db_client.get_fids("test_regions"))
        self.assertIsInstance(result, list)

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def test_get_area_of_bpolys(self):
        result = asyncio.run(db_client.get_area_of_bpolys(self.bpolys))
        self.assertIsInstance(result, float)

    @vcr.use_cassette(
        os.path.join(TEST_DIR, "fixtures/vcr_cassettes", TEST_FILE_BASENAME + ".yml")
    )
    def test_get_bpolys_from_db(self):
        result = asyncio.run(db_client.get_bpolys_from_db("test_regions", 3))
        self.assertTrue(result.is_valid)


if __name__ == "__main__":
    unittest.main()
