# CLAUDE.md — Zudio Store Insight Engine

## 1. Project Context

You are working on **Zudio Store Insight Engine**, a production-quality retail analytics project based on a synthetic September fashion-store sales dataset.

The system must:

1. Generate or consume realistic sales data.
2. Validate and sanitize the dataset.
3. Calculate deterministic business metrics using Pandas.
4. Build structured analytical context.
5. Send only relevant metrics/context to an LLM.
6. Receive structured JSON insights.
7. Validate the LLM response.
8. Fall back to deterministic Python insights when the LLM is unavailable.
9. Generate a clean manager-facing Markdown report.
10. Optionally generate a PDF with charts.

The project is an internship-level assignment, so prioritize **clean engineering and practical reliability over unnecessary enterprise complexity**.

---

# 2. Source of Truth

Before implementing anything, read:

```text
PLAN.md
```

`PLAN.md` defines the intended architecture, requirements, dataset strategy, analytics, LLM behavior, testing strategy, and acceptance criteria.

Do not silently redesign the architecture unless there is a clear technical reason.

If an implementation detail is missing from `PLAN.md`, choose the simplest production-appropriate solution.

---

# 3. Core Engineering Principle

The most important rule in this project is:

> **Pandas determines what happened. The LLM explains why it may matter and what the manager should do next.**

Never use the LLM as the primary calculator.

The following must be calculated deterministically in Python:

* revenue
* quantity
* rankings
* percentages
* averages
* weekday totals
* product totals
* size totals
* category totals
* discount statistics
* customer segment statistics
* festival comparisons

The LLM should primarily handle:

* interpretation
* explanation
* hypothesis generation
* business recommendations
* natural-language reporting

---

# 4. Do Not Over-Engineer

This is not a distributed production SaaS platform.

Do NOT introduce unnecessary:

* microservices
* Kubernetes
* message queues
* databases
* authentication systems
* REST APIs
* Docker orchestration
* background workers
* cloud infrastructure

unless explicitly requested.

A clean local Python application is sufficient.

---

# 5. Python Standards

Use:

```text
Python 3.11+
```

Prefer:

* type hints
* clear function names
* small functions
* docstrings for important modules/functions
* meaningful variable names
* standard logging
* exception handling at system boundaries

Avoid:

* giant functions
* duplicated calculations
* hard-coded business logic scattered throughout the project
* unnecessary global state
* unexplained magic numbers

---

# 6. Dependency Management

Prefer:

```text
venv + requirements.txt
```

over introducing a more complicated dependency system unless there is a specific reason.

Expected core dependencies include:

```text
pandas
numpy
matplotlib
python-dotenv
pydantic
pytest
```

Add an LLM SDK and PDF-generation dependency only when required.

Keep dependencies minimal.

---

# 7. Environment Variables

Never hard-code API credentials.

Use:

```text
.env
```

Example:

```text
LLM_API_KEY=...
LLM_MODEL=...
```

Provide:

```text
.env.example
```

with placeholder values.

Never print API keys in logs or reports.

Never commit `.env`.

---

# 8. Dataset Rules

The synthetic dataset must contain at least **150 rows**.

Required columns:

```text
sale_id
transaction_id
date
day_of_week
product_name
category
size
color
quantity_sold
price
discount
total_amount
payment_method
customer_gender
age_group
store_section
```

The data must intentionally contain realistic variation.

Include:

* strong products
* slow products
* high-demand sizes
* slow-moving sizes
* a weak Tuesday
* discount-heavy products/categories
* different customer buying patterns
* seasonal/festival variation
* realistic payment-method distribution

Use deterministic random generation.

Recommended:

```python
SEED = 42
```

---

# 9. Do Not Fake Analytics

Do not manually force the final Pandas results to produce predetermined rankings.

For example, do NOT write:

```python
top_products = ["Slim Fit Jeans", ...]
```

just because the plan expects Slim Fit Jeans to perform well.

Instead, design the data-generation probabilities so that the expected behavior naturally appears when the analytics are calculated.

The purpose is to demonstrate that the analytics engine actually discovers the patterns.

---

# 10. Stockout Handling

Be precise about stockouts.

Transaction data alone cannot prove that a product was physically out of stock.

For example:

```text
No Slim Fit Jeans M sales after September 15
```

does NOT automatically mean:

```text
Slim Fit Jeans M was out of stock.
```

It could also mean that nobody purchased it.

Therefore:

* If inventory/availability data exists, detect actual stockouts.
* If it does not, describe the result as high observed demand or a potential replenishment constraint.

Never fabricate inventory events.

---

# 11. Profit/Margin Handling

Do not claim actual profit or margin unless cost information exists.

The required dataset contains selling price and discount but does not necessarily contain cost price.

Therefore acceptable statements include:

```text
high discount
low revenue efficiency
discount-heavy category
strong sales volume despite discounts
```

Avoid:

```text
This category made only ₹500 profit.
```

unless cost data exists.

If margin analysis is later required, introduce a `cost_price` field.

---

