from dataclasses import dataclass
from typing import Optional
from typing import *
import sys
import unittest
import math

sys.setrecursionlimit(10**6)
EARTH_RADIUS_KM: float = 6378.1


# Data Classes

# GlobeRect - rectangular region of the globe
@dataclass(frozen=True)
class GlobeRect:
    hi_lat: float # north latitude   
    lo_lat: float # south latitude   
    west_long: float # west longitude
    east_long: float # east longitude
# all coordinates use decimal degrees

# Region - describes identity and terrain of region
@dataclass(frozen=True)
class Region:
    rect: GlobeRect # boundaries of region
    name: str # name of region
    terrain: str # ocean, mountains, forest, other

# RegionCondition - descibes current state
@dataclass(frozen=True)
class RegionCondition:
    region: Region
    year: int # year of observation
    pop: int # population of region
    ghg_rate: float # ghg emissions in tons of CO2



# Example Data
# Four instances of RegionCondition
# New York Metro, Sydney Metro, Catalina Island, SLO County
region_conditions = [
    # New York metro area, North America
    RegionCondition(
        region=Region(
            rect=GlobeRect(
                hi_lat=41.2,
                lo_lat=40.3,
                west_long=-74.6,
                east_long=-73.4,
            ),
            name="New York metropolitan area",
            terrain="other",
        ),
        year=2024,
        pop=20000000,
        ghg_rate=80000000.0,
    ),

    # Sydney metro area, Australia / Oceania
    RegionCondition(
        region=Region(
            rect=GlobeRect(
                hi_lat=-33.4,
                lo_lat=-34.2,
                west_long=150.5,
                east_long=151.5,
            ),
            name="Sydney metropolitan area",
            terrain="other",
        ),
        year=2024,
        pop=5000000,
        ghg_rate=20000000.0,
    ),

    # Southern California Bight / Catalina ocean region
    RegionCondition(
        region=Region(
            rect=GlobeRect(
                hi_lat=34.2,
                lo_lat=32.8,
                west_long=-119.0,
                east_long=-117.2,
            ),
            name="Southern California Bight near Catalina",
            terrain="ocean",
        ),
        year=2024,
        pop=0,
        ghg_rate=100000.0,
    ),

    # SLO County Region
     RegionCondition(
        region=Region(
            rect=GlobeRect(
                hi_lat=35.6,
                lo_lat=35.0,
                west_long=-120.9,
                east_long=-120.2,
            ),
            name="San Luis Obispo County / Cal Poly region",
            terrain="other",
        ),
        year=2024,
        pop=300000,
        ghg_rate=1000000.0,
    ),
]


# External Functions (no methods, recursive)

# Purpose: Return annual greenhouse-gas emissions per person for a region condition.
# Type: RegionCondition -> float

def emissions_per_capita(rc: RegionCondition) -> float:
    if rc.pop <= 0:
        return 0.0
    return rc.ghg_rate / rc.pop


def _longitude_width_radians(west_long: float, east_long: float) -> float:
    """Return eastward longitude width in radians, correcting for date-line wraparound."""

    west_radians = math.radians(west_long)
    east_radians = math.radians(east_long)
    width = east_radians - west_radians
    if width < 0:
        return width + (2 * math.pi)
    return width


# Purpose: Return the spherical surface area of a globe rectangle in square kilometers.
# Type: GlobeRect -> float
def area(gr: GlobeRect) -> float:
    lo_lat_radians = math.radians(gr.lo_lat)
    hi_lat_radians = math.radians(gr.hi_lat)
    longitude_width = _longitude_width_radians(gr.west_long, gr.east_long)
    latitude_height = math.sin(hi_lat_radians) - math.sin(lo_lat_radians)
    return (EARTH_RADIUS_KM ** 2) * abs(longitude_width) * abs(latitude_height)


# Purpose: Return emissions per square kilometer for a region condition.
# Type: RegionCondition -> float
def emissions_per_square_km(rc: RegionCondition) -> float:
    region_area = area(rc.region.rect)
    if region_area == 0.0:
        return 0.0
    return rc.ghg_rate / region_area


def _population_density(rc: RegionCondition) -> float:
    """Return population density, treating positive population in zero area as infinite."""

    region_area = area(rc.region.rect)
    if region_area == 0.0:
        if rc.pop > 0:
            return float("inf")
        return 0.0
    return rc.pop / region_area


def _densest_region(rc_list: List[RegionCondition]) -> RegionCondition:
    """Return the densest region condition from a non-empty list."""

    if len(rc_list) == 1:
        return rc_list[0]

    densest_rest = _densest_region(rc_list[1:])
    if _population_density(rc_list[0]) >= _population_density(densest_rest):
        return rc_list[0]
    return densest_rest


# Purpose: Return the name of the region with the greatest population density.
# Type: List[RegionCondition] -> str
def densest(rc_list: List[RegionCondition]) -> str:
    if rc_list == []:
        return ""
    return _densest_region(rc_list).region.name


def _terrain_growth_rate(terrain: str) -> float:
    """Return the annual population growth rate for a terrain."""

    if terrain == "ocean":
        return 0.0001
    if terrain == "mountains":
        return 0.0005
    if terrain == "forest":
        return -0.00001
    return 0.0003


def _compound_growth_factor(rate: float, years: int) -> float:
    """Return compound growth factor after a non-negative number of years."""

    if years <= 0:
        return 1.0
    return (1.0 + rate) * _compound_growth_factor(rate, years - 1)


# Purpose: Return a new region condition projected forward by a number of years.
# Type: RegionCondition, int -> RegionCondition
def project_condition(rc: RegionCondition, years: int) -> RegionCondition:
    if years <= 0:
        return RegionCondition(
            region=rc.region,
            year=rc.year + years,
            pop=rc.pop,
            ghg_rate=rc.ghg_rate,
        )
    growth_rate = _terrain_growth_rate(rc.region.terrain)
    growth_factor = _compound_growth_factor(growth_rate, years)
    projected_pop = int(rc.pop * growth_factor)
    if rc.pop <= 0:
        projected_ghg_rate = 0.0
    else:
        projected_ghg_rate = rc.ghg_rate * (projected_pop / rc.pop)
    return RegionCondition(
        region=rc.region,
        year=rc.year + years,
        pop=projected_pop,
        ghg_rate=projected_ghg_rate,
    )
