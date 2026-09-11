# PLAN.md — Zudio Store Insight Engine

> **Project Goal:** Build a production-quality retail analytics pipeline that generates a realistic September fashion-store dataset, calculates deterministic business metrics using Pandas, uses an LLM as a semantic reasoning layer, and produces actionable insights that a store manager can understand and use.

---

# 1. Project Objective

The **Zudio Store Insight Engine** simulates a real fashion retail store environment.

The system will:

1. Generate realistic synthetic September sales data.
2. Intentionally introduce realistic business patterns and problems.
3. Validate and sanitize the dataset.
4. Calculate reliable business metrics using Pandas.
5. Detect important sales patterns before sending information to the LLM.
6. Build a compact, structured context for the LLM.
7. Ask the LLM the 5 core business questions plus 3 High-Value Operational Extensions (Q6 Basket Size/Cross-Selling via bill_id, Q7 Weekend Sale Clearance, Q8 Week-on-Week Salary-Cycle Trend).
8. Validate the LLM response and prevent unsupported claims.
9. Generate a clean Markdown report covering Q1 through Q8, What to Avoid, and Bilingual Summaries (English & Hindi).
10. Optionally compile the report into PDF with charts.
11. Provide a real-time Web CRM Copilot with 1-click floating quick chips for English Briefing, Hindi Briefing, and Q6-Q8.
12. Gracefully fall back to deterministic Python insights if the LLM API fails.

### Core engineering principle

> **Pandas determines what happened. The LLM explains why it may matter and what the manager should do next.**

The LLM must never be treated as the source of truth for numerical calculations.

---

# 2. Assignment Requirements

The implementation must satisfy the original assignment requirements.

## Required Deliverables

```text
sales_data.csv
insight_engine.py
store_report.md OR store_report.pdf
short_note.md
```

The dataset must contain **at least 150 rows**.

The main program must run with:

```bash
python insight_engine.py
```

The final report must be understandable by a non-technical store manager.

---

# 3. High-Level Architecture

```text
                  ┌──────────────────────┐
                  │ Synthetic Data       │
                  │ Generator            │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ CSV Sales Dataset    │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Validation &         │
                  │ Sanitization        │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Pandas Analytics     │
                  │ Engine               │
                  └──────────┬───────────┘
                             │
                    Structured Metrics
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Context Builder      │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ LLM Insight Provider │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ JSON Validation &    │
                  │ Evidence Checking    │
                  └──────────┬───────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │ Markdown Report │       │ Chart Generator │
       └────────┬────────┘       └────────┬────────┘
                │                         │
                └────────────┬────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Final PDF/MD    │
                    └─────────────────┘
```

---

# 4. Streamlined & Evaluator-Friendly Project Structure

The project is kept clean, lightweight, and directly aligned with the 4 submission deliverables required in the assignment PDF:

```text
Sales-Managment_CRM/
│
├── sales_data.csv          # Deliverable 1: Synthetic sales dataset (180–220 rows)
├── generate_data.py        # Python script to generate sales_data.csv (reproducible SEED=42)
├── insight_engine.py       # Deliverable 2: End-to-end analytics, LLM query, chart, and report runner
├── store_report.md         # Deliverable 3: Final manager-ready report (answering Q1–Q5 + bonuses)
├── short_note.md           # Deliverable 4: 100–150 word reflection answering the 4 PDF prompts
├── requirements.txt        # Minimal dependencies: pandas, matplotlib, python-dotenv, google-genai
├── .env.example            # Environment template for LLM API key
├── README.md               # Quick setup and run instructions
└── output/
    └── top_products.png    # Bonus: Matplotlib bar chart of best-selling products
```

The evaluator can test everything with:

```bash
python generate_data.py
python insight_engine.py
```

---

# 5. Environment & Dependency Setup

## Recommended approach

Use:

```text
Python 3.11+
venv
requirements.txt
python-dotenv
```

Poetry is acceptable, but it is not necessary for this assignment.

A simple evaluator-friendly setup is preferable.

## Core dependencies

```text
pandas
numpy
matplotlib
python-dotenv
pydantic
pytest
```

