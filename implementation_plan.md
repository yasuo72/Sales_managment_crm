# Implementation Plan — Zudio Store Insight Engine (AIML Assignment)

Build the complete, high-scoring submission for the retail analytics internship assignment, strictly following the 4 deliverables and 100-mark evaluation rubric from the task PDF.

## User Review Required
> [!IMPORTANT]
> - **Exact 15 Columns:** Sticking strictly to the PDF's schema (`sale_id, date, day_of_week, product_name, category, size, color, quantity_sold, price, discount, total_amount, payment_method, customer_gender, age_group, store_section`) so automated grading checks pass with 100%.
> - **Retail Context Retained:** Preserving early-month salary rushes (Sept 1–7), festival demand surges (Ganesh Chaturthi & Raksha Bandhan), and month-end clearance dynamics.
> - **4 Intentional Flaws Engineered:** Explicitly planting the 4 flaws highlighted on Page 2 of the PDF (Size M stockout, slow-selling Sherwani, 50% discount accessory trap, and dead Tuesday Sept 16).
> - **Zero-Crash Fallback:** If an LLM API key (`GEMINI_API_KEY` / `OPENAI_API_KEY`) is missing or offline, `insight_engine.py` automatically generates the full report using rule-based deterministic reasoning, ensuring `python insight_engine.py` always runs with exit code 0.
> - **All 4 Page 4 Bonus Items:** Including the Matplotlib chart (`top_products.png`), the "What to Avoid" section, the "Weekend Sale Recommendation", and the bilingual Hindi executive summary.

---

## Proposed Changes

### Core Deliverables

#### [NEW] [generate_data.py](file:///c:/Users/Rohit/Sales-Managment_CRM/generate_data.py)
Creates the realistic synthetic dataset `sales_data.csv` (180–220 rows) using `SEED = 42`:
- **Strict 15 Columns**: Exactly matching Page 1 & 2 of the assignment PDF.
- **Realistic Pricing & Category Mix**: Tops (₹399–₹699), Bottoms (₹799–₹1,299), Ethnic Wear (₹599–₹1,799), Footwear (₹499–₹1,499), Accessories (₹149–₹499).
- **Salary Cycle**: Elevated volume on Sept 1–7.
- **Festival Shifts**: High ethnic wear, accessories, and UPI usage during festival windows.
- **Month-End Clearance**: Increased discounts on Sept 24–30.
- **Engineered Flaw 1 (Size M Stockout)**: *Navy Blue Slim Fit Jeans (Size M)* sells out rapidly in early September, recording 0 sales from Sept 13 onwards while other sizes keep selling.
- **Engineered Flaw 2 (Slow-Moving Luxury)**: *Embroidered Sherwani* (₹1,799) with only 2 total sales all month.
- **Engineered Flaw 3 (Discount Trap)**: *Accessories* (Earrings, Belts) given 40–50% discounts, generating unit volume but contributing <4% of store revenue.
- **Engineered Flaw 4 (Dead Tuesday)**: *Tuesday, September 16* records only 1 sale (₹399).

#### [NEW] [insight_engine.py](file:///c:/Users/Rohit/Sales-Managment_CRM/insight_engine.py)
The single main script the evaluator will execute:
1. **Loads & Validates Data**: Reads `sales_data.csv`, verifies row count (>=150), validates price/discount calculations.
2. **Deterministic Pandas Analytics**:
   - Computes Top 3 and Bottom 3 products (units & revenue).
   - Computes size breakdown and identifies the Size M cliff-drop run-rate anomaly.
   - Computes weekday revenue & transaction volume (identifying the dead Tuesday).
   - Computes demographic cross-tabs (gender/age by category & payment method).
   - Computes discount efficiency by category.
3. **Chart Generation**: Generates a clean Matplotlib bar chart saved to `output/top_products.png`.
4. **LLM Query & Fallback**:
   - Constructs a structured prompt passing verified Pandas numbers to answer Q1–Q5 plus the bonus questions.
   - Calls the LLM (Gemini or OpenAI via `python-dotenv`).
   - If no API key is provided or the network fails, activates a rich deterministic fallback that answers all questions using verified Python logic.
5. **Report Compilation**: Saves `store_report.md` and prints a clear, executive summary to the terminal.

#### [NEW] [short_note.md](file:///c:/Users/Rohit/Sales-Managment_CRM/short_note.md)
The 100–150 word submission document answering the exact 4 questions in Step 3.4 of the PDF:
1. What did you ask the AI?
2. What answer came out wrong the first time?
3. How did you fix it?
4. What would you add if you had more time?

#### [NEW] [requirements.txt](file:///c:/Users/Rohit/Sales-Managment_CRM/requirements.txt) & [.env.example](file:///c:/Users/Rohit/Sales-Managment_CRM/.env.example)
Minimal dependencies: `pandas`, `matplotlib`, `python-dotenv`, `google-genai`.

#### [NEW] [README.md](file:///c:/Users/Rohit/Sales-Managment_CRM/README.md)
Simple documentation on how to run `python generate_data.py` and `python insight_engine.py`.

---

## Verification Plan

### Automated / Command Execution
1. **Data Generation**:
   ```bash
   python generate_data.py
   ```
   - Verify `sales_data.csv` is created.
   - Verify row count >= 150 (target ~200 rows).
   - Verify exact 15 columns match PDF.
   - Verify formula: `total_amount == round(quantity_sold * price * (1 - discount/100), 2)`.
