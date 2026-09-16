# LinkedIn Senior Backend Engineer Scoring Rubric

Role: Senior Backend Engineer - SafeGold, Mumbai  
Purpose: Score and rank pre-filtered LinkedIn profiles.  
Maximum score: 60 points.

## Objective

Score PHP, Python, Laravel, and AWS independently using evidence, recency, and evidenced duration. PHP and Python are highest priority. Missing information receives zero points but must be reported as not evidenced, not as proof that the candidate lacks the technology.

## 1. Fields to Use

Allowed scoring fields:

- Headline
- About
- Experience title or position
- Experience description
- Experience-level technologies or skills attached to a specific experience
- Experience start date, end date, current status, and written duration

Candidate name, LinkedIn URL, current company, employment type, and location are for identification and audit only. Do not score global skills, top skills, endorsements, education, certifications, courses, recommendations, projects, portfolio items, followers, connections, languages, or volunteering. Merge duplicate experience records before scoring.

## 2. Technologies and Maximum Scores

Each technology receives a raw score out of 10:

`Raw Skill Score = Evidence Points + Recency Points + Duration Points`

| Technology | Multiplier | Maximum |
| --- | ---: | ---: |
| PHP | 2.0 | 20 |
| Python | 2.0 | 20 |
| Laravel | 1.2 | 12 |
| AWS | 0.8 | 8 |

Final Score = PHP + Python + Laravel + AWS. Maximum 60.

## 3. Approved Technology Evidence

### PHP

Count explicit references to PHP, Core PHP, or PHP followed by a version. Do not infer PHP from Laravel alone, WordPress, phpMyAdmin, or LAMP.

### Python

Count explicit references to Python or Python followed by a version. Do not infer Python from Django, Flask, or FastAPI unless Python itself is explicitly present.

### Laravel

Count explicit references to Laravel or Laravel Framework. Do not infer Laravel from generic PHP-framework references. Laravel does not automatically count as PHP evidence.

### AWS

Count explicit references to AWS, Amazon Web Services, EC2, RDS, Lambda, SQS, or ElastiCache when the context establishes cloud or infrastructure usage. Do not count generic cloud, serverless, virtual-machine, or message-queue references without AWS or an identifiable AWS service.

## 4. Evidence Points - Maximum 4 per Technology

Find all valid mentions and use the strongest valid evidence source. Do not stack evidence points.

| Strongest evidence | Points |
| --- | ---: |
| Experience description showing actual engineering use | 4 |
| Role-specific technology stack/list inside an experience | 3 |
| Technology-specific experience title | 3 |
| Headline explicitly naming the technology | 3 |
| About explicitly naming the technology | 2 |
| Experience-level technology/skill attached to a role | 1 |
| No permitted evidence | 0 |

Actual engineering use connects the technology to work such as developed, built, maintained, implemented, migrated, integrated, deployed, architected, optimised, operated, managed, or scaled. A role-specific stack is valid even without an engineering action, but it is not the same as the global Skills section.

## 5. Recency Points - Maximum 3 per Technology

For each technology, use the end date of the latest dated experience containing valid evidence.

| Latest qualifying end date | Points |
| --- | ---: |
| Present or 2026 | 3 |
| 2025 | 2 |
| 2024 | 1 |
| 2022-2023 | 0.5 |
| 2021 or earlier | 0 |

Recency may come from a technology-specific title, actual-use description, role-specific stack, or experience-level technology. Headline and About are undated and receive no recency points. Do not use the latest job date unless that job contains evidence of the technology.

## 6. Evidenced Duration Points - Maximum 3 per Technology

### Tier A - Strong duration evidence

Qualifying sources are an experience description showing actual engineering use or a technology-specific experience title. Combine non-overlapping duration across qualifying Tier A experiences.

| Evidenced duration | Points |
| --- | ---: |
| 3 years or more | 3 |
| 2 to under 3 years | 2 |
| 1 to under 2 years | 1 |
| More than 0 but under 1 year | 0.5 |
| None | 0 |

Maximum Tier A duration score: 3.

### Tier B - Role-stack duration evidence