# 12. Data Validation

Validate the dataset before analytics.

Check:

* required columns
* duplicate IDs
* missing values
* invalid dates
* invalid categories
* invalid sizes
* invalid quantities
* invalid prices
* invalid discounts
* incorrect weekdays
* incorrect total amounts

The total amount should follow:

```text
quantity_sold × price × (1 - discount / 100)
```

Use appropriate floating-point tolerance.

---

# 13. Sanitization

Do not automatically delete every problematic row.

Classify issues as:

```text
repairable
invalid
critical
```

Examples:

```text
Incorrect day_of_week
→ repair from date

Negative quantity
→ reject

Missing required column
→ fail fast
```

Always log validation results.

---

# 14. Pandas Analytics

Create reusable analytics functions.

At minimum calculate:

### Products

* units sold
* revenue
* transaction count
* average discount
* top 3
* bottom 3

### Sizes

* units by size
* percentage by size
* product × size demand

### Weekdays

* revenue
* units
* transaction count
* average transaction value

### Customers

* age group
* gender
* category
* product
* meaningful cross-segment patterns

### Categories

* revenue
* units
* average discount

### Festival/Normal

* revenue
* units
* category mix
* average discount
* payment distribution

### Week-on-Week (WoW) Dynamics

* 4 operational weeks breakdown
* WoW revenue growth % & unit velocity
* emerging vs declining categories

### Basket Size & Cross-Selling

* units per transaction (UPT / basket size)
* average order value (AOV)
* multi-item basket ratio
* top co-purchased category pairs

### Floor & Replenishment Alerts

* dead stock alerts (stagnant SKUs ≤ 2 units, clearance candidate)
* stockout urgency anomaly flag (steep W1-2 vs W3-4 run-rate cliff drops)

---

# 15. Statistical Common Sense

Do not call tiny samples meaningful patterns.

For example:

```text
1 Teen customer bought 1 accessory.
```

is not sufficient evidence to claim:

```text
Teenagers prefer accessories.
```

Prefer patterns with meaningful sample sizes and noticeable differences from the overall baseline.

The LLM should be told when a pattern is weak.

---

# 16. LLM Context

Do NOT send the entire CSV by default.

Build a compact structured context:

```json
{
  "dataset": {},
  "products": {},
  "sizes": {},
  "weekdays": {},
  "customers": {},
  "discounts": {},
  "festival_comparison": {}
}
```

The context should contain the numbers required to answer the five assignment questions.

---

# 17. LLM Prompt Requirements

Never use a generic prompt such as:

```text
Analyse this sales data.
```

The prompt must explicitly define:

* September retail context
* available metrics
* five business questions
* expected output format
* plain-English requirement
* evidence requirement
* hallucination restrictions
* distinction between facts and hypotheses

The model should behave like a retail analyst speaking to a store manager.

---

# 18. Required Five Questions

The LLM must answer:

### Q1 — Product Performance

Identify:

* top 3 products
* bottom 3 products
* numerical evidence
* plausible reasons for weak products

Reasons must be labelled as hypotheses when not directly supported.

### Q2 — Size Analysis

Identify:

* high-demand sizes
* slow sizes
* important product-size combinations
* replenishment priorities

Do not claim actual stockouts without inventory evidence.

### Q3 — Weekday Analysis

Identify:

* busiest day
* slowest day
* revenue difference
* whether a promotion is justified

### Q4 — Customer Buying Patterns

Find at least:

* 2 interesting patterns

Each should contain supporting numbers.

### Q5 — Recommended Actions

Generate exactly:

```text
3 actions
```

Each action must be specific and evidence-based.

---

# 19. Structured LLM Output

Prefer JSON.

Example:

```json
{
  "product_insight": {},
  "size_insight": {},
  "weekday_insight": {},
  "customer_patterns": [],
  "recommended_actions": []
}
```

Validate the response using Pydantic or equivalent schema validation.

Do not pass unvalidated model output directly into the final report.

---

# 20. LLM Failure Handling

Handle:

* missing API key
* timeout
* rate limit
* provider errors
* malformed JSON
* empty response
* missing fields

Use bounded retries.

Never retry forever.

If the LLM fails:

```text
LLM
 ↓
Retry
 ↓
Retry failed
 ↓
Deterministic fallback
```

The application must still generate a useful report.

---

# 21. Deterministic Fallback

The fallback report should contain useful Python-generated insights.

At minimum:

* top products
* slow products
* size demand
* busiest day
* slowest day
* major customer patterns
* three rule-based actions

Clearly identify that AI commentary was unavailable.

---

# 22. LLM Provider Abstraction

Keep provider-specific code isolated.

Recommended interface:

```python
class InsightProvider:
    def generate_insights(self, context):
        raise NotImplementedError
```

Do not spread provider SDK calls throughout the analytics code.

The analytics layer must remain independent from the selected LLM.

---

# 23. Hallucination Protection

Never allow the LLM to invent:

* revenue
* quantity
* percentages
* inventory
* profit
* customer counts
* stockout events
* external market statistics

