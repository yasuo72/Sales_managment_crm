"""
test_engine.py — Comprehensive Test Suite using standard library unittest
Zudio Store Insight Engine (AIML Internship Submission)
"""

import os
import unittest
import pandas as pd
from generate_data import generate_sales_dataset, write_csv, SEED
from insight_engine import (
    DataValidator, AnalyticsEngine, ChartGenerator,
    LLMInsightProvider, ReportCompiler, run_pipeline, REQUIRED_COLUMNS, PDF_HEADER_COLUMNS
)


class TestInsightEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = generate_sales_dataset()
        cls.df = pd.DataFrame(cls.dataset)

    def test_schema_and_row_count(self):
        """Verifies row count >= 150, presence of all columns including bill_id, and sequential bill_ids."""
        self.assertGreaterEqual(len(self.dataset), 150)
        for col in REQUIRED_COLUMNS:
            self.assertIn(col, self.df.columns, f"Missing required column: {col}")
        for col in PDF_HEADER_COLUMNS:
            self.assertIn(col, self.df.columns, f"Missing PDF unit column: {col}")
        self.assertEqual(self.df["sale_id"].nunique(), len(self.df), "sale_id values must be unique")
        self.assertGreaterEqual(self.df["bill_id"].nunique(), 100, "bill_id must group transactions into diverse baskets")

        # Verify chronological bill_id sequence has zero non-sequential jumps
        unique_bills = list(dict.fromkeys(self.df["bill_id"]))
        expected_bills = [f"B{i:03d}" for i in range(1, len(unique_bills) + 1)]
        self.assertEqual(unique_bills, expected_bills, "bill_id sequence must be strictly sequential (B001...B{N})")

        # Verify sales_data.csv on disk contains the exact PDF schema with units
        csv_path = "sales_data.csv"
        if os.path.exists(csv_path):
            csv_df = pd.read_csv(csv_path)
            for col in PDF_HEADER_COLUMNS:
                self.assertIn(col, csv_df.columns, f"sales_data.csv must contain PDF header column: {col}")
            cleaned_csv_df, summary = DataValidator.validate_and_clean(csv_df)
            self.assertEqual(len(cleaned_csv_df), len(csv_df), "All CSV rows must be successfully validated")

    def test_intentional_flaws(self):
        """Verifies all engineered business flaws and audited retail benchmarks."""
        df = self.df

        # Flaw 1: Size M Stockout
        jeans = df[df["product_name"] == "Slim Fit Jeans"]
        jeans_m_early = jeans[(jeans["size"] == "M") & (jeans["date"] <= "2025-09-12")]["quantity_sold"].sum()
        jeans_m_late = jeans[(jeans["size"] == "M") & (jeans["date"] > "2025-09-12")]["quantity_sold"].sum()
        self.assertGreater(jeans_m_early, 0)
        self.assertEqual(jeans_m_late, 0)

        # Flaw 2: Slow-Moving Luxury and 3 Distinct Worst Sellers
        sherwani_sales = df[df["product_name"] == "Embroidered Sherwani"]["quantity_sold"].sum()
        crop_top_sales = df[df["product_name"] == "Printed Crop Top"]["quantity_sold"].sum()
        loafers_sales = df[df["product_name"] == "Slip-On Loafers"]["quantity_sold"].sum()
        self.assertEqual(sherwani_sales, 2)
        self.assertLessEqual(crop_top_sales, 4)
        self.assertLessEqual(loafers_sales, 5)

        # Verify crop top sizes are fringe only (XS & XL)
        crop_sizes = set(df[df["product_name"] == "Printed Crop Top"]["size"])
        self.assertTrue(crop_sizes.issubset({"XS", "XL"}))

        # Verify loafers discount is strictly 0%
        loafers_discounts = set(df[df["product_name"] == "Slip-On Loafers"]["discount"])
        self.assertEqual(loafers_discounts, {0})

        # Flaw 3: Discount Trap
        acc_df = df[df["category"] == "Accessories"]
        acc_share = (acc_df["total_amount"].sum() / df["total_amount"].sum()) * 100
        self.assertLess(acc_share, 5.0)
        self.assertGreater(acc_df["discount"].mean(), 40.0)

        # Flaw 4: Dead Tuesday (Sept 16)
        tue_16 = df[df["date"] == "2025-09-16"]
        self.assertEqual(len(tue_16), 1)
        self.assertEqual(tue_16.iloc[0]["total_amount"], 399.0)

        # Footwear minimum price floor >= 699
        self.assertGreaterEqual(df[df["category"] == "Footwear"]["price"].min(), 699)

        # Kids store section presence
        self.assertGreaterEqual((df["store_section"] == "Kids").sum(), 3)

        # Month-end slump
        me_df = df[(df["date"] >= "2025-09-24") & (df["date"] <= "2025-09-30")]
        self.assertLess(len(me_df) / 7.0, 5.0)

    def test_basket_metrics_and_cross_selling(self):
        """Verifies basket intelligence, UPT, and cross-selling calculations."""
        engine = AnalyticsEngine(self.df)
        basket = engine._basket_metrics()
        self.assertIn("upt", basket)
        self.assertIn("aov", basket)
        self.assertIn("multi_item_tx_percentage", basket)
        self.assertGreater(basket["upt"], 1.0)
        self.assertGreater(basket["total_bills"], 100)
        self.assertGreater(len(basket["top_cross_sell_pairs"]), 0)

    def test_data_validator_repair(self):
        """Tests validator cleans discrepancies."""
        test_df = pd.DataFrame([
            {
                "bill_id": "B001",
                "sale_id": "S001",
                "date": "2025-09-01",
                "day_of_week": "Friday",  # Intentionally wrong weekday
                "product_name": "Slim Fit Jeans",
                "category": "Bottoms",
                "size": "M",
                "color": "Navy Blue",
                "quantity_sold": 1,
                "price": 1000,
                "discount": 10,
                "total_amount": 999.0,  # Intentionally wrong math (should be 900.0)
                "payment_method": "UPI",
                "customer_gender": "Male",
                "age_group": "Young Adult (20-30)",
                "store_section": "Men"
            }
        ])
        cleaned_df, summary = DataValidator.validate_and_clean(test_df)
        self.assertGreater(summary["repaired_rows"], 0)
        self.assertEqual(cleaned_df.iloc[0]["day_of_week"], "Monday")
        self.assertEqual(cleaned_df.iloc[0]["total_amount"], 900.0)

    def test_short_note_word_count(self):
        """Verifies short_note.md is strictly within 100-150 words."""
        self.assertTrue(os.path.exists("short_note.md"))
        with open("short_note.md", "r", encoding="utf-8") as f:
            text = f.read()
        words = [w for w in text.split() if not w.startswith("#")]
        self.assertTrue(100 <= len(words) <= 150, f"Word count {len(words)} is outside the 100-150 range!")

    def test_end_to_end_pipeline(self):
        """Verifies that full pipeline executes successfully and generates outputs."""
        exit_code = run_pipeline(input_file="sales_data.csv", output_file="store_report.md", no_llm=True)
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists("store_report.md"))
        self.assertTrue(os.path.exists("output/top_products.png"))


if __name__ == "__main__":
    unittest.main()
