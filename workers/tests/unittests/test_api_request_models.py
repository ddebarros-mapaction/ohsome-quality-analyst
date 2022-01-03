"""Test module for the `pydantic` data models for API requests"""
import json
import os
import unittest

from geojson import Polygon

from ohsome_quality_analyst.api import request_models


class TestApiRequestModels(unittest.TestCase):
    def setUp(self):
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "fixtures",
            "heidelberg-altstadt-feature.geojson",
        )
        with open(path, "r") as file:
            self.bpolys = json.load(file)

    def test_bpolys_valid(self):
        request_models.BasePOSTModel(bpolys=self.bpolys)

    def test_bpolys_invalid(self):
        bpolys = Polygon(
            [[(2.38, 57.322), (23.194, -20.28), (-120.43, 19.15), (2.0, 1.0)]]
        )

        with self.assertRaises(ValueError):
            request_models.BasePOSTModel(bpolys=bpolys)

    def test_dataset_valid(self):
        request_models.BasePOSTModel(dataset="regions", feature_id="3")
        request_models.BasePOSTModel(
            dataset="regions", feature_id="3", fid_field="ogc_fid"
        )
        request_models.BaseGETModel(dataset="regions", feature_id="3")
        request_models.BaseGETModel(
            dataset="regions", feature_id="3", fid_field="ogc_fid"
        )

    def test_dataset_invalid(self):
        with self.assertRaises(ValueError):
            request_models.BasePOSTModel(dataset="foo", feature_id="3")
        with self.assertRaises(ValueError):
            request_models.BaseGETModel(dataset="foo", feature_id="3")

    def test_invalid_set_of_arguments(self):
        with self.assertRaises(ValueError):
            request_models.BasePOSTModel(
                bpolys=self.bpolys, dataset="regions", feature_id="3"
            )
        with self.assertRaises(ValueError):
            request_models.BasePOSTModel(dataset="regions")
        with self.assertRaises(ValueError):
            request_models.BaseGETModel(dataset="regions")
        with self.assertRaises(ValueError):
            request_models.BasePOSTModel(feature_id="3")
        with self.assertRaises(ValueError):
            request_models.BaseGETModel(feature_id="3")
        with self.assertRaises(ValueError):
            request_models.BaseIndicatorModel(name="GhsPopComparisonBuildings")
        with self.assertRaises(ValueError):
            request_models.BaseIndicatorModel(layer_name="building_count")

    def test_valid_indicator_layer_combination(self):
        request_models.BaseIndicatorModel(
            name="GhsPopComparisonBuildings",
            layerName="building_count",
        )

    def test_invalid_indicator_layer_combination(self):
        with self.assertRaises(ValueError):
            request_models.BaseIndicatorModel(
                name="GhsPopComparisonBuildings",
                layerName="amenities",
            )