If a number is needed, it should come from the Python analytics context.

---

# 24. Report Generation

The report should be manager-friendly.

Recommended structure:

```text
Executive Summary
Product Performance
Size & Replenishment
Day-of-Week Performance
Customer Buying Patterns
Discount Analysis
Festival Analysis
Recommended Actions
What to Avoid
Limitations
```

Avoid dumping raw JSON into the report.

Avoid excessive technical terminology.

---

# 25. Charts

Generate meaningful charts using Matplotlib.

Recommended:

```text
Top Products
Revenue by Weekday
Units by Size
Revenue by Category
```

Store charts under:

```text
output/charts/
```

Charts should support the report rather than simply decorate it.

---

# 26. Code Quality

Before considering implementation complete:

* remove duplicated code
* remove unused imports
* avoid magic numbers
* add type hints where useful
* use logging
* handle file paths safely
* handle missing files
* handle invalid CSVs
* keep functions focused
* avoid hidden side effects

---

# 27. Testing

Use `pytest`.

Test:

### Validation

* duplicate IDs
* invalid quantity
* invalid price
* invalid discount
* invalid category
* invalid size
* incorrect total amount
* incorrect weekday

### Analytics

* rankings
* revenue
* size aggregation
* weekday aggregation
* customer patterns

### LLM

Mock the provider.

Test:

* valid JSON
* malformed JSON
* missing fields
* timeout
* API failure
* retry
* fallback

Do not make real LLM API calls during normal unit tests.

---

# 28. End-to-End Test

The following should work:

```bash
python generate_data.py
python insight_engine.py
```

The final execution should produce:

```text
output/store_report.md
```

and optionally:

```text
output/store_report.pdf
output/charts/*.png
```

---

# 29. CLI Requirement

The primary command must remain:

```bash
python insight_engine.py
```

Optional arguments can be added later:

```bash
--input
--output
--no-llm
```

Do not make CLI configuration unnecessarily complicated.

---

# 30. Logging

Use the Python logging framework.

Useful events:

```text
INFO  Dataset loaded
INFO  Validation completed
INFO  Analytics completed
INFO  LLM request started
WARNING LLM retry
WARNING Falling back to deterministic analysis
INFO  Charts generated
INFO  Report generated
```

Never log secrets.

---

# 31. Implementation Order

Implement in this order:

```text
1. Project structure
2. Environment configuration
3. Synthetic dataset generator
4. Dataset validation
5. Pandas analytics
6. Analytics tests
7. Context builder
8. LLM provider
9. Structured response validation
10. LLM fallback
11. Chart generation
12. Markdown report
13. PDF generation
14. End-to-end CLI
15. Final tests
16. README
17. Short note
```

Do not jump directly to the LLM before the deterministic analytics layer works.

---

# 32. Development Workflow

For each implementation stage:

1. Read the relevant section of `PLAN.md`.
2. Implement the smallest clean solution.
3. Run tests.
4. Inspect generated data/results.
5. Fix problems.
6. Continue to the next layer.

Do not implement the entire application blindly in one pass.

---

# 33. Verification Before Completion

Before declaring the project complete, verify:

```text
[ ] CSV contains >= 150 rows
[ ] Required columns exist (including transaction_id)
[ ] Data validation works
[ ] Analytics produce expected patterns
[ ] Top/bottom products are sensible
[ ] Size analysis & stockout anomaly flags work
[ ] Slow Tuesday is detected
[ ] Week-on-Week (WoW) velocity trends calculated
[ ] Basket size (UPT & AOV) & cross-selling calculated
[ ] Dead stock & markdown alerts generated
[ ] Customer patterns are meaningful
[ ] Discount analysis works
[ ] Festival comparison works
[ ] LLM receives structured context
[ ] LLM response is schema validated
[ ] Invalid LLM output is handled
[ ] API failure activates fallback
[ ] Charts are generated
[ ] Markdown report is readable
[ ] PDF works if enabled
[ ] Unit tests pass
[ ] python insight_engine.py works
[ ] No secrets are committed
```

---

# 34. Definition of Done

The implementation is complete only when:

```bash
python insight_engine.py
```

runs successfully and produces a manager-ready report.

The report must answer all five required business questions and provide specific recommendations supported by calculated data.

The project must demonstrate:

```text
Reliable Data
      ↓
Validation
      ↓
Deterministic Analytics
      ↓
Structured Context
      ↓
Grounded LLM Reasoning
      ↓
Response Validation
      ↓
Fallback Safety
      ↓
Business Report
```

---

# 35. Final Instruction

Build this project as a **strong, practical portfolio/internship submission**, not as a toy CSV + ChatGPT script.

Prioritize:

1. Correctness
2. Evidence-backed insights
3. Reliability
4. Clean architecture
5. Readability
6. Simple execution
7. Good manager-facing output

When forced to choose between a complicated solution and a simple reliable solution, choose the simple reliable solution.

Never sacrifice numerical correctness just to make the AI output sound impressive.