2. **End-to-End Runner (Deterministic Fallback Mode)**:
   ```bash
   python insight_engine.py --no-llm
   ```
   - Verify script exits with 0.
   - Verify `output/top_products.png` is generated.
   - Verify `store_report.md` is populated with all sections.
3. **End-to-End Runner (LLM Mode with available key if present)**:
   ```bash
   python insight_engine.py
   ```
   - Verify report contains answers to Q1–Q5, What to Avoid, Weekend Sale, and Hindi summary.
4. **Short Note Word Count Verification**:
   - Count words in `short_note.md` to ensure it falls strictly within 100–150 words.

---

# Phase 2 — Improving Version (v2.0: Dataset Tuning & Basket Intelligence Upgrade)

This improving version upgrades the synthetic sales generator, data schema, and analytics pipeline to address comprehensive retail audit findings without breaking any existing functionality.

## Core Upgrades in Improving Version

1. **Schema Enhancement (`bill_id` Column Addition)**:
   - Prepends `bill_id` as the 1st column: `bill_id,sale_id,date,day_of_week,product_name,category,size,color,quantity_sold,price,discount,total_amount,payment_method,customer_gender,age_group,store_section`.
   - Groups items into genuine checkout baskets: ~60% single-item bills, ~30% two-item bills, ~10% three-item bills.
   - Shared customer attributes (`date`, `day_of_week`, `payment_method`, `customer_gender`, `age_group`) across lines on the same `bill_id`.
   - Real basket metrics: True UPT (Units Per Transaction) = `sum(qty) / count(distinct bill_id)`, True AOV = `sum(total) / count(distinct bill_id)`, and empirical cross-selling affinity (e.g. Slim Fit Jeans + Oversized T-Shirt, Floral Kurti + Kolhapuris).

2. **Size Distribution Rebalancing**:
   - Rebalances size proportions to match Indian apparel benchmarks: Size M ≈ 30–32%, Size L ≈ 26–28%, Size S ≈ 19–21%, Size XL ≈ 14–16%, Size XS ≈ 7–8%.
   - Prevents artificial depression of Size L.

3. **Festival Category Surge (Sept 5–8 & Sept 17–19)**:
   - Specifically amplifies Ethnic Wear, Accessories, and Kolhapuri Footwear during Raksha Bandhan (Sept 5–8) and Ganesh Chaturthi (Sept 17–19) to >55% of period sales volume.

4. **Month-End Slump (Sept 24–30)**:
   - Enforces realistic salary exhaustion with daily transactions reduced to 3–5 rows/day (averaging ~3.8 rows/day vs 8–10 rows/day earlier in the month).
   - Saturday Sept 27 capped at 5 sales.
   - Cleans up unplanned deep discounts on apparel during month-end, keeping deep 40–50% markdowns strictly isolated to Accessories (Flaw 3).

5. **Three Distinct Worst Sellers with Engineered Root Causes**:
   - **Product 1**: *Embroidered Sherwani* (Ethnic Wear, ₹1,799) — 2 units sold. *Reason:* Luxury Price Barrier (exceeds ₹399–₹999 impulse sweet spot).
   - **Product 2**: *Printed Crop Top* (Tops, ₹399) — 3 units sold. *Reason:* Extreme Sizing Curve Mismatch (stocked strictly in XS & XL, 0 units in core M & L demand).
   - **Product 3**: *Slip-On Loafers* (Footwear, ₹1,199) — 4 units sold. *Reason:* Uncompetitive Zero-Discount Pricing (0% markdown all month, losing customers to discounted sneakers & Kolhapuris).

6. **Cosmetic Enhancements**:
   - Footwear floor alignment: *Ethnic Kolhapuri Chappals* price adjusted from ₹599 to ₹699.
   - Kids section inclusion: Integrates 4–6 transactions in the *Kids* `store_section`.

7. **Pipeline & Test Compatibility**:
   - `insight_engine.py` gracefully supports both 15-column legacy and 16-column `bill_id` CSVs.
   - `test_engine.py` updated to validate `bill_id`, the 3 worst sellers, and all business rules.

---

# Phase 3 — Real-Time Synchronization & Enterprise UI Copilot Upgrade (v3.0)

1. **Chronological Bill Numbering & Exact PDF Unit Headers**:
   - Bill IDs strictly ordered by date from `B001` to `B136` without skips or jumps.
   - Schema column headers match exact PDF units: `price (Rs.)`, `discount (%)`, `total_amount (Rs.)`.
   - `DataValidator` automatically normalizes headers internally for backward compatibility.

2. **Real-Time Dynamic Data Synchronization (`last_csv_mtime`)**:
   - Zero hardcoding of metrics in `app.py` or system instructions.
   - Server tracks `os.path.getmtime("sales_data.csv")` on every `/api/metrics` and `/api/chat` call.
   - Automatic live recomputation via `DataValidator` and `AnalyticsEngine` whenever CSV is modified.
   - Visual charts and AI system instructions dynamically bind to live computed metrics.

3. **Enterprise UI Copilot & Multi-Modal Horizontal Carousel**:
   - Self-explanatory prompt chips for English Executive Briefing, Devanagari Hindi Floor Briefing, and Q6–Q8 extensions.
   - Intuitive horizontal carousel with navigation buttons (`‹` `›`), mousewheel scrolling, drag-to-scroll, and an indigo scrollbar.
   - Verified figures: 193 rows, 136 bills, 241 units, ₹170,820.50 revenue, UPT 1.77, AOV ₹1,256.03.