Add the selected LLM SDK and PDF/Markdown libraries only when needed.

## Environment variables

Use:

```text
.env
```

Example:

```text
LLM_API_KEY=your_api_key_here
LLM_MODEL=your_model_name
```

Never hard-code API keys.

Include:

```text
.env
__pycache__/
.venv/
output/
*.pyc
```

in `.gitignore` where appropriate.

Provide:

```text
.env.example
```

without real credentials.

---

# 6. Synthetic Data Engineering Strategy

The dataset should look intentionally realistic rather than randomly generated.

## Minimum

```text
150+ rows (prefer 180–220 rows for rich statistical distribution)
```

Each row represents one item sold in the store (like a billing register row), strictly following the enhanced 16 columns (with `bill_id` and units) requested in the assignment PDF.

## Mandatory Columns (Strict Assignment Schema with Units & Basket bill_id)

| Column Name        | What it means                                                     |
| ------------------ | ----------------------------------------------------------------- |
| bill_id            | Unique bill identifier grouping multi-item baskets (`B001`...`B136` sequential) |
| sale_id            | A unique number for each sale line item (`S001`...`S193` sequential) |
| date               | The date when the item was sold (YYYY-MM-DD in September 2025)   |
| day_of_week        | Monday, Tuesday, Wednesday... etc.                                |
| product_name       | Name of the item sold (e.g. Slim Fit Jeans, Floral Kurti)         |
| category           | Type of item — Tops, Bottoms, Ethnic Wear, Footwear, Accessories |
| size               | XS, S, M, L, XL                                                   |
| color              | Color of the item (e.g. Navy Blue, White, Red, Black, Olive)      |
| quantity_sold      | How many pieces were sold in this transaction                     |
| price (Rs.)        | Selling price per piece in Rupees (exact PDF specification)       |
| discount (%)       | Discount given — 0%, 10%, 20%, 30%, 50%                           |
| total_amount (Rs.) | Final amount paid after discount (`quantity * price * (1-d/100)`) |
| payment_method     | Cash, UPI, or Card                                                |
| customer_gender    | Male, Female, or Other                                            |
| age_group          | Teen (13-19), Young Adult (20-30), Adult (31-45), Senior (46+)    |
| store_section      | Men, Women, Kids, or Accessories                                  |

---

# 7. Synthetic Market Scenario

The dataset represents a **September retail scenario in India**.

Any festival effects used in the dataset should be treated as **simulation assumptions**, not claims about actual historical sales data.

The purpose is to create meaningful correlations that the analytics engine can discover.

---

# 8. Engineered Business Patterns

The generator should intentionally create several patterns.

## 8.1 Strong Products

Create 2–3 clear best-selling products.

Example:

```text
Anarkali Kurta Set
Slim Fit Jeans
Floral Kurti
```

These should naturally appear near the top after aggregation.

Do not simply force their rankings after analytics.

---

# 8. Engineered Retail Patterns & Intentional Flaws

The generator combines **realistic retail drivers** (salary cycles, festivals, month-end clearance) with the **4 specific intentional flaws** highlighted on Page 2 of the assignment PDF:

### Retail Driver 1: Salary-Cycle Effect (Sept 1–7)
* Higher customer footfall and purchasing power in the first week.
* Full-price or low-discount sales across core Western and Formal wear.

### Retail Driver 2: Festival Shopping Surge (Raksha Bandhan & Ganesh Chaturthi)
* Spike in Ethnic Wear (Floral Kurtis, Kurtas), Footwear, and Accessories.
* Women and Young Adult segments lead the surge.
* UPI becomes the dominant payment method (62%+).

### Retail Driver 3: Month-End Salary Exhaustion Slump (Sept 24–30)
* Natural retail footfall dip to ~4.14 transactions/day due to monthly salary exhaustion.

---

### The 4 Intentional Flaws (Explicit Marking Criteria)

The PDF states: *"Do NOT make everything perfect. A good dataset has some problems — slow-selling items, one size that keeps running out, a discount section that barely makes money, a Tuesday where almost nobody came. These problems are what the AI will find and explain."*

