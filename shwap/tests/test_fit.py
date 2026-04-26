import unittest

from shwap.utils.fit import evaluate_fit


class TestFitEvaluation(unittest.TestCase):
    def test_likely_fit(self):
        result = evaluate_fit(
            garment={"chest_bust": 40.0, "waist": 32.0, "hip": 40.0, "inseam": 30.0},
            profile={"chest_bust": 39.0, "waist": 31.5, "hip": 39.5, "inseam": 30.5},
        )
        self.assertEqual(result["fit_result"], "Likely fits")

    def test_unlikely_fit(self):
        result = evaluate_fit(
            garment={"chest_bust": 34.0, "waist": 27.0, "hip": 35.0, "inseam": 26.0},
            profile={"chest_bust": 42.0, "waist": 36.0, "hip": 43.0, "inseam": 33.0},
        )
        self.assertEqual(result["fit_result"], "Unlikely to fit")

    def test_manual_review_when_missing_measurements(self):
        result = evaluate_fit(garment={}, profile={})
        self.assertEqual(result["fit_result"], "Needs manual review")


if __name__ == "__main__":
    unittest.main()
