# Excel knowledge format

All knowledge workbooks use the same columns:

| Column | Meaning |
| --- | --- |
| category | faq, syllabus, pyq, premium, etc. |
| subcategory | optional extra grouping |
| title | short title |
| question | what the student is asking |
| answer | verified reply text |
| keywords | comma-separated search terms |
| url | official URL only — never invent new ones |
| branch | CSE, Mechanical, Civil, ... |
| exam | HSBTE LEET / HSBTE Diploma |
| priority | higher ranks first |
| active | true/false |

Edit rows, save the file, then call `POST /admin/reload-knowledge` with `X-Admin-Key`.
Do not treat Excel as the user/memory database. That lives in Supabase.