1. **Flaw 1: The Size M Stockout (Navy Blue Slim Fit Jeans):**
   * High demand in Weeks 1 & 2 (9 units sold).
   * From September 13 onwards, Size M records **0 sales** because it ran out of stock, while Sizes S, L, and XL continue selling (15 units).
2. **Flaw 2: 3 Distinct Worst Sellers with Separate Failure Hypotheses:**
   * *Embroidered Sherwani*: Luxury Price Barrier — ₹1,799 price point (double Zudio's impulse sweet spot), recording only 2 units all month.
   * *Printed Crop Top*: Assortment Sizing Curve Mismatch — Stocked only in fringe sizes (XS & XL, 0 core M/L), starving core Indian female demand (only 3 units sold).
   * *Slip-On Loafers*: Uncompetitive Zero Discount — Rigid 0% markdown at ₹1,199 while competing footwear alternatives captured buyer interest (only 4 units sold).
3. **Flaw 3: The Discount Trap (Accessories Section):**
   * Heavy discounts (40%–50%, avg 45.2%) on items like Earrings and Belts.
   * 49 units sold, but total revenue contribution is only 4.22% of store revenue (< 5% threshold).
4. **Flaw 4: The Dead Tuesday (Tuesday, September 16, 2025):**
   * Unusually dead day with exactly 1 transaction (₹399), contrasting sharply with Saturday peaks (₹31,728).

---

# 10. Pricing Strategy

Use realistic synthetic price ranges.

| Category    | Example Range |
| ----------- | ------------: |
| Tops        |     ₹399–₹799 |
| Bottoms     |    ₹799–₹1499 |
| Ethnic Wear |    ₹599–₹1799 |
| Footwear    |    ₹699–₹1999 |
| Accessories |     ₹199–₹599 |

Prices should not be completely random.

Assign products their own normal price ranges.

---

# 11. Festival Scenario

Create synthetic seasonal effects around the selected September festival windows.

For the simulation:

### Raksha Bandhan scenario

Increase:

```text
Accessories
Ethnic Wear
Kids
```

### Ganesh Chaturthi scenario

Increase:

```text
Ethnic Wear
Footwear
Women
```

These effects should be implemented through weighted generation rather than manually inserting rows.

---

# 12. Salary-Cycle Simulation

Create a mild synthetic salary-cycle effect.

Example:

```text
September 1–7:
Higher purchasing activity

September 24–30:
Slightly lower purchasing activity
```

Do not make this effect so strong that it overwhelms the festival/day-of-week patterns.

---

# 13. Payment Distribution

Use approximate synthetic proportions:

```text
UPI   ≈ 55–60%
Card  ≈ 25–30%
Cash  ≈ 15–20%
```

During simulated festival periods, increase UPI usage slightly.

The exact values should vary rather than being identical on every day.

---

# 14. Discount Strategy

Normal days:

```text
0–10%
```

Festival periods:

```text
20–50%
```

Accessories:

```text
30–50%
```

The dataset should allow the analytics layer to identify that a heavily discounted section may generate volume without being especially strong in revenue efficiency.

Important:

Since the dataset does not contain product cost/margin, the system should **not claim actual profit**.

Instead use terms such as:

```text
discount-heavy
revenue efficiency
sales volume vs discount
```

If margin analysis is required later, add a `cost_price` field.

---

# 15. Slow Tuesday Scenario

Create one deliberately weak Tuesday in the second half of the month.

The day should contain approximately:

```text
1–2 transactions
```

This provides a clear signal for the weekday analysis.

The analytics engine should discover the result naturally.

---

# 16. Reproducibility

Use deterministic random generation:

```python
SEED = 42
```

Running:

```bash
python generate_data.py
```

multiple times should produce the same dataset unless a new seed is deliberately selected.

---

# 17. Data Validation Layer

Before analytics, validate the CSV.

## Validation checks

### IDs

* `sale_id` must be unique.
* Missing IDs should be rejected.

### Dates

* Valid date format.
* Date must fall inside the simulated September period.

### Categories

Allowed values:

```text
Tops
Bottoms
Ethnic Wear
Footwear
Accessories
```

### Sizes

```text
XS
S
M
L
XL
```

### Quantity

```text
quantity_sold > 0
```

### Price

```text
price > 0
```

### Discount

```text
0 <= discount <= 50
```

### Total Amount

Validate:

```text
total_amount =
quantity_sold × price × (1 - discount / 100)
```

Use a small floating-point tolerance when comparing values.

### Day of Week

Recalculate `day_of_week` from `date`.

If the provided value differs, either repair it or flag the row.

---

# 18. Data Sanitization Policy

Not every error should automatically be deleted.

Classify problems as:

```text
REPAIRABLE
INVALID
CRITICAL
```

Examples:

### Repairable

Incorrect weekday derived from a valid date.

### Invalid

Negative quantity.

### Critical

Missing required columns.

Produce a validation summary:

```text
Rows loaded: 220
Rows repaired: 3
Rows rejected: 2
Rows analyzed: 215
```

---

# 19. Pandas Analytics Layer

Pandas owns all numerical calculations.

The LLM receives summaries rather than raw calculations.

---

## 19.1 Product Analytics

Calculate:

* units sold
* revenue
* transaction count
* average discount
* average selling price

Produce:

```text
top 3 products
bottom 3 products
```

Rank primarily by units sold, while also showing revenue.

---

# 20. Size Analytics

Calculate:

* total units by size
* percentage of units
* product × size demand
* size/category demand

Identify:

```text
high-demand sizes
low-demand sizes
```

If inventory/availability data exists, detect actual stockout events.

Otherwise describe the result as:

```text
high-demand / potentially constrained size
```

rather than a confirmed stockout.

---

# 21. Weekday Analytics

Calculate:

* revenue
* quantity sold
* transaction count
* average transaction value

Group by:

```text
Monday
Tuesday
Wednesday
Thursday
Friday
Saturday
Sunday
```

Identify:

```text
busiest day
slowest day
```

Compare Tuesday against the overall daily average.

---

# 22. Customer Buying Pattern Analytics

Use cross-tabulations such as:

```text
age_group × gender × category
age_group × gender × product
store_section × category
```

Do not send every possible combination to the LLM.

First identify meaningful patterns.

A pattern should ideally have:

* sufficient sample size
* clear difference from the overall baseline
* meaningful business interpretation

Avoid calling a 1-transaction segment an important trend.

---

# 23. Discount Analysis

Calculate:

```text
category
average discount
units sold
revenue
```

Compare discount-heavy categories against normal categories.

Do not calculate profit unless cost data exists.

Possible insight:

> Accessories received much deeper discounts but contributed less revenue than major apparel categories.

This is a defensible observation.

---

# 24. Festival vs Normal Period Analysis

Create a derived field:

```text
period_type
```

Examples:

```text
Normal
Festival A
Festival B
```

Compare:

* revenue
* units
* category mix
* payment methods
* average discount

This helps determine whether the synthetic festival patterns actually appear in the resulting dataset.

---

# 24.1 Week-on-Week (WoW) Sales Dynamics

Break September into 4 operational weeks:
* **Week 1 (Sept 1–7):** Salary rush window, high footfall, full-price velocity.
* **Week 2 (Sept 8–14):** Mid-month stabilization, steady baseline.
* **Week 3 (Sept 15–21):** Festival ramp-up (Ganesh Chaturthi / Raksha Bandhan), ethnic wear & accessories surge.
* **Week 4 (Sept 22–30):** Month-end clearance window, discount-driven volume.

Calculate:
* WoW revenue growth rate (%)
* WoW units sold velocity
* Emerging vs declining categories across weekly shifts

---

# 24.2 Basket Size & Cross-Selling Analytics

Group by `transaction_id` to evaluate register and cashier performance:
* **Units Per Transaction (UPT / Basket Size):** Average items per bill.
* **Average Order Value (AOV):** Revenue per completed bill.
* **Basket Distribution:** 1-item bills vs multi-item bills (2+ items).
* **Cross-Category Affinity:** Frequency of co-purchased categories (e.g. Bottoms + Tops basket incidence rate, Apparel + Accessories impulse attachment).

---

# 24.3 Dead Stock & Markdown Radar

Identify capital chokepoints and stagnant inventory:
* Products with cumulative sales ≤ 2 units across the entire month.
* Stagnant products with high discounts (>25%) failing to clear.
* Flag as **DEAD_STOCK_WARNING** with floor action: Reallocate prime rack space to high-velocity lines, move dead stock to 50% discount bins or entrance value tables.

---

# 24.4 Stockout Urgency & Replenishment Flag

Pragmatic stockout inference for store replenishment:
* Compare SKU-size daily run-rate across Weeks 1–2 vs Weeks 3–4.
* If a high-volume SKU-size (top 20% in W1–W2) records zero sales in the second half while adjacent sizes remain active, tag as:
  * `STOCKOUT_PROBABILITY: HIGH`
  * `REPLENISHMENT_URGENCY: CRITICAL`
* Quantify estimated lost sales volume based on baseline run-rate.

---

# 25. Analytics Output Contract

The analytics layer should produce a structured object similar to:

```json
{
  "dataset": {
    "rows": 240,
    "unique_transactions": 175,
    "date_range": "September"
  },
  "products": {
    "top_3": [],
    "bottom_3": []
  },
  "sizes": {
    "distribution": {},
    "top_combos": []
  },
  "weekdays": {
    "busiest_day": {},
    "slowest_day": {},
    "daily_breakdown": {}
  },
  "weekly_trends": {
    "week_on_week": [],
    "velocity_shifts": []
  },
  "basket_analytics": {
    "upt": 1.45,
    "aov": 890.50,
    "multi_item_ratio": 0.35,
    "top_cross_sell_pairs": []
  },
  "dead_stock_alerts": [],
  "stockout_risk_flags": [],
  "customer_patterns": [],
  "discount_analysis": {},
  "festival_comparison": {}
}
```

This object becomes the main source of truth for the LLM.

---

# 26. LLM Context Engineering

## Main Principle

Do not send the entire CSV to the model by default.

Instead send:

```text
validated business metrics
+
important comparisons
+
detected patterns
+
simulation context
```

This reduces token usage and hallucination risk.

---

# 27. LLM System Role

The model should behave as:

> An experienced retail business analyst helping a store manager understand September sales performance.

It must:

* use simple English
* be specific
* use numbers from the provided context
* never invent metrics
* distinguish facts from assumptions
* avoid unsupported claims
* provide practical recommendations

---

# 28. Five Required LLM Questions

## Q1 — Product Performance

Ask:

* Which 3 products sold the most?
* Which 3 sold the least?
* Give numerical evidence.
* For each weak product, provide one plausible explanation.
* Clearly label explanations as hypotheses when they are not directly proven.

---

## Q2 — Size Performance

Ask:

* Which sizes have the highest demand?
* Which sizes are slow?
* Which product-size combinations show unusually high demand?
* Which sizes should be prioritized for replenishment?

If no inventory data exists, do not claim confirmed stockouts.

---

## Q3 — Weekday Performance

Ask:

* Which day generated the highest revenue?
* Which day generated the lowest revenue?
* How far below/above the average was the slowest day?
* Should the store run a promotion?
* What type of promotion would be appropriate?

---

## Q4 — Customer Buying Patterns

Ask for at least two non-obvious patterns.

Requirements:

* include supporting numbers
* avoid tiny sample sizes
* explain why the pattern matters

---

## Q5 — Three Actions

Generate exactly three specific actions.

Each action must contain:

```text
Action
Evidence
Expected business purpose
```

Example structure:

```text
1. Restock...
   Evidence: ...
   Why: ...
```

Avoid:

```text
Improve marketing.
Increase sales.
Focus on customers.
```

---

# 29. Structured LLM Response

Prefer JSON over free-form text.

Example:

```json
{
  "product_insight": {
    "best_sellers": [],
    "slow_sellers": []
  },
  "size_and_stockout_insight": {
    "high_demand_sizes": [],
    "low_demand_sizes": [],
    "stockout_alerts": []
  },
  "weekday_insight": {
    "busiest_day": {},
    "slowest_day": {}
  },
  "weekly_trend_insight": {
    "salary_rush_impact": "",
    "festival_ramp_impact": ""
  },
  "basket_cross_sell_insight": {
    "upt_analysis": "",
    "cross_selling_opportunities": []
  },
  "dead_stock_recommendations": [],
  "customer_patterns": [],
  "recommended_actions": []
}
```

Validate the response using Pydantic or equivalent schema validation.

---

# 30. LLM Error Handling

Handle:

* missing API key
* timeout
* rate limit
* provider error
* empty response
* malformed JSON
* markdown-wrapped JSON
* missing required fields
* unexpected response structure

Use bounded retries.

Example:

```text
Attempt 1
   ↓
Invalid response?
   ↓
Attempt 2
   ↓
Still invalid?
   ↓
Deterministic fallback
```

Never retry indefinitely.

---

# 31. Evidence Validation

After receiving the LLM response, validate its claims against the analytics context.

The system should prevent:

```text
LLM says revenue = ₹50,000
Python says revenue = ₹38,000
```

from appearing in the final report.

Numerical values should come from Python-generated context whenever possible.

The LLM should primarily provide:

```text
interpretation
reasoning
recommendations
```

---

# 32. Deterministic Fallback

If the LLM is unavailable:

```bash
python insight_engine.py
```

must still complete successfully.

Generate a fallback report containing:

* top products
* slow products
* size demand
* busiest/slowest day
* customer patterns
* three rule-based recommendations

Clearly state:

```text
AI commentary was unavailable; insights below were generated from deterministic sales analytics.
```

This is preferable to crashing the entire application.

---

# 33. LLM Provider Abstraction

Avoid hard-coding the application around one provider.

Use a simple abstraction:

```python
class InsightProvider:
    def generate_insights(self, context):
        raise NotImplementedError
```

Then implement the selected provider separately.

This allows the project to change models without rewriting the analytics/reporting layers.

---

# 34. Visualization Engine

Generate only useful charts.

Recommended:

### Chart 1

Top 10 products by units sold.

### Chart 2

Revenue by weekday.

### Chart 3

Units sold by size.

### Chart 4

Revenue by category.

Store them under:

```text
output/charts/
```

Use clear titles, labels, and readable sizing.

Do not create charts merely for decoration.

---

# 35. Store Report Structure (`store_report.md`)

The final report directly answers the **5 mandatory assignment questions** plus the **Page 4 bonus questions**, written in clean, professional, non-technical manager language:

```text
# September Store Performance Report — Zudio Store Operations

## Executive Summary
(Quick 3-4 sentence manager overview: total revenue, units sold, key wins, and critical warnings)

## 1. Product Performance (Question 1)
- Top 3 Best-Selling Products (units, revenue, color/price details)
- Bottom 3 Worst-Selling Products (with specific, grounded hypotheses: price, size, discount)

## 2. Size Analysis & Stockout Detection (Question 2)
- High-demand sizes vs slow-moving sizes
- Explicit identification of the Size M stockout anomaly
- Recommendations: which sizes to order more of, which were over-ordered

## 3. Day-of-Week Performance & Slow Tuesday Strategy (Question 3)
- Busiest day vs slowest day (revenue & transaction difference)
- Clear recommendation: Should the store run a Tuesday offer? What specific promotion?

## 4. Customer Buying Patterns (Question 4)
- Pattern 1: Age group / Gender buying preferences (with supporting data)
- Pattern 2: Category & Payment method trend (e.g. UPI adoption in ethnic wear)

## 5. Priority Action Plan for Next Week (Question 5)
- Action 1: Specific restocking directive with evidence
- Action 2: Mid-week footfall stimulation directive with evidence
- Action 3: Merchandise/display or markdown directive with evidence

## 6. What to Avoid (Page 4 Bonus)
- Things the store should stop doing (e.g. stop 50% accessory discounts that erode value)

## 7. Weekend Sale Recommendation (Page 4 Bonus)
- Which specific item to put on sale this upcoming weekend and why

## 8. Hindi Executive Summary (Page 4 Bonus)
- Short bilingual Hindi summary for floor staff and supervisors
```

---

# 36. Executive Summary

The first section should answer:

```text
How did the store perform?
What went well?
What went wrong?
What should the manager focus on?
```

Keep this short.

Do not dump raw tables into the opening section.

---

# 37. PDF Generation

PDF generation is optional but recommended for presentation quality.

The pipeline should be:

```text
Analytics
   ↓
Validated LLM JSON
   ↓
Markdown Report
   ↓
Charts
   ↓
PDF Compiler
```

If PDF compilation fails, the Markdown report should still be produced.

---

# 38. CLI Design

Minimum:

```bash
python insight_engine.py
```

Optional:

```bash
python insight_engine.py --input data/sales_data.csv
python insight_engine.py --output output/store_report.md
python insight_engine.py --no-llm
```

The default execution path should remain simple.

---

# 39. Logging

Use Python's `logging` module.

Log:

```text
Dataset loaded
Validation completed
Rows repaired/rejected
Analytics completed
LLM request started
LLM retry
LLM fallback activated
Charts generated
Report generated
```

Never log:

```text
API keys
secrets
private credentials
```

---

# 40. Testing Strategy

Use `pytest`.

## Data validation tests

Test:

* duplicate sale IDs
* negative quantities
* invalid prices
* invalid discounts
* missing required columns
* invalid categories
* invalid sizes
* incorrect weekdays
* incorrect total amounts

---

# 41. Analytics Tests

Test:

* top 3 ranking
* bottom 3 ranking
* size aggregation
* weekday aggregation
* revenue calculation
* average discount
* customer segmentation
* festival comparison

Use small deterministic fixtures.

---

# 42. LLM Tests

Do not make real API calls inside normal unit tests.

Mock the provider.

Test:

* valid JSON
* malformed JSON
* missing fields
* empty response
* timeout
* provider failure
* retry
* fallback

---

# 43. Evidence Validation Tests

Create a fake LLM response containing an incorrect number.

Example:

```text
Python revenue: ₹40,000
LLM revenue: ₹55,000
```

The validator must reject or correct the unsupported claim.

---

# 44. End-to-End Acceptance Test

Run:

```bash
python generate_data.py
python insight_engine.py
```

Verify:

```text
sales_data.csv exists
row count >= 150
validation succeeds
analytics succeeds
LLM succeeds OR fallback activates
charts are generated
store_report.md exists
PDF exists if enabled
```

---

# 45. Synthetic Pattern Acceptance

The generated dataset should demonstrate the intended patterns.

Verify:

* [ ] Best-selling products appear in expected high-demand range.
* [ ] Slow products remain visibly weaker.
* [ ] High-demand sizes rank highly.
* [ ] Low-demand sizes remain visible.
* [ ] The engineered slow Tuesday is detected.
* [ ] Festival periods show the intended category shift.
* [ ] Discount-heavy categories are detectable.
* [ ] Payment distribution is reasonably realistic.
* [ ] Salary-cycle effect is present but not overwhelming.

---

# 46. Quality Rules for LLM Insights

Every important insight should answer:

```text
WHAT happened?
WHY might it matter?
WHAT should the manager do?
```

Weak:

> Jeans are popular.

Strong:

> Slim Fit Jeans sold 42 units, the highest of all products. Demand was particularly strong for size M, so replenishing M should be prioritized.

If the reason cannot be proven:

> A possible reason is the product's lower price compared with other Bottoms, although the dataset does not contain customer preference data to confirm this.

---

# 47. Hallucination Prevention

The LLM must not invent:

* sales numbers
* inventory levels
* customer counts
* profit
* margins
* stockouts without evidence
* external market statistics

When information is unavailable, it must explicitly say so.

---

# 48. Important Analytical Limitation

The required transaction dataset does not inherently contain:

```text
opening inventory
closing inventory
stock received
stockout timestamp
profit margin
customer footfall
conversion rate
```

Therefore the system must not pretend to know these values.

For example:

### Supported

> Size M had the highest observed sales volume.

### Potential inference

> Size M may require higher replenishment.

### Not directly supported

> Size M was out of stock five times.

Unless actual inventory/availability events exist in the dataset.

---

# 49. Optional Advanced Extension

If time permits, extend the synthetic dataset with:

```text
inventory_before
inventory_after
stock_received
cost_price
customer_id
transaction_id
```

This would allow:

* true stockout detection
* margin analysis
* repeat-customer analysis
* inventory turnover
* profitability analysis

These should remain optional because they are not required by the assignment.

---

# 50. Short Note

Create:

```text
short_note.md
```

Keep it between **100–150 words**.

Explain:

1. What was asked from the AI.
2. What initially went wrong.
3. How the prompt/data pipeline was improved.
4. What would be added with more time.

The note should demonstrate that the LLM was iteratively improved rather than blindly accepted.

---

# 51. Final Acceptance Checklist

## Dataset

* [ ] At least 150 rows.
* [ ] All mandatory columns present.
* [ ] Unique sale IDs.
* [ ] Realistic products and prices.
* [ ] Realistic discounts.
* [ ] Good and bad sales periods.
* [ ] Strong and weak products.
* [ ] Size demand variation.
* [ ] Slow Tuesday exists.
* [ ] Festival effects are detectable.
* [ ] Payment distribution is realistic.

## Data Quality

* [ ] Missing values handled.
* [ ] Invalid values detected.
* [ ] Duplicate IDs handled.
* [ ] Total amount verified.
* [ ] Day of week verified.
* [ ] Validation summary generated.

## Analytics

* [ ] Top 3 products.
* [ ] Bottom 3 products.
* [ ] Size analysis.
* [ ] Stockout urgency anomaly detection.
* [ ] Weekday analysis (including slow Tuesday).
* [ ] Week-on-Week (WoW) velocity trends.
* [ ] Basket size (UPT & AOV) and cross-selling pairs.
* [ ] Dead stock & markdown radar alerts.
* [ ] Customer buying patterns.
* [ ] Discount analysis.
* [ ] Festival comparison.

## LLM

* [ ] Specific prompts used.
* [ ] All five assignment questions answered.
* [ ] Structured JSON response.
* [ ] Response schema validated.
* [ ] Numerical claims grounded in Python data.
* [ ] No unsupported stockout/profit claims (inferences clearly labelled).
* [ ] Retry handling implemented.
* [ ] API failure fallback implemented.

## Report

* [ ] Manager-friendly language.
* [ ] Executive summary.
* [ ] Specific insights with supporting evidence.
* [ ] Stockout and dead stock alerts clearly highlighted.
* [ ] Three actionable recommendations.
* [ ] Charts included.
* [ ] Markdown generated.
* [ ] PDF generated if enabled.
* [ ] Report remains usable if LLM fails.

## Code

* [ ] `python insight_engine.py` works.
* [ ] Configuration uses `.env`.
* [ ] Secrets are not committed.
* [ ] Logging implemented.
* [ ] Unit tests pass.
* [ ] End-to-end test passes.
* [ ] Code is modular and readable.

---

# 52. Definition of Done

The project is considered complete when a reviewer can clone the repository, configure the LLM API key, run:

```bash
python insight_engine.py
```

and receive a clean manager-ready report containing:

1. The three strongest products.
2. The three weakest products with plausible explanations.
3. Size demand, stockout velocity anomalies, and replenishment priorities.
4. Busiest and slowest days with Week-on-Week (WoW) velocity trends.
5. Basket size (UPT), AOV, and register cross-selling opportunities.
6. Dead stock alerts with clear markdown recommendations.
7. At least two meaningful customer buying patterns.
8. Three specific actions for the following week.
9. Supporting charts.
10. Clear distinction between facts and AI-generated hypotheses.
11. Safe behavior when the LLM API fails.

The final implementation should demonstrate that this is not simply a CSV-to-LLM demo.

It should demonstrate a complete analytics workflow:

```text
Reliable Data
      ↓
Deterministic Analytics
      ↓
Structured Context
      ↓
Grounded LLM Reasoning
      ↓
Validation
      ↓
Actionable Business Report
```

> **Final Principle:** Think like a store manager, engineer like a data professional, and use the LLM where language reasoning adds value—not where deterministic computation is more reliable.
