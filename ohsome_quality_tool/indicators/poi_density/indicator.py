import json
from string import Template

import matplotlib.pyplot as plt
import numpy as np
from geojson import FeatureCollection

from ohsome_quality_tool.base.indicator import BaseIndicator
from ohsome_quality_tool.geodatabase.client import get_area_of_bpolys
from ohsome_quality_tool.ohsome import client as ohsome_client
from ohsome_quality_tool.utils.definitions import TrafficLightQualityLevels, logger

# threshold values defining the color of the traffic light
# derived directly from sketchmap_fitness repo


class PoiDensity(BaseIndicator):
    def __init__(
        self,
        dynamic: bool,
        layer_name: str,
        bpolys: FeatureCollection = None,
        dataset: str = None,
        feature_id: int = None,
    ) -> None:
        super().__init__(
            dynamic=dynamic,
            layer_name=layer_name,
            bpolys=bpolys,
            dataset=dataset,
            feature_id=feature_id,
        )
        self.threshold_yellow = 30
        self.threshold_red = 10
        self.area_sqkm = None
        self.count = None
        self.density = None

    def preprocess(self):
        logger.info(f"Preprocessing for indicator: {self.metadata.name}")

        query_results_count = ohsome_client.query(
            layer=self.layer, bpolys=json.dumps(self.bpolys)
        )

        self.area_sqkm = get_area_of_bpolys(self.bpolys)  # calc polygon area
        self.count = query_results_count["result"][0]["value"]
        self.density = self.count / self.area_sqkm

    def calculate(self):
        # TODO: we need to think about how we handle this
        #  if there are different layers
        logger.info(f"Calculation for indicator: {self.metadata.name}")

        description = Template(self.metadata.result_description).substitute(
            result=f"{self.density:.2f}"
        )
        if self.density >= self.threshold_yellow:
            self.result.value = 1.0
            self.result.label = TrafficLightQualityLevels.GREEN
            self.result.description = (
                description + self.metadata.label_description["green"]
            )
        else:
            self.result.value = self.density / self.threshold_red
            if self.density > self.threshold_red:
                self.result.label = TrafficLightQualityLevels.YELLOW
                self.result.description = (
                    description + self.metadata.label_description["yellow"]
                )
            else:
                self.result.label = TrafficLightQualityLevels.RED
                self.result.description = (
                    description + self.metadata.label_description["red"]
                )

    def create_figure(self) -> str:
        def greenThresholdFunction(area):
            return self.threshold_yellow * area

        def yellowThresholdFunction(area):
            return self.threshold_red * area

        px = 1 / plt.rcParams["figure.dpi"]  # Pixel in inches
        figsize = (400 * px, 400 * px)
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()

        ax.set_title("POI Density (POIs per Area)")
        ax.set_xlabel("Area [$km^2$]")
        ax.set_ylabel("POIs")

        # Set x max value based on area
        if self.area_sqkm < 10:
            max_area = 10
        else:
            max_area = round(self.area_sqkm * 2 / 10) * 10
        x = np.linspace(0, max_area, 2)

        # Plot thresholds as line.
        y1 = [greenThresholdFunction(xi) for xi in x]
        y2 = [yellowThresholdFunction(xi) for xi in x]

        line = ax.plot(
            x,
            y1,
            color="black",
            label="Threshold A",
        )
        plt.setp(line, linestyle="--")

        line = ax.plot(
            x,
            y2,
            color="black",
            label="Threshold B",
        )
        plt.setp(line, linestyle=":")

        # Fill in space between thresholds
        ax.fill_between(x, y2, 0, alpha=0.5, color="red")
        ax.fill_between(x, y1, y2, alpha=0.5, color="yellow")
        ax.fill_between(x, y1, max(max(y1), self.count), alpha=0.5, color="green")

        # Plot point as circle ("o").
        ax.plot(
            self.area_sqkm,
            self.count,
            "o",
            color="black",
            label="location",
        )

        ax.legend()

        logger.info(
            f"Save figure for indicator: {self.metadata.name}\n to: {self.result.svg}"
        )
        plt.savefig(self.result.svg, format="svg")
        plt.close("all")
