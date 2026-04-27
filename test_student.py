import unittest
import math
from proj1 import *


class TestStudentRegionFunctions(unittest.TestCase):
    ny_condition: RegionCondition
    syd_condition: RegionCondition
    catalina_condition: RegionCondition
    slo_condition: RegionCondition

    def setUp(self) -> None:
        self.ny_condition = region_conditions[0]
        self.syd_condition = region_conditions[1]
        self.catalina_condition = region_conditions[2]
        self.slo_condition = region_conditions[3]

        self.ny_rect = self.ny_condition.region.rect
        self.syd_rect = self.syd_condition.region.rect
        self.catalina_rect = self.catalina_condition.region.rect
        self.slo_rect = self.slo_condition.region.rect

    def test_region_conditions_has_four_examples(self) -> None:
        self.assertEqual(len(region_conditions), 4)
        self.assertIsInstance(region_conditions[0], RegionCondition)
        self.assertIsInstance(region_conditions[1], RegionCondition)
        self.assertIsInstance(region_conditions[2], RegionCondition)
        self.assertIsInstance(region_conditions[3], RegionCondition)

    def test_region_conditions_contains_slo_example(self) -> None:
        self.assertEqual(
            region_conditions[3].region.name,
            "San Luis Obispo County / Cal Poly region"
        )
        self.assertEqual(region_conditions[3].region.terrain, "other")

    def test_region_conditions_contains_catalina_example(self) -> None:
        self.assertEqual(
            region_conditions[2].region.name,
            "Southern California Bight near Catalina"
        )
        self.assertEqual(region_conditions[2].region.terrain, "ocean")

    def test_emissions_per_capita_new_york(self) -> None:
        expected = 80000000.0 / 20000000
        self.assertAlmostEqual(
            emissions_per_capita(self.ny_condition),
            expected,
            places=7
        )

    def test_emissions_per_capita_sydney(self) -> None:
        expected = 20000000.0 / 5000000
        self.assertAlmostEqual(
            emissions_per_capita(self.syd_condition),
            expected,
            places=7
        )

    def test_emissions_per_capita_zero_population(self) -> None:
        self.assertEqual(emissions_per_capita(self.catalina_condition), 0.0)

    def test_area_matches_full_sphere_for_whole_globe(self) -> None:
        whole_globe = GlobeRect(-90.0, 90.0, -180.0, 180.0)
        expected = 4.0 * math.pi * (EARTH_RADIUS_KM ** 2)
        self.assertAlmostEqual(area(whole_globe), expected, places=5)

    def test_area_handles_date_line_wraparound(self) -> None:
        wrapped_rect = GlobeRect(10.0, 20.0, 170.0, -170.0)
        longitude_width = math.radians(20.0)
        latitude_height = math.sin(math.radians(20.0)) - math.sin(math.radians(10.0))
        expected = (EARTH_RADIUS_KM ** 2) * longitude_width * latitude_height
        self.assertAlmostEqual(area(wrapped_rect), expected, places=5)

    def test_area_is_same_when_latitudes_are_reversed(self) -> None:
        normal_rect = GlobeRect(35.6, 35.0, -120.9, -120.2)
        reversed_rect = GlobeRect(35.0, 35.6, -120.9, -120.2)
        self.assertAlmostEqual(area(normal_rect), area(reversed_rect), places=7)

    def test_emissions_per_square_km_positive_area_new_york(self) -> None:
        expected = self.ny_condition.ghg_rate / area(self.ny_rect)
        self.assertAlmostEqual(
            emissions_per_square_km(self.ny_condition),
            expected,
            places=7
        )

    def test_emissions_per_square_km_positive_area_slo(self) -> None:
        expected = self.slo_condition.ghg_rate / area(self.slo_rect)
        self.assertAlmostEqual(
            emissions_per_square_km(self.slo_condition),
            expected,
            places=7
        )

    def test_emissions_per_square_km_positive_area_zero_population_region(self) -> None:
        expected = self.catalina_condition.ghg_rate / area(self.catalina_rect)
        self.assertAlmostEqual(
            emissions_per_square_km(self.catalina_condition),
            expected,
            places=7
        )

    def test_emissions_per_square_km_zero_area(self) -> None:
        point_rect = GlobeRect(35.0, 35.0, -120.0, -120.0)
        point_region = Region(point_rect, "Point", "other")
        point_condition = RegionCondition(point_region, 2024, 100, 500.0)
        self.assertEqual(emissions_per_square_km(point_condition), 0.0)

    def test_densest_empty_list_returns_empty_string(self) -> None:
        self.assertEqual(densest([]), "")

    def test_densest_returns_expected_example_region(self) -> None:
        densities = [
            (rc.region.name, rc.pop / area(rc.region.rect) if area(rc.region.rect) != 0 else float("inf"))
            for rc in region_conditions
        ]
        expected_name = max(densities, key=lambda pair: pair[1])[0]
        self.assertEqual(densest(region_conditions), expected_name)

    def test_densest_prefers_zero_area_positive_population(self) -> None:
        point_region = Region(GlobeRect(1.0, 1.0, 2.0, 2.0), "Point City", "other")
        point_condition = RegionCondition(point_region, 2024, 10, 1.0)
        self.assertEqual(densest([self.slo_condition, point_condition]), "Point City")

    def test_project_condition_uses_other_growth_rate_on_slo(self) -> None:
        projected = project_condition(self.slo_condition, 10)
        projected_pop = int(300000 * ((1.0003) ** 10))
        expected_ghg = 1000000.0 * (projected_pop / 300000)

        self.assertEqual(projected.year, 2034)
        self.assertEqual(projected.pop, projected_pop)
        self.assertAlmostEqual(projected.ghg_rate, expected_ghg, places=7)
        self.assertEqual(projected.region, self.slo_condition.region)

    def test_project_condition_uses_ocean_growth_rate_on_catalina(self) -> None:
        projected = project_condition(self.catalina_condition, 5)
        projected_pop = int(0 * ((1.0001) ** 5))

        self.assertEqual(projected.year, 2029)
        self.assertEqual(projected.pop, projected_pop)
        self.assertEqual(projected.ghg_rate, 0.0)
        self.assertEqual(projected.region, self.catalina_condition.region)

    def test_project_condition_preserves_values_when_years_is_zero(self) -> None:
        projected = project_condition(self.ny_condition, 0)

        self.assertEqual(projected.year, self.ny_condition.year)
        self.assertEqual(projected.pop, self.ny_condition.pop)
        self.assertEqual(projected.ghg_rate, self.ny_condition.ghg_rate)
        self.assertEqual(projected.region, self.ny_condition.region)

    def test_project_condition_negative_years_keeps_population_and_emissions(self) -> None:
        projected = project_condition(self.syd_condition, -2)

        self.assertEqual(projected.year, 2022)
        self.assertEqual(projected.pop, self.syd_condition.pop)
        self.assertEqual(projected.ghg_rate, self.syd_condition.ghg_rate)
        self.assertEqual(projected.region, self.syd_condition.region)

    def test_project_condition_zero_population_sets_zero_emissions(self) -> None:
        projected = project_condition(self.catalina_condition, 3)
        self.assertEqual(projected.pop, 0)
        self.assertEqual(projected.ghg_rate, 0.0)


if __name__ == "__main__":
    unittest.main()