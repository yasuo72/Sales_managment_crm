# Short Note

I prompted the AI with role-based, store-manager-grade questions rather than vague "analyze data" requests, targeting product velocity, size demand distribution, mid-week footfall troughs, and next-week floor action plans.

Thinking like a store manager, I noticed critical gaps and enriched the dataset: I added festival sales spikes and sequential `bill_id` clustering to enable real-world market basket analysis.

Initially, feeding raw transaction rows directly to the LLM caused severe arithmetic hallucinations: revenue drifted from ₹1,70,820.50 to ~₹1,95,000, and it flagged five unevidenced stockouts simply because those SKUs did not sell daily.

I resolved this by enforcing a strict architectural boundary: Pandas computes all deterministic sums, run-rates, size curves, and basket metrics, injecting verified JSON proof into the prompt.

With additional time, I would integrate live ERP inventory webhooks, SKU cost sheets (COGS) for gross margin calculation, and automated multi-store PDF dispatch and intigrated live instruction message share for floor staffs.
