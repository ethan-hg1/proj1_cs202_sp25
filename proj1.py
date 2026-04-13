from dataclasses import dataclass
from typing import Optional
from typing import TypeAlias


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