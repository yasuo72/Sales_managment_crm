"""
generate_data.py — Synthetic Sales Data Generator (Improving Version 2.0)
Zudio Store Insight Engine (Retail Analytics Assignment)

Generates realistic September sales data (sales_data.csv) following the enhanced
16-column schema with bill_id grouping for basket and cross-selling analytics,
and embedding the 4 required intentional retail flaws plus audited retail dynamics:
1. Size M Stockout (Slim Fit Jeans runs out on Sept 13)
2. Slow-Moving Luxury & 3 Distinct Worst Sellers (Sherwani, Crop Top, Loafers)
3. Discount Trap (Accessories at 40-50% discount generate <5% of revenue)
4. Dead Tuesday (Tuesday, September 16 records only 1 sale of Rs. 399)
5. Festival Surges (Raksha Bandhan Sept 5-8 & Ganesh Chaturthi Sept 17-19)
6. Month-End Slump (Sept 24-30 salary exhaustion)
7. Rebalanced Size Proportions (M ~30%, L ~28%, S ~20%, XL ~15%, XS ~7%)
8. Footwear price floor >= Rs. 699 and full 4 store sections (Men, Women, Kids, Accessories)
"""

import csv
import datetime
import logging
import os
import random
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Fixed seed for 100% reproducibility
SEED = 42

# Product Catalog: (product_name, category, default_price, store_section, colors, allowed_sizes)
PRODUCTS = [
    # Tops (Rs. 399 - Rs. 799)
    ("Oversized Cotton T-Shirt", "Tops", 499, "Men", ["Black", "White", "Olive", "Charcoal"], ["S", "M", "L", "XL"]),
    ("Classic Polo T-Shirt", "Tops", 599, "Men", ["Navy Blue", "White", "Black"], ["S", "M", "L", "XL"]),
    ("Printed Crop Top", "Tops", 399, "Women", ["Pink", "Sky Blue", "White", "Mustard"], ["XS", "XL"]),  # Worst 2: Assortment size mismatch
    ("Linen Casual Shirt", "Tops", 799, "Men", ["White", "Sky Blue", "Olive"], ["M", "L", "XL"]),
    
    # Bottoms (Rs. 899 - Rs. 1,199)
    ("Slim Fit Jeans", "Bottoms", 999, "Men", ["Navy Blue", "Black", "Charcoal"], ["S", "M", "L", "XL"]),
    ("Wide Leg Denim", "Bottoms", 1199, "Women", ["Sky Blue", "Navy Blue", "Black"], ["XS", "S", "M", "L"]),
    ("Cotton Chinos", "Bottoms", 899, "Men", ["Olive", "Charcoal", "Navy Blue"], ["S", "M", "L", "XL"]),
    ("High-Rise Trousers", "Bottoms", 999, "Women", ["Black", "Olive", "Charcoal"], ["S", "M", "L"]),

    # Ethnic Wear (Rs. 699 - Rs. 1,799)
    ("Floral Kurti", "Ethnic Wear", 699, "Women", ["Red", "Mustard", "Pink", "White"], ["XS", "S", "M", "L", "XL"]),
    ("Anarkali Kurta Set", "Ethnic Wear", 1299, "Women", ["Red", "Mustard", "Emerald"], ["S", "M", "L", "XL"]),
    ("Cotton Kurta Pajama", "Ethnic Wear", 999, "Men", ["White", "Mustard", "Sky Blue"], ["M", "L", "XL"]),
    ("Embroidered Sherwani", "Ethnic Wear", 1799, "Men", ["Red", "Mustard"], ["M", "L", "XL"]),  # Worst 1: Luxury price disconnect

    # Footwear (Rs. 699 - Rs. 1,199) — Minimum price floor Rs. 699
    ("Casual White Sneakers", "Footwear", 899, "Men", ["White"], ["S", "M", "L", "XL"]),
    ("Ethnic Kolhapuri Chappals", "Footwear", 699, "Women", ["Mustard", "Red", "Black"], ["S", "M", "L"]),
    ("Slip-On Loafers", "Footwear", 1199, "Men", ["Black", "Navy Blue"], ["M", "L", "XL"]),  # Worst 3: Uncompetitive 0% discount

    # Accessories (Rs. 199 - Rs. 349) — Discount Trap
    ("Beaded Boho Earrings", "Accessories", 199, "Accessories", ["Red", "Mustard", "Sky Blue"], ["XS"]),
    ("Classic Leather Belt", "Accessories", 349, "Accessories", ["Black", "Charcoal"], ["M", "L", "XL"]),
    ("Printed Silk Scarf", "Accessories", 249, "Accessories", ["Pink", "Mustard", "Emerald"], ["S", "M"]),
]

