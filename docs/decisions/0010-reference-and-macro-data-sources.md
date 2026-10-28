# 0010. Reference and macro data sources

Status: Accepted · 2026-10-28

Extends [0005](0005-public-data-sources-only.md).

## Context

Job postings from company ATS boards (Greenhouse, Lever, Ashby) show what employers ask for, but they cover only the companies we track. They cannot show the size of the whole market, official wage levels or exchange rates, and they give us no ready skill dictionary. Under 0005 every new source must be public, free and allowed for automated use.

## Decision

Add these sources, all open and free:

| Source | What we use | Phase |
| --- | --- | --- |
| Bank of Canada Valet API | Daily USD/CAD rate to convert salaries; JSON, no key | MVP |
| O*NET Technology Skills, Hot Technologies | Seed skill dictionary with names, categories and demand flags | MVP |
| Indeed Hiring Lab job postings tracker | Daily index of Indeed posting volume (100 = 1 February 2020) for Canada, provinces and sectors including software development; CSV, CC BY 4.0 | MVP |
| BLS Occupational Employment and Wage Statistics | Official US wages by occupation and state, to check our posted salaries | Later |
| BLS JOLTS | US openings, hires and layoffs by industry, as context for the layoffs view | Later |
| Statistics Canada Job Vacancy and Wage Survey | Canadian vacancies and offered wages by province and industry | Later |
| Stack Overflow Developer Survey | Self-reported pay by country and technology, to compare with posted pay; ODbL | Later |
| Hacker News "Who is hiring?" threads | Extra startup postings through the official Hacker News API, parsed with an LLM | Later |

Each source keeps its own adapter and raw storage, like the ATS sources.

## Alternatives considered

- **TrueUp.** Has jobs, trends and layoffs, but no API, and its terms forbid automated access, scraping, reuse and using its data to train or evaluate models.
- **Postings from indeed.com.** Its terms allow personal, non-commercial job search only, and its APIs serve employers and ATS partners.
- **SmartRecruiters Posting API.** Needs an API key from each company's account.

## Consequences

- The site credits Indeed Hiring Lab and O*NET as sources (CC BY 4.0).
- If we publish a database derived from Stack Overflow survey data, it must also be under ODbL.
- Hiring Lab is an index, not a count of jobs, and its history was revised when its method changed in November 2024. Charts label it as an index.
- Statistics Canada breaks vacancies by occupation only into broad national groups, so it gives context by province and industry, not by tech role.
