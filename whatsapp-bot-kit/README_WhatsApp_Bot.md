# WhatsApp Bot Kit — hsbteleet.com

## Import to Google Sheets

1. Open [Google Sheets](https://sheets.google.com) → Blank spreadsheet.
2. **File → Import → Upload** `Sheet1_FAQ_WhatsApp_Bot.csv` → Import location: *Replace spreadsheet* or new sheet named **FAQ**.
3. Create second sheet / second spreadsheet → Import `Sheet2_All_Pages_Resources_URLs.csv` → name it **Resources**.
4. Open `HSBTE_LEET_Project_Overview.html` in Chrome → **Ctrl+P → Save as PDF** (or use generated PDF if present).

## Suggested bot logic

```
IF message matches FAQ.Trigger_Keywords → send FAQ.Full_Answer
ELSE IF message has branch + semester → lookup Resources where Category=PYQ Semester
ELSE IF message has "syllabus" + branch → lookup Diploma Syllabus PDF
ELSE IF message has "leet syllabus" → send LEET PDF URL
ELSE IF message has buy/premium/ultra → send Premium/Ultra buy links
ELSE → send HIGH PRIORITY doubt template (Sheet1 Category = Doubt / Unknown)
```

## Must-know links

| Need | URL |
|------|-----|
| Buy Premium ₹99 | https://hsbteleet.com/premium-login?tier=premium |
| Buy Ultra ₹149 | https://hsbteleet.com/premium-login?tier=ultra |
| LEET Syllabus PDF | https://hsbteleet.com/pdf/B.Tech-LEET-Syllabus-2026.pdf |
| CSE Syllabus PDF | https://hsbteleet.com/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf |
| CSE Sem 1 PYQ | https://hsbteleet.com/computer-1-semester |
| Premium papers | https://hsbteleet.com/premium-papers |
| Contact | https://hsbteleet.com/contact |
| WhatsApp | https://wa.me/919992507270 |

## Example replies

**User:** leet syllabus  
**Bot:** send Sheet1 → LEET Syllabus answer + PDF link

**User:** cse syllabus  
**Bot:** Computer Engineering syllabus PDF

**User:** computer 1st semester pyq  
**Bot:** https://hsbteleet.com/computer-1-semester

**User:** why buy premium  
**Bot:** Sheet1 → Why Buy Premium

**User:** something random / payment stuck  
**Bot:** HIGH PRIORITY admin template
