# Hand-labeled skills

`labeled.jsonl` holds 30 open postings (10 each from Stripe, Cohere and Wealthsimple, picked in `md5(source_id)` order) with the skills a person found by reading the text. `skills_eval` compares the dictionary extractor against these labels.

Each line: `company`, `source`, `source_id`, `title`, `skills` (canonical names), `text` (title plus description at labeling time, so the evaluation does not change when a posting does).

## Labeling rules

- Label a specific technology or engineering/data practice the text names as something the role uses, requires or would like (nice-to-have counts), including a described team stack.
- Do not infer: "cloud" is not AWS, "data pipelines" is not ETL, PostgreSQL does not imply SQL.
- Scope is the dictionary's scope, development and data work. Business tools are not labeled: CRMs (Salesforce, HubSpot), HR systems (Workday), marketing platforms (Braze), design suites (Adobe), chat and docs (Slack, Notion).
- Use the canonical name even if the dictionary lacks the skill ("Kata Containers", "C"): a skill missing from the dictionary should count as a miss.
- Labels were written before the dictionary existed and are not edited to fit it. Fix a label only when it is wrong about the text, and say so in the commit.