AGE_GROUPS = ["Teen (13-19)", "Young Adult (20-30)", "Adult (31-45)", "Senior (46+)"]
PAYMENT_METHODS = ["UPI", "Card", "Cash"]


def calculate_total_amount(quantity: int, price: int, discount: int) -> float:
    """Calculate total amount accurately rounded to 2 decimal places."""
    return round(quantity * price * (1 - discount / 100.0), 2)


def generate_sales_dataset(year: int = 2025, target_rows: int = 205) -> List[Dict[str, Any]]:
    """
    Generate synthetic sales dataset for September with realistic retail dynamics,
    multi-item basket grouping via bill_id, and the 4 required intentional retail flaws.
    """
    random.seed(SEED)
    rows: List[Dict[str, Any]] = []
    bill_counter = 1

    prod_map = {p[0]: p for p in PRODUCTS}
    standard_pool = [p for p in PRODUCTS if p[0] not in ["Embroidered Sherwani", "Printed Crop Top", "Slip-On Loafers"]]

    kids_assigned = 0
    target_kids_rows = 5
    days_in_september = 30

    for day in range(1, days_in_september + 1):
        curr_date = datetime.date(year, 9, day)
        date_str = curr_date.strftime("%Y-%m-%d")
        day_of_week = curr_date.strftime("%A")

        # Intentional Flaw 4: Dead Tuesday (Tuesday, September 16, 2025)
        # Exactly 1 bill with 1 sale of Rs. 399
        if day == 16:
            item = prod_map["Printed Crop Top"]
            bill_id = f"B{bill_counter:03d}"
            bill_counter += 1
            rows.append({
                "bill_id": bill_id,
                "date": date_str,
                "day_of_week": day_of_week,
                "product_name": item[0],
                "category": item[1],
                "size": "XS",
                "color": "Pink",
                "quantity_sold": 1,
                "price (Rs.)": item[2],
                "discount (%)": 0,
                "total_amount (Rs.)": 399.0,
                "price": item[2],
                "discount": 0,
                "total_amount": 399.0,
                "payment_method": "UPI",
                "customer_gender": "Female",
                "age_group": "Young Adult (20-30)",
                "store_section": "Women",
            })
            continue

        # Calendar period markers
        is_weekend = day_of_week in ["Saturday", "Sunday"]
        is_salary_rush = 1 <= day <= 7
        is_fest_rb = 5 <= day <= 8       # Raksha Bandhan surge
        is_fest_gc = 17 <= day <= 19     # Ganesh Chaturthi surge
        is_festival = is_fest_rb or is_fest_gc
        is_month_end = 24 <= day <= 30    # Month-end salary exhaustion

        # Daily bill count determination
        if is_month_end:
            # Month-end slump: only 2-3 bills/day, Saturday Sept 27 capped
            daily_bills = 3 if day == 27 else random.randint(2, 3)
        elif is_festival:
            daily_bills = random.randint(5, 7) if is_weekend else random.randint(4, 6)
        elif is_salary_rush:
            daily_bills = random.randint(5, 7) if is_weekend else random.randint(4, 6)
        elif is_weekend:
            daily_bills = random.randint(5, 7)
        else:
            daily_bills = random.randint(3, 5)

        for _ in range(daily_bills):
            bill_id = f"B{bill_counter:03d}"
            bill_counter += 1

            # Bill-level customer profile
            if is_festival:
                pm = random.choices(["UPI", "Card", "Cash"], weights=[65, 22, 13], k=1)[0]
            else:
                pm = random.choices(["UPI", "Card", "Cash"], weights=[60, 24, 16], k=1)[0]

            gender = random.choices(["Female", "Male", "Other"], weights=[55, 43, 2], k=1)[0]
            age_grp = random.choices(AGE_GROUPS, weights=[15, 48, 25, 12], k=1)[0]

            # Basket size breakdown: ~60% single-item, ~30% 2-item, ~10% 3-item
            item_count = random.choices([1, 2, 3], weights=[60, 30, 10], k=1)[0]
            bill_items = []

            for item_idx in range(item_count):
                if item_idx == 0:
                    weights = []
                    for p in standard_pool:
                        name, cat, price, sec, cols, szs = p
                        w = 8.0 if cat == "Accessories" else 12.0
                        # Core volume bestsellers
                        if name in ["Slim Fit Jeans", "Oversized Cotton T-Shirt", "Floral Kurti"]:
                            w += 22.0
                            if name == "Slim Fit Jeans" and day <= 12:
                                w += 28.0  # Heavy early-month denim rush
                        elif name in ["Classic Polo T-Shirt", "Cotton Chinos", "Wide Leg Denim", "Anarkali Kurta Set"]:
                            w += 8.0

                        # Festival category surge
                        if is_festival:
                            if cat == "Ethnic Wear":
                                w *= 3.0
                            elif cat == "Accessories":
                                w *= 1.8
                            elif cat == "Footwear" and name == "Ethnic Kolhapuri Chappals":
                                w *= 2.5
                            else:
                                w *= 0.5

                        if is_salary_rush and cat in ["Bottoms", "Tops"]:
                            w *= 1.6

                        weights.append(w)
                    chosen_prod = random.choices(standard_pool, weights=weights, k=1)[0]

                elif item_idx == 1:
                    # Natural retail cross-selling associations
                    prev_cat = bill_items[0]["category"]
                    if prev_cat == "Bottoms":
                        if random.random() < 0.85:
                            candidates = [p for p in standard_pool if p[1] == "Tops"]
                        else:
                            candidates = [p for p in standard_pool if p[0] == "Classic Leather Belt"]
                    elif prev_cat == "Ethnic Wear":
                        candidates = [p for p in standard_pool if p[0] == "Ethnic Kolhapuri Chappals" or p[1] in ["Ethnic Wear", "Accessories"]]
                    elif prev_cat == "Tops":
                        if random.random() < 0.85:
                            candidates = [p for p in standard_pool if p[1] == "Bottoms"]
                        else:
                            candidates = [p for p in standard_pool if p[1] == "Accessories"]
                    else:
                        candidates = standard_pool
                    chosen_prod = random.choice(candidates)

                else:
                    # Item 3: Impulse purchase (Accessories 50%, lightweight Top or Footwear 50%)
                    if random.random() < 0.5:
                        candidates = [p for p in standard_pool if p[1] == "Accessories"]
                    else:
                        candidates = [p for p in standard_pool if p[1] in ["Tops", "Footwear"]]
                    chosen_prod = random.choice(candidates)

                prod_name, category, base_price, def_sec, colors, allowed_sizes = chosen_prod

                # Intentional Flaw 1: Size M Stockout for Slim Fit Jeans from Sept 13 onwards
                if prod_name == "Slim Fit Jeans":
                    if day <= 12:
                        size = random.choices(["M", "L", "S", "XL"], weights=[80, 10, 6, 4], k=1)[0]
                    else:
                        # Stocked out of Size M! Exactly 0 sales of Size M
                        size = random.choices(["L", "S", "XL"], weights=[50, 26, 24], k=1)[0]
                else:
                    # Tuned size selection: M ~30-32%, L ~26-28%, S ~19-21%, XL ~14-16%, XS ~7-8%
                    if set(allowed_sizes) == {"S", "M", "L", "XL"}:
                        size = random.choices(["M", "L", "S", "XL"], weights=[30, 28, 24, 18], k=1)[0]
                    elif set(allowed_sizes) == {"XS", "S", "M", "L", "XL"}:
                        size = random.choices(["M", "L", "S", "XL", "XS"], weights=[28, 26, 24, 16, 6], k=1)[0]
                    elif set(allowed_sizes) == {"S", "M", "L"}:
                        size = random.choices(["M", "L", "S"], weights=[38, 34, 28], k=1)[0]
                    elif set(allowed_sizes) == {"M", "L", "XL"}:
                        size = random.choices(["M", "L", "XL"], weights=[38, 34, 28], k=1)[0]
                    else:
                        size = random.choice(allowed_sizes)

                color = random.choice(colors)
                qty = random.choices([1, 2, 3], weights=[82, 15, 3], k=1)[0]
                if category == "Accessories":
                    qty = random.choices([1, 2, 3], weights=[70, 22, 8], k=1)[0]

                # Intentional Flaw 3: Accessories Discount Trap (40-50% discount strictly)
                if category == "Accessories":
                    discount = random.choice([40, 50])
                elif is_salary_rush:
                    discount = random.choices([0, 10], weights=[75, 25], k=1)[0]
                elif is_festival:
                    discount = random.choices([0, 10, 20], weights=[45, 35, 20], k=1)[0]
                elif is_month_end:
                    # Controlled month-end apparel discounts (no 30-50% markdowns on apparel)
                    discount = random.choices([0, 10, 20], weights=[50, 35, 15], k=1)[0]
                else:
                    discount = random.choices([0, 10, 20], weights=[55, 30, 15], k=1)[0]

                total_amount = calculate_total_amount(qty, base_price, discount)

                # Store Section: integrate "Kids" for Teen/youth apparel
                store_sec = def_sec
                if kids_assigned < target_kids_rows and age_grp == "Teen (13-19)" and category in ["Tops", "Bottoms"]:
                    store_sec = "Kids"
                    kids_assigned += 1

                item_dict = {
                    "bill_id": bill_id,
                    "date": date_str,
                    "day_of_week": day_of_week,
                    "product_name": prod_name,
                    "category": category,
                    "size": size,
                    "color": color,
                    "quantity_sold": qty,
                    "price (Rs.)": base_price,
                    "discount (%)": discount,
                    "total_amount (Rs.)": total_amount,
                    "price": base_price,
                    "discount": discount,
                    "total_amount": total_amount,
                    "payment_method": pm,
                    "customer_gender": gender,
                    "age_group": age_grp,
                    "store_section": store_sec,
                }
                bill_items.append(item_dict)
                rows.append(item_dict)

    # Controlled Deterministic Products: 3 Distinct Worst Sellers
    # 1. Flaw 2: Embroidered Sherwani (2 units, Luxury Price Rs. 1799)
    sherwani = prod_map["Embroidered Sherwani"]
    for date_str, dow, sz in [("2025-09-05", "Friday", "L"), ("2025-09-18", "Thursday", "XL")]:
        b_id = f"B{bill_counter:03d}"
        bill_counter += 1
        tot_amt = calculate_total_amount(1, sherwani[2], 10)
        rows.append({
            "bill_id": b_id, "date": date_str, "day_of_week": dow,
            "product_name": sherwani[0], "category": sherwani[1],
            "size": sz, "color": "Mustard", "quantity_sold": 1,
            "price (Rs.)": sherwani[2], "discount (%)": 10,
            "total_amount (Rs.)": tot_amt,
            "price": sherwani[2], "discount": 10,
            "total_amount": tot_amt,
            "payment_method": "Card", "customer_gender": "Male",
            "age_group": "Adult (31-45)", "store_section": "Men"
        })

    # 2. Flaw 2b: Printed Crop Top (3 units total, Flaw: Sizing Curve Mismatch XS & XL only)
    crop_top = prod_map["Printed Crop Top"]
    for date_str, dow, sz in [("2025-09-07", "Sunday", "XL"), ("2025-09-22", "Monday", "XS")]:
        b_id = f"B{bill_counter:03d}"
        bill_counter += 1
        tot_amt = calculate_total_amount(1, crop_top[2], 0)
        rows.append({
            "bill_id": b_id, "date": date_str, "day_of_week": dow,
            "product_name": crop_top[0], "category": crop_top[1],
            "size": sz, "color": "Sky Blue", "quantity_sold": 1,
            "price (Rs.)": crop_top[2], "discount (%)": 0,
            "total_amount (Rs.)": tot_amt,
            "price": crop_top[2], "discount": 0,
            "total_amount": tot_amt,
            "payment_method": "UPI", "customer_gender": "Female",
            "age_group": "Teen (13-19)", "store_section": "Women"
        })

    # 3. Flaw 2c: Slip-On Loafers (4 units total, Flaw: Uncompetitive 0% Discount)
    loafers = prod_map["Slip-On Loafers"]
    for date_str, dow, sz in [("2025-09-03", "Wednesday", "M"), ("2025-09-10", "Wednesday", "L"),
                              ("2025-09-14", "Sunday", "M"), ("2025-09-21", "Sunday", "XL")]:
        b_id = f"B{bill_counter:03d}"
        bill_counter += 1
        tot_amt = calculate_total_amount(1, loafers[2], 0)
        rows.append({
            "bill_id": b_id, "date": date_str, "day_of_week": dow,
            "product_name": loafers[0], "category": loafers[1],
            "size": sz, "color": "Navy Blue", "quantity_sold": 1,
            "price (Rs.)": loafers[2], "discount (%)": 0,
            "total_amount (Rs.)": tot_amt,
            "price": loafers[2], "discount": 0,
            "total_amount": tot_amt,
            "payment_method": "Card", "customer_gender": "Male",
            "age_group": "Young Adult (20-30)", "store_section": "Men"
        })

    # Sort rows strictly chronologically by date
    rows.sort(key=lambda r: r["date"])

    # Re-assign sequential bill_id strictly chronologically (B001 to B{N} with 0 jumps)
    # preserving multi-item basket groupings
    bill_mapping: Dict[str, str] = {}
    bill_counter = 1
    for r in rows:
        orig_b = r["bill_id"]
        if orig_b not in bill_mapping:
            bill_mapping[orig_b] = f"B{bill_counter:03d}"
            bill_counter += 1
        r["bill_id"] = bill_mapping[orig_b]

    # Assign sequential sale_id S001...
    for idx, r in enumerate(rows, start=1):
        r["sale_id"] = f"S{idx:03d}"

    return rows


