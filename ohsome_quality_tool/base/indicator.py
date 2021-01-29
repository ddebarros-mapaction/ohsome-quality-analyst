"""
TODO:
    Describe this module and how to implement child classes
"""

import os
import uuid
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Dict

from dacite import from_dict
from geojson import FeatureCollection

import ohsome_quality_tool.geodatabase.client as db_client
from ohsome_quality_tool.utils.definitions import (
    DATA_PATH,
    get_layer_definition,
    get_metadata,
)


@dataclass
class Metadata:
    """Metadata of an indicator as defined in the metadata.yaml file"""

    name: str
    indicator_description: str
    label_description: Dict
    result_description: str


@dataclass
class LayerDefinition:
    """Definitions of a layer as defined in the layer_definition.yaml file.

    The definition consist of the ohsome API Parameter needed to create the layer.
    """

    name: str
    description: str
    endpoint: str
    filter: str


@dataclass
class Result:
    """The result of the Indicator."""

    label: str
    value: float
    description: str
    svg: str


class BaseIndicator(metaclass=ABCMeta):
    """
    The base class of every indicator.

    An indicator can be created in two ways:

    One; Calculate from scratch for an area of interest.
    This is done by providing a bounding polygone as input parameter.

    Two; Fetch the precaclulated results from the Geodatabase.
    This is done by providing the dataset name and feature id as input parameter.
    """

    def __init__(
        self,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        if bpolys:
            self.bpolys = bpolys
        elif bpolys is None and dataset and feature_id:
            self.dataset = dataset
            self.feature_id = feature_id
            self.bpolys = db_client.get_bpolys_from_db(self.dataset, self.feature_id)
        else:
            raise ValueError(
                "Provide either a bounding polygon "
                + "or dataset name and feature id as parameter."
            )
        # setattr(object, key, value) could be used instead of relying on from_dict.
        metadata = get_metadata("indicators", type(self).__name__)
        self.metadata: Metadata = from_dict(data_class=Metadata, data=metadata)

        layer = get_layer_definition(layer_name)
        self.layer: LayerDefinition = from_dict(data_class=LayerDefinition, data=layer)

        random_id = str(uuid.uuid1())
        filename = "_".join([self.metadata.name, self.layer.name, random_id, ".svg"])
        figure_path = os.path.join(DATA_PATH, filename)

        self.result: Result = Result(None, None, None, figure_path)

    @abstractmethod
    def preprocess(self) -> None:
        pass

    @abstractmethod
    def calculate(self) -> None:
        pass

    @abstractmethod
    def create_figure(self) -> None:
        pass