The qualifying source is a technology explicitly included in a role-specific stack. Combine non-overlapping Tier B durations and use the same duration table. Maximum Tier B duration score: 2.

### Tier C - Experience-level technology tag

The qualifying source is an experience-level technology or skill attached to a dated role. Combine non-overlapping Tier C durations and use the same duration table. Maximum Tier C duration score: 1.

Calculate each tier independently. Final Duration Points are the highest eligible score across Tier A, B, or C; do not add tiers. Headline and About receive zero duration points.

## 7. Date Normalisation

- Use stated month and year when both exist.
- For Present roles, use the evaluation date as the end date.
- Use a clear written duration when dates are incomplete.
- If only years are available and the start and end year are the same, use 6 months.
- If only years are available and the end year is later, use `12 x (end year - start year - 1) + 8 months`.
- Do not otherwise invent month-level precision.
- Count overlapping qualifying roles only once within the same duration tier and technology.
- If dates are contradictory or impossible, count only supportable duration and set Date-Quality Warning to Yes.

## 8. Score Calculation

- PHP Score = Raw PHP Score x 2.0, maximum 20.
- Python Score = Raw Python Score x 2.0, maximum 20.
- Laravel Score = Raw Laravel Score x 1.2, maximum 12.
- AWS Score = Raw AWS Score x 0.8, maximum 8.
- Final Score = PHP + Python + Laravel + AWS, maximum 60.

Use full precision while calculating. Display technology scores and Final Score to one decimal place when necessary. Do not apply undocumented adjustments.

## 9. Evidence Interpretation

Evidence, recency, and duration are separate for every technology. Headline and About provide evidence only. An experience-level technology provides evidence, recency, and Tier C duration eligibility. A role-specific stack provides evidence, recency, and Tier B duration eligibility. A technology-specific title or actual-use description provides evidence, recency, and Tier A duration eligibility. Evidence points may come from one source while recency or duration comes from another valid dated source.

## 10. Non-Scoring Warnings

Warnings never change the score.

- **PHP Unverified:** Yes when PHP is absent from every permitted source.
- **Python Unverified:** Yes when Python is absent from every permitted source.
- **Backend Relevance Unverified:** Yes when no title or description clearly indicates backend, server-side, API development, software engineering, application development, or related backend engineering work.
- **Seniority Unverified:** Yes when less than approximately four years of identifiable development experience is visible or dates cannot verify seniority.
- **Date-Quality Warning:** Yes when dates are contradictory, impossible, or materially inconsistent.

Use "unverified," not language claiming the candidate lacks the capability.

## 11. Ranking

Rank candidates from highest to lowest Final Score. For equal scores, apply these tie-breakers in order:

1. Higher PHP score
2. Higher Python score
3. Higher Laravel score
4. Higher AWS score
5. Higher weighted recency subtotal
6. Higher weighted duration subtotal
7. Higher weighted evidence subtotal
8. Candidate name alphabetically

Tie-breakers affect rank only and do not change Final Score.

## 12. Final Output

Return one row per candidate with these columns in this order:

1. Rank Number
2. Candidate
3. Profile URL
4. Current Company
5. Current Title
6. PHP Score (/20)
7. Python Score (/20)
8. Laravel Score (/12)
9. AWS Score (/8)
10. Final Score (/60)
11. PHP Unverified
12. Python Unverified
13. Backend Relevance Unverified
14. Seniority Unverified
15. Date-Quality Warning
16. Strongest Evidence
17. Missing or Unclear Information
18. Score Rationale

Return at most three short evidence points in the single Strongest Evidence cell, separated by ` | `, prioritising evidence that materially influenced ranking. State missing information neutrally. Score Rationale must contain 50 to 75 words.

## 13. Deterministic Edge Rules

- Repeated mentions of one technology do not increase evidence points.
- Several valid terms for one technology still produce one technology score.
- Laravel does not automatically score PHP.
- Django, Flask, and FastAPI do not automatically score Python.
- Several AWS services still produce one AWS score.
- Headline and About receive no recency or duration.
- Duration tiers are never added; use the strongest eligible tier score.
- Missing permitted evidence produces zero and must be reported as not evidenced.
- Duplicate experience records must not add repeated evidence or duration.