def write_csv(rows: List[Dict[str, Any]], filepath: str) -> None:
    """Save rows to CSV matching PDF 16-column schema with units and bill_id."""
    fieldnames = [
        "bill_id", "sale_id", "date", "day_of_week", "product_name", "category",
        "size", "color", "quantity_sold", "price (Rs.)", "discount (%)",
        "total_amount (Rs.)", "payment_method", "customer_gender", "age_group", "store_section"
    ]
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"Successfully generated {len(rows)} sales records in '{filepath}'.")


def verify_generated_dataset(rows: List[Dict[str, Any]]) -> None:
    """Verify and assert statistics for intentional flaws, schema integrity, and tuning targets."""
    import pandas as pd
    df = pd.DataFrame(rows)

    logger.info("--- Dataset Verification Summary ---")
    logger.info(f"Total Rows: {len(df)}")
    assert len(df) >= 150, "Dataset must contain at least 150 rows!"
    assert "bill_id" in df.columns, "bill_id column must be present in dataset!"
    assert df["bill_id"].nunique() >= 100, "Must contain diverse unique bills!"

    # Verify bill_ids are strictly sequential (B001 to B{N}) without any non-sequential jumps
    unique_bills = list(dict.fromkeys(r["bill_id"] for r in rows))
    expected_bills = [f"B{i:03d}" for i in range(1, len(unique_bills) + 1)]
    assert unique_bills == expected_bills, f"bill_id sequence must be strictly sequential! Found: {unique_bills[:5]}...{unique_bills[-5:]}"
    logger.info(f"bill_id sequence verified: strictly sequential from {expected_bills[0]} to {expected_bills[-1]} ({len(expected_bills)} bills, 0 jumps).")

    # Verify unit-decorated columns matching PDF specification
    for col in ["price (Rs.)", "discount (%)", "total_amount (Rs.)"]:
        assert col in df.columns, f"Unit column '{col}' must be present in dataset!"
    logger.info("PDF unit columns verified: 'price (Rs.)', 'discount (%)', 'total_amount (Rs.)'.")

    # 1. Size M Stockout for Slim Fit Jeans
    jeans = df[df["product_name"] == "Slim Fit Jeans"]
    jeans_m = jeans[jeans["size"] == "M"]
    jeans_m_w12 = jeans_m[jeans_m["date"] <= "2025-09-12"]["quantity_sold"].sum()
    jeans_m_after = jeans_m[jeans_m["date"] > "2025-09-12"]["quantity_sold"].sum()
    jeans_other_after = jeans[(jeans["date"] > "2025-09-12") & (jeans["size"] != "M")]["quantity_sold"].sum()
    logger.info(f"Flaw 1 (Size M Stockout): Slim Fit Jeans (Size M) sold {jeans_m_w12} units Sept 1-12, and {jeans_m_after} units Sept 13-30 (Other sizes sold {jeans_other_after} units).")
    assert jeans_m_after == 0, "Size M Slim Fit Jeans must have 0 sales after Sept 12!"
    assert jeans_m_w12 >= 8, "Size M Slim Fit Jeans must have at least 8 sales before Sept 13!"

    # 2. Slow-Moving Products (3 Distinct Worst Sellers)
    sherwani_sales = df[df["product_name"] == "Embroidered Sherwani"]["quantity_sold"].sum()
    crop_top_sales = df[df["product_name"] == "Printed Crop Top"]["quantity_sold"].sum()
    loafers_sales = df[df["product_name"] == "Slip-On Loafers"]["quantity_sold"].sum()
    logger.info(f"Flaw 2 (Worst Sellers): Sherwani={sherwani_sales}, Crop Top={crop_top_sales}, Loafers={loafers_sales}")
    assert sherwani_sales == 2, "Embroidered Sherwani must sell exactly 2 units!"
    assert crop_top_sales <= 4, "Printed Crop Top must sell <= 4 units!"
    assert loafers_sales <= 5, "Slip-On Loafers must sell <= 5 units!"

    # 3. Discount Trap: Accessories
    total_rev = df["total_amount"].sum()
    acc_df = df[df["category"] == "Accessories"]
    acc_rev = acc_df["total_amount"].sum()
    acc_units = acc_df["quantity_sold"].sum()
    acc_pct = (acc_rev / total_rev) * 100
    acc_avg_disc = acc_df["discount"].mean()
    logger.info(f"Flaw 3 (Discount Trap): Accessories sold {acc_units} units ({acc_avg_disc:.1f}% avg discount) generating Rs. {acc_rev:.2f} ({acc_pct:.2f}% of total store revenue Rs. {total_rev:.2f}).")
    assert acc_pct < 5.0, "Accessories revenue contribution must be under 5%!"
    assert acc_avg_disc >= 40.0, "Accessories average discount must be at least 40%!"

    # 4. Dead Tuesday: September 16, 2025
    tue_16 = df[df["date"] == "2025-09-16"]
    tue_16_rev = tue_16["total_amount"].sum()
    logger.info(f"Flaw 4 (Dead Tuesday): Sept 16, 2025 transactions = {len(tue_16)}, total revenue = Rs. {tue_16_rev:.2f}")
    assert len(tue_16) == 1, "Tuesday Sept 16 must have exactly 1 transaction!"

    # 5. Footwear Price Floor
    min_footwear_price = df[df["category"] == "Footwear"]["price"].min()
    logger.info(f"Footwear min price: Rs. {min_footwear_price}")
    assert min_footwear_price >= 699, "Footwear minimum price must be >= Rs. 699!"

    # 6. Kids section presence
    kids_count = len(df[df["store_section"] == "Kids"])
    logger.info(f"Kids section row count: {kids_count}")
    assert kids_count >= 3, "Kids store section must contain at least 3 rows!"

    # 7. Month-End Slump
    me_df = df[(df["date"] >= "2025-09-24") & (df["date"] <= "2025-09-30")]
    me_avg_daily = len(me_df) / 7.0
    logger.info(f"Month-End (Sept 24-30) daily average rows: {me_avg_daily:.2f}")
    assert me_avg_daily < 5.0, "Month-end average daily transactions must be < 5.0!"


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "sales_data.csv")
    dataset = generate_sales_dataset()
    write_csv(dataset, output_path)
    verify_generated_dataset(dataset)
