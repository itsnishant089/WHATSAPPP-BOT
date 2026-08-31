/**
 * Generate WhatsApp automation kit: 2 CSV sheets + overview HTML/PDF
 * Run: node whatsapp-bot-kit/_generate.js
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname);
const BASE = 'https://hsbteleet.com';

function csvEscape(v) {
  const s = String(v ?? '');
  if (/[",\n\r]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
  return s;
}
function writeCsv(file, headers, rows) {
  const lines = [headers.join(',')];
  for (const row of rows) lines.push(headers.map((h) => csvEscape(row[h])).join(','));
  fs.writeFileSync(path.join(ROOT, file), '\uFEFF' + lines.join('\n'), 'utf8'); // BOM for Google Sheets/Excel
  console.log('Wrote', file, rows.length, 'rows');
}

const DOUBT_REPLY =
  'Your message is marked HIGH PRIORITY ✅\n\n' +
  'Our admin will contact you soon on WhatsApp.\n\n' +
  'Meanwhile you can also:\n' +
  '• Email: nishant@hsbteleet.com\n' +
  '• WhatsApp: https://wa.me/919992507270\n' +
  '• Contact page: https://hsbteleet.com/contact\n\n' +
  'Thank you for choosing hsbteleet.com 🙏';

// ═══════════════════════════════════════════════════════════
// SHEET 1 — FAQ (full answers for WhatsApp bot)
// ═══════════════════════════════════════════════════════════
const faqRows = [
  {
    Category: 'Greeting',
    Trigger_Keywords: 'hi, hello, namaste, hii, hey, start, help',
    Full_Answer:
      'Namaste! 🙏 Welcome to *hsbteleet.com* WhatsApp help.\n\nI can instantly share:\n1️⃣ HSBTE Diploma PYQ (branch + semester)\n2️⃣ Diploma Syllabus PDF (branch-wise)\n3️⃣ Haryana LEET Syllabus / Exam Pattern\n4️⃣ Free LEET sample papers\n5️⃣ Premium ₹99 & Ultra Premium ₹149 details\n6️⃣ Counseling help ₹99\n\nReply with what you need, e.g.\n• "CSE 1st semester PYQ"\n• "LEET syllabus"\n• "Computer syllabus PDF"\n• "Buy Premium"\n• "Ultra Premium kya milta hai"',
    Links_To_Send: BASE + '/',
    Priority: 'Normal'
  },
  {
    Category: 'Doubt / Unknown',
    Trigger_Keywords: 'doubt, doubt hai, question, custom, help me, confuse, samajh nahi, not listed, other',
    Full_Answer: DOUBT_REPLY,
    Links_To_Send: BASE + '/contact',
    Priority: 'HIGH'
  },
  {
    Category: 'Why Buy Premium',
    Trigger_Keywords: 'why premium, why buy, kyun buy, premium kyu, worth, free vs premium, difference free',
    Full_Answer:
      '*Why buy Premium on hsbteleet.com?*\n\nFree site pe HSBTE diploma PYQ + basic LEET info milti hai.\n\n*Premium (₹99 one-time)* unlock karta hai:\n✅ *34 exclusive* full-syllabus LEET sample papers (free papers se alag unique questions)\n✅ Official Haryana LEET Syllabus PDF + B.Tech LEET Prospectus\n✅ Formula sheets + important topics + cheat sheets (Section A–D)\n✅ Rank Analysis tool\n✅ 100% Ad-free + *Lifetime access*\n\nLEET 90 Q / 90 min pattern pe practice karne ke liye ye papers real exam jaisi difficulty pe banaye gaye hain.\n\n👉 Buy / Login: ' +
      BASE +
      '/premium-login?tier=premium\n👉 Plans detail: ' +
      BASE +
      '/btech-leet-premium\n👉 After login papers: ' +
      BASE +
      '/premium-papers',
    Links_To_Send: BASE + '/premium-login?tier=premium | ' + BASE + '/btech-leet-premium',
    Priority: 'Normal'
  },
  {
    Category: 'Premium Plan',
    Trigger_Keywords: 'premium, buy premium, premium 99, get premium, premium price, premium kya hai',
    Full_Answer:
      '*HSBTE LEET Premium — ₹99 (one-time, lifetime)*\n\n*Includes:*\n• 34 exclusive LEET sample papers (section-wise + full syllabus)\n• Official LEET Syllabus PDF\n• Official B.Tech LEET Prospectus 2027\n• Formula sheets (A/B/C/D)\n• Important topics PDFs\n• Cheat sheets\n• Rank Analysis tool\n• Zero ads\n• Lifetime access (pay once)\n\n*Does NOT include:* College Predictor, Rank Predictor, Cutoff Analyzer, AI Counselling tools (wo Ultra Premium mein hain).\n\n🛒 Buy now: ' +
      BASE +
      '/premium-login?tier=premium\n📄 See all features: ' +
      BASE +
      '/btech-leet-premium',
    Links_To_Send: BASE + '/premium-login?tier=premium',
    Priority: 'Normal'
  },
  {
    Category: 'Ultra Premium Plan',
    Trigger_Keywords: 'ultra, ultra premium, 149, college predictor, rank predictor, counselling tool, cutoff analyzer',
    Full_Answer:
      '*Ultra Premium — ₹149 (one-time, lifetime)* 🔥 Best Value\n\n*Everything in Premium ₹99* PLUS:\n⭐ AI College Predictor (2027 analytics)\n⭐ Rank Predictor by marks\n⭐ Smart Counselling Advisor (AI)\n⭐ AI Choice Filling Generator\n⭐ Cutoff Analyzer (all colleges)\n⭐ Choice Mistake Detector\n⭐ College Comparison Tool\n⭐ Upgrade Chance Calculator\n⭐ Mock Counselling Simulator\n⭐ AI Study Planner (LEET syllabus)\n⭐ Zero ads + Lifetime access\n\nNote: Predictions approximate (±15%). Always verify with official HSTES.\n\n🛒 Buy Ultra: ' +
      BASE +
      '/premium-login?tier=ultra\n🛠 Ultra tools page: ' +
      BASE +
      '/ultra-premium\n📄 Full compare: ' +
      BASE +
      '/btech-leet-premium',
    Links_To_Send: BASE + '/premium-login?tier=ultra | ' + BASE + '/ultra-premium',
    Priority: 'Normal'
  },
  {
    Category: 'Premium vs Ultra',
    Trigger_Keywords: 'premium vs ultra, difference premium ultra, which plan, konsa plan, compare plans',
    Full_Answer:
      '*Premium ₹99 vs Ultra Premium ₹149*\n\n*Both get:* 34 exclusive papers, syllabus PDF, prospectus, formula/topic sheets, Rank Analysis, ad-free, lifetime.\n\n*Only Ultra ₹149 gets:* College Predictor, Rank Predictor, Cutoff Analyzer, AI Counselling Advisor, Choice Filling tools, Study Planner, Mock Counselling, College Comparison.\n\n*Recommendation:*\n• Sirf papers practice chahiye → *Premium ₹99*\n• College/rank/counselling strategy bhi chahiye → *Ultra ₹149*\n\nBuy Premium: ' +
      BASE +
      '/premium-login?tier=premium\nBuy Ultra: ' +
      BASE +
      '/premium-login?tier=ultra',
    Links_To_Send: BASE + '/btech-leet-premium',
    Priority: 'Normal'
  },
  {
    Category: 'How to Buy / Login',
    Trigger_Keywords: 'how to buy, kaise buy, login, register, payment, razorpay, account',
    Full_Answer:
      '*How to buy Premium / Ultra*\n\n1. Open: ' +
      BASE +
      '/premium-login\n2. Choose *Premium ₹99* or *Ultra ₹149*\n3. Register with Name, Email, Mobile\n4. Pay securely via Razorpay\n5. Lifetime access unlock instantly\n\nAfter payment:\n• Papers → ' +
      BASE +
      '/premium-papers\n• Ultra tools → ' +
      BASE +
      '/ultra-premium\n\nAlready paid? Just Login on the same page.\n\nPayment issue? Reply here — admin will help (HIGH PRIORITY).',
    Links_To_Send: BASE + '/premium-login',
    Priority: 'Normal'
  },
  {
    Category: 'Premium Papers Access',
    Trigger_Keywords: 'premium papers, sample paper premium, mock test, paper 17, 34 papers, where papers',
    Full_Answer:
      '*34 Premium LEET Sample Papers*\n\nPattern: 90 MCQ · 90 minutes · No negative marking (official LEET scheme)\nSections: Basic Sciences, Electronics stream, Mechanical stream, Other Engg streams.\n\nAccess (login required):\n👉 ' +
      BASE +
      '/premium-papers\n\nDirect paper examples:\n• Paper 1: ' +
      BASE +
      '/premium-sample-paper-1\n• Paper 17: ' +
      BASE +
      '/premium-sample-paper-17\n• Paper 26: ' +
      BASE +
      '/premium-sample-paper-26\n\nNot purchased yet? Buy: ' +
      BASE +
      '/premium-login?tier=premium',
    Links_To_Send: BASE + '/premium-papers',
    Priority: 'Normal'
  },
  {
    Category: 'LEET Syllabus',
    Trigger_Keywords: 'leet syllabus, leet syllabus pdf, btech leet syllabus, haryana leet syllabus, ocet syllabus',
    Full_Answer:
      '*Haryana B.Tech LEET Syllabus (Official PDF)*\n\nDownload PDF:\n📄 ' +
      BASE +
      '/pdf/B.Tech-LEET-Syllabus-2026.pdf\n\nSyllabus page (explained):\n👉 ' +
      BASE +
      '/leet-syllabus\nAlso: ' +
      BASE +
      '/haryana-leet-syllabus\n\n*Exam quick facts:*\n• 90 objective MCQs · 90 minutes\n• 1 mark each · *No negative marking*\n• Section a Basic Sciences (25)\n• Section b Electronics stream (25)\n• Section c Mechanical stream (20)\n• Section d Other Engg streams (20)\n\nExam pattern page: ' +
      BASE +
      '/haryana-leet-exam-pattern',
    Links_To_Send: BASE + '/pdf/B.Tech-LEET-Syllabus-2026.pdf | ' + BASE + '/leet-syllabus',
    Priority: 'Normal'
  },
  {
    Category: 'LEET Exam Pattern',
    Trigger_Keywords: 'exam pattern, marking scheme, negative marking, 90 questions, duration',
    Full_Answer:
      '*Haryana LEET Exam Pattern*\n\n• Mode: Online CBT\n• Questions: 90 MCQ\n• Duration: 90 minutes\n• Marks: 1 per question\n• Negative marking: *NO*\n• Language: English\n\nFull page: ' +
      BASE +
      '/haryana-leet-exam-pattern\nSyllabus PDF: ' +
      BASE +
      '/pdf/B.Tech-LEET-Syllabus-2026.pdf',
    Links_To_Send: BASE + '/haryana-leet-exam-pattern',
    Priority: 'Normal'
  },
  {
    Category: 'LEET Eligibility',
    Trigger_Keywords: 'eligibility, eligible, diploma percentage, who can apply leet',
    Full_Answer:
      '*LEET Eligibility (summary)*\n\nDiploma holders seeking admission to *2nd year (3rd semester) B.E./B.Tech* under Lateral Entry in Haryana (as per HSTES brochure).\n\nFull details:\n👉 ' +
      BASE +
      '/haryana-leet-eligibility\nProspectus PDF (Premium users also get inside dashboard):\n👉 ' +
      BASE +
      '/pdf/BTechLE-Prospectus-2026.pdf\n\nOfficial HSTES: https://hstes.org.in',
    Links_To_Send: BASE + '/haryana-leet-eligibility',
    Priority: 'Normal'
  },
  {
    Category: 'Free LEET Sample Papers',
    Trigger_Keywords: 'free sample paper, free leet paper, btech sample, mock free, leet sample',
    Full_Answer:
      '*Free LEET Sample Papers*\n\nHub: ' +
      BASE +
      '/btech-leet-sample-paper\nAlso: ' +
      BASE +
      '/leet-sample-paper\n\nFree set examples:\n• ' +
      BASE +
      '/btech-sample-paper-1\n• ' +
      BASE +
      '/btech-sample-paper-2\n(… up to free sample sets on site)\n\n*Want harder exclusive papers?* 34 Premium papers → ' +
      BASE +
      '/premium-login?tier=premium',
    Links_To_Send: BASE + '/btech-leet-sample-paper',
    Priority: 'Normal'
  },
  {
    Category: 'Diploma Syllabus Hub',
    Trigger_Keywords: 'diploma syllabus, hsbte syllabus, polytechnic syllabus, branch syllabus',
    Full_Answer:
      '*HSBTE Diploma Syllabus (all branches)*\n\nOpen branch cards & download PDFs:\n👉 ' +
      BASE +
      '/hsbte-syllabus\n\nPopular direct PDFs:\n• Computer Engg: ' +
      BASE +
      '/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf\n• Mechanical: ' +
      BASE +
      '/syllabus/14-Final-01-08-2024-Diploma-in-Mechanical-Engineering.pdf\n• Civil: ' +
      BASE +
      '/syllabus/17-Final-01-08-2024-Diploma-in-Civil-Engineering.pdf\n• Electrical: ' +
      BASE +
      '/syllabus/21-Final-01-08-2024-Diploma-in-Electrical-Engineering.pdf\n• AI & ML: ' +
      BASE +
      '/syllabus/18-Final-01-08-2024-Diploma-in-Artificial-Intelligence-and-Machine-Learning.pdf\n\nBol do branch name — main PDF link bhej dunga.',
    Links_To_Send: BASE + '/hsbte-syllabus',
    Priority: 'Normal'
  },
  {
    Category: 'CSE Syllabus PDF',
    Trigger_Keywords: 'cse syllabus, computer syllabus, computer engineering syllabus, diploma cse syllabus',
    Full_Answer:
      '*Diploma in Computer Engineering — Official Syllabus PDF*\n\n📄 Download:\n' +
      BASE +
      '/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf\n\nAll branches syllabus page:\n👉 ' +
      BASE +
      '/hsbte-syllabus\n\nCSE PYQ hub:\n👉 ' +
      BASE +
      '/computer-pyq',
    Links_To_Send: BASE + '/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf',
    Priority: 'Normal'
  },
  {
    Category: 'PYQ Hub',
    Trigger_Keywords: 'pyq, previous year, previous year paper, hsbte pyq, question paper diploma',
    Full_Answer:
      '*HSBTE Previous Year Question Papers (FREE)*\n\nAll branches hub:\n👉 ' +
      BASE +
      '/hsbte-pyq\n\nComputer Engg hub:\n👉 ' +
      BASE +
      '/computer-pyq\n\nFormat: Branch page → Semester → Subject-wise PDFs.\n\nExample — CSE 1st semester:\n👉 ' +
      BASE +
      '/computer-1-semester\n\nExample — Mechanical 3rd semester:\n👉 ' +
      BASE +
      '/mech-3\n\nBatao: *Branch + Semester* (jaise "civil 2nd sem PYQ").',
    Links_To_Send: BASE + '/hsbte-pyq',
    Priority: 'Normal'
  },
  {
    Category: 'CSE Sem 1 PYQ',
    Trigger_Keywords: 'cse 1, cse 1st, computer 1st semester, computer semester 1, cse sem 1 pyq, computer 1 semester',
    Full_Answer:
      '*Computer Engineering — 1st Semester PYQ*\n\n👉 Open all subjects:\n' +
      BASE +
      '/computer-1-semester\n\nBranch hub: ' +
      BASE +
      '/computer-pyq\nSyllabus PDF: ' +
      BASE +
      '/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf',
    Links_To_Send: BASE + '/computer-1-semester',
    Priority: 'Normal'
  },
  {
    Category: 'CSE Other Semesters',
    Trigger_Keywords: 'cse 2, cse 3, cse 4, cse 5, cse 6, computer 2nd, computer 3rd, computer 4th, computer 5th, computer 6th',
    Full_Answer:
      '*Computer Engineering PYQ by semester*\n\n• Sem 1: ' +
      BASE +
      '/computer-1-semester\n• Sem 2: ' +
      BASE +
      '/computer-pyq-2-semester\n• Sem 3: ' +
      BASE +
      '/computer-pyq-3-semester\n• Sem 4: ' +
      BASE +
      '/computer-pyq-4-semester\n• Sem 5: ' +
      BASE +
      '/computer-pyq-5-semester\n• Sem 6: ' +
      BASE +
      '/computer-pyq-6-semester\n\nHub: ' +
      BASE +
      '/computer-pyq',
    Links_To_Send: BASE + '/computer-pyq',
    Priority: 'Normal'
  },
  {
    Category: 'Counseling Help',
    Trigger_Keywords: 'counseling, counselling, choice filling help, college recommend, counseling 99',
    Full_Answer:
      '*Personalized LEET Counseling Help — ₹99*\n\nExpert reviews your rank, category, diploma branch & preferences and suggests colleges/branches with reasons.\n\n👉 Submit: ' +
      BASE +
      '/counseling\n👉 Track replies: ' +
      BASE +
      '/user-counseling\n\nResponse usually 24–48 hours on dashboard.\n\nWant AI predictors yourself? → Ultra Premium ₹149\n' +
      BASE +
      '/premium-login?tier=ultra',
    Links_To_Send: BASE + '/counseling',
    Priority: 'Normal'
  },
  {
    Category: 'LEET Counselling Info',
    Trigger_Keywords: 'leet counselling process, hstes counselling, choice locking, seat allotment',
    Full_Answer:
      '*Haryana LEET Counselling (info)*\n\nGuide: ' +
      BASE +
      '/haryana-leet-counselling\nAlso: ' +
      BASE +
      '/leet-counselling\nDocuments: ' +
      BASE +
      '/haryana-leet-admission-documents\nSeat intake: ' +
      BASE +
      '/haryana-leet-seat-intake\nColleges: ' +
      BASE +
      '/haryana-leet-colleges\n\nOfficial portal: https://hstes.org.in',
    Links_To_Send: BASE + '/haryana-leet-counselling',
    Priority: 'Normal'
  },
  {
    Category: 'Cutoff / Colleges',
    Trigger_Keywords: 'cutoff, cut off, last year cutoff, colleges, college list',
    Full_Answer:
      '*Cutoff & Colleges*\n\n• Cutoff page: ' +
      BASE +
      '/haryana-leet-cutoff\n• Last year cutoff: ' +
      BASE +
      '/last-year-cutoff\n• Cutoff analytics: ' +
      BASE +
      '/cutoff-analytics\n• Colleges: ' +
      BASE +
      '/haryana-leet-colleges\n• College comparison: ' +
      BASE +
      '/college-comparison\n\n*AI College Predictor* (Ultra only):\n' +
      BASE +
      '/college-predictor\nBuy Ultra: ' +
      BASE +
      '/premium-login?tier=ultra',
    Links_To_Send: BASE + '/haryana-leet-cutoff',
    Priority: 'Normal'
  },
  {
    Category: 'B.Pharmacy LEET',
    Trigger_Keywords: 'bpharmacy, b pharma leet, pharmacy leet, ocet pharmacy',
    Full_Answer:
      '*B.Pharmacy Lateral Entry / OCET*\n\nPage: ' +
      BASE +
      '/B-Pharmacy-leet\nSample papers: ' +
      BASE +
      '/b-pharmacy-leet-sample-paper\nKey dates: ' +
      BASE +
      '/b-pharmacy-leet-key-dates\nSyllabus PDF: ' +
      BASE +
      '/pdf/Syllabus-for-OCET-of-B.Pharmacy-Lateral-Entry-2026.pdf\nProspectus: ' +
      BASE +
      '/pdf/BPharma-BPharmaLE-Prospectus-2026.pdf',
    Links_To_Send: BASE + '/B-Pharmacy-leet',
    Priority: 'Normal'
  },
  {
    Category: 'Contact',
    Trigger_Keywords: 'contact, admin, support, whatsapp number, email, phone',
    Full_Answer:
      '*Contact hsbteleet.com*\n\n📧 Email: nishant@hsbteleet.com\n📱 WhatsApp only: 9992507270\n💬 Chat: https://wa.me/919992507270\n🌐 Page: ' +
      BASE +
      '/contact\n\nAapka message HIGH PRIORITY pe mark ho sakta hai — admin jaldi reply karega.',
    Links_To_Send: BASE + '/contact | https://wa.me/919992507270',
    Priority: 'Normal'
  },
  {
    Category: 'Website Overview',
    Trigger_Keywords: 'website, about, kya hai site, hsbteleet, what is this',
    Full_Answer:
      '*hsbteleet.com* — Haryana Polytechnic (HSBTE) PYQ + Haryana LEET (B.Tech / B.Pharm lateral entry) preparation platform.\n\n*FREE:* Diploma PYQ all branches, diploma syllabus PDFs, LEET info pages, some free sample papers.\n*Premium ₹99:* 34 exclusive LEET mocks + PDFs + Rank Analysis.\n*Ultra ₹149:* Premium + AI college/rank/counselling tools.\n*Counseling ₹99:* Personal expert suggestions.\n\nHome: ' +
      BASE +
      '/\nLEET hub: ' +
      BASE +
      '/haryanaleet\nPremium: ' +
      BASE +
      '/btech-leet-premium',
    Links_To_Send: BASE + '/',
    Priority: 'Normal'
  },
  {
    Category: 'Refund / Lifetime',
    Trigger_Keywords: 'refund, lifetime, expiry, expire, one time',
    Full_Answer:
      'Premium & Ultra Premium are *one-time payment* with *lifetime access* (as long as the service runs). No monthly fee.\n\nPayment/access issue? Send your registered email + payment ID — reply marked HIGH PRIORITY, admin will contact soon.\n\n' +
      DOUBT_REPLY,
    Links_To_Send: BASE + '/contact',
    Priority: 'HIGH'
  },
  {
    Category: 'Official Sources',
    Trigger_Keywords: 'official, hstes, dte, government site',
    Full_Answer:
      'Official portals:\n• HSTES: https://hstes.org.in\n• Technical Education Haryana: http://techeduhry.gov.in/\n\nhsbteleet.com helps with PYQ, syllabus PDFs, LEET practice & counselling tools — always cross-check dates/rules on official HSTES brochure.',
    Links_To_Send: 'https://hstes.org.in',
    Priority: 'Normal'
  }
];

writeCsv(
  'Sheet1_FAQ_WhatsApp_Bot.csv',
  ['Category', 'Trigger_Keywords', 'Full_Answer', 'Links_To_Send', 'Priority'],
  faqRows
);

// ═══════════════════════════════════════════════════════════
// SHEET 2 — All resources / URLs
// ═══════════════════════════════════════════════════════════
const resourceRows = [];
function addRes(Category, Name, Description, URL, Keywords, Notes) {
  resourceRows.push({ Category, Name, Description, URL, Keywords, Notes });
}

// Main pages
addRes('Main', 'Home', 'Website homepage', BASE + '/', 'home, hsbteleet', 'Start here');
addRes('Main', 'HSBTE PYQ Hub', 'All diploma previous year papers', BASE + '/hsbte-pyq', 'pyq, previous year, diploma papers', 'FREE');
addRes('Main', 'HSBTE Diploma Syllabus', 'All branch syllabus PDF cards', BASE + '/hsbte-syllabus', 'diploma syllabus, hsbte syllabus', 'FREE PDFs');
addRes('Main', 'Haryana LEET Hub', 'LEET landing / overview', BASE + '/haryanaleet', 'leet, haryana leet', '');
addRes('Main', 'B.Tech LEET', 'B.Tech LEET main page', BASE + '/btech-leet', 'btech leet', '');
addRes('Main', 'FAQ', 'Website FAQ page', BASE + '/faq', 'faq', '');
addRes('Main', 'Contact', 'Email + WhatsApp contact', BASE + '/contact', 'contact, support', 'WhatsApp 9992507270');
addRes('Main', 'HSBTE Result', 'Result related page', BASE + '/hsbte-result', 'result', '');
addRes('Main', 'Haryana Diploma Info', 'Diploma info page', BASE + '/haryana-diploma-info', 'diploma info', '');

// Premium
addRes('Premium', 'Premium Landing', 'Plans compare Premium vs Ultra', BASE + '/btech-leet-premium', 'premium, ultra, plans', 'Marketing page');
addRes('Premium', 'Buy / Login Premium', 'Register + Razorpay for Premium ₹99', BASE + '/premium-login?tier=premium', 'buy premium, login, pay 99', 'BUY LINK');
addRes('Premium', 'Buy / Login Ultra', 'Register + Razorpay for Ultra ₹149', BASE + '/premium-login?tier=ultra', 'buy ultra, login, pay 149', 'BUY LINK');
addRes('Premium', 'Premium Login (default)', 'Login/register page', BASE + '/premium-login', 'login premium', '');
addRes('Premium', 'Premium Papers Dashboard', 'All 34 papers + PDFs (login required)', BASE + '/premium-papers', 'premium papers, mocks', 'Login required');
addRes('Premium', 'Ultra Premium Tools', 'College/rank/counselling tools', BASE + '/ultra-premium', 'ultra tools, predictor', 'Ultra login required');
addRes('Premium', 'Rank Analysis', 'Rank analysis tool', BASE + '/rank-analysis', 'rank analysis', 'Premium+');
addRes('Premium', 'College Predictor', 'AI college predictor', BASE + '/college-predictor', 'college predictor', 'Ultra only');
addRes('Premium', 'Study Plan', 'AI study planner', BASE + '/study-plan', 'study plan', 'Ultra');
addRes('Premium', 'Cutoff Analytics', 'Cutoff analytics tool', BASE + '/cutoff-analytics', 'cutoff analytics', 'Ultra');
addRes('Premium', 'College Comparison', 'Compare colleges', BASE + '/college-comparison', 'college comparison', 'Ultra');
addRes('Premium', 'Last Year Cutoff', 'Last year cutoff page', BASE + '/last-year-cutoff', 'last year cutoff', '');

for (let i = 1; i <= 26; i++) {
  addRes(
    'Premium Papers',
    'Premium Sample Paper ' + i,
    'Full syllabus mock 90Q / 90 min (login)',
    BASE + '/premium-sample-paper-' + i,
    'premium paper ' + i + ', mock ' + i,
    'Requires Premium/Ultra'
  );
}

// LEET info
const leetPages = [
  ['LEET Syllabus (page)', '/leet-syllabus', 'leet syllabus'],
  ['Haryana LEET Syllabus', '/haryana-leet-syllabus', 'haryana leet syllabus'],
  ['Exam Pattern', '/haryana-leet-exam-pattern', 'exam pattern, marking'],
  ['Eligibility', '/haryana-leet-eligibility', 'eligibility'],
  ['Counselling Guide', '/haryana-leet-counselling', 'counselling process'],
  ['LEET Counselling', '/leet-counselling', 'leet counselling'],
  ['Cutoff', '/haryana-leet-cutoff', 'cutoff'],
  ['Colleges', '/haryana-leet-colleges', 'colleges'],
  ['Seat Intake', '/haryana-leet-seat-intake', 'seat intake'],
  ['Admission Documents', '/haryana-leet-admission-documents', 'documents'],
  ['OCET Documents', '/haryana-leet-ocet-documents', 'ocet documents'],
  ['Key Dates B.Tech', '/btech-leet-key-dates', 'key dates'],
  ['LEET Overview', '/leet-overview', 'overview'],
  ['LEET Preparation Guide', '/leet-preparation-guide', 'preparation'],
  ['Tentative Dates', '/leet-tentative-dates', 'dates'],
  ['Haryana LEET 2026/2027 page', '/haryana-leet-2026', 'leet 2026, leet 2027'],
  ['Free B.Tech Sample Hub', '/btech-leet-sample-paper', 'free sample'],
  ['Free LEET Sample Hub', '/leet-sample-paper', 'sample paper']
];
for (const [name, url, kw] of leetPages) {
  addRes('LEET Info', name, 'Public LEET information page', BASE + url, kw, 'FREE');
}

// PDFs LEET
addRes('LEET PDF', 'B.Tech LEET Syllabus PDF', 'Official entrance syllabus PDF', BASE + '/pdf/B.Tech-LEET-Syllabus-2026.pdf', 'leet syllabus pdf', 'SEND THIS for LEET syllabus');
addRes('LEET PDF', 'B.Tech LE Prospectus', 'Official prospectus PDF', BASE + '/pdf/BTechLE-Prospectus-2026.pdf', 'prospectus', 'Also in Premium dashboard');
addRes('LEET PDF', 'B.Pharm OCET Syllabus', 'B.Pharmacy LE syllabus', BASE + '/pdf/Syllabus-for-OCET-of-B.Pharmacy-Lateral-Entry-2026.pdf', 'bpharma syllabus', '');
addRes('LEET PDF', 'B.Pharm Prospectus', 'B.Pharmacy prospectus', BASE + '/pdf/BPharma-BPharmaLE-Prospectus-2026.pdf', 'bpharma prospectus', '');
['A', 'B', 'C', 'D'].forEach((s) => {
  addRes('LEET PDF', 'Formula Sheet Section ' + s, 'Premium formula sheet', BASE + '/pdf/formula-sheet-LEET2026_Section_' + s + '.pdf', 'formula ' + s, 'Premium');
  addRes('LEET PDF', 'Important Topics Section ' + s, 'Important topics PDF', BASE + '/pdf/important-topic-LEET2026_Section_' + (s === 'A' ? 'A' : s.toLowerCase()) + '.pdf', 'important topics ' + s, 'Premium');
  addRes('LEET PDF', 'Cheat Sheet Section ' + s, 'Cheat sheet PDF', BASE + '/pdf/cheat-sheat-LEET2026_Section_' + (s === 'A' ? 'A' : s.toLowerCase()) + '.pdf', 'cheat sheet ' + s, 'Premium');
});

// Counseling
addRes('Counseling', 'Counseling Help Buy', '₹99 personalized counselling request', BASE + '/counseling', 'counseling help, 99 counselling', 'BUY LINK ₹99');
addRes('Counseling', 'User Counseling Dashboard', 'Track admin suggestions', BASE + '/user-counseling', 'dashboard counseling', 'After payment');

// B.Pharm
addRes('B.Pharmacy', 'B.Pharmacy LEET', 'B.Pharm lateral entry page', BASE + '/B-Pharmacy-leet', 'bpharmacy leet', '');
addRes('B.Pharmacy', 'B.Pharm Sample Papers', 'Sample paper hub', BASE + '/b-pharmacy-leet-sample-paper', 'bpharma sample', '');
addRes('B.Pharmacy', 'B.Pharm Key Dates', 'Key dates', BASE + '/b-pharmacy-leet-key-dates', 'bpharma dates', '');
for (let i = 1; i <= 6; i++) {
  addRes('B.Pharmacy', 'Bpharma Sample Paper ' + i, 'Free/sample set', BASE + '/Bpharma-sample-paper-' + i, 'bpharma paper ' + i, '');
}

// Diploma syllabus PDFs
const syllabi = [
  ['Computer Engineering', '/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf', 'cse, computer syllabus'],
  ['AI & ML', '/syllabus/18-Final-01-08-2024-Diploma-in-Artificial-Intelligence-and-Machine-Learning.pdf', 'ai ml syllabus'],
  ['Civil Engineering', '/syllabus/17-Final-01-08-2024-Diploma-in-Civil-Engineering.pdf', 'civil syllabus'],
  ['Mechanical Engineering', '/syllabus/14-Final-01-08-2024-Diploma-in-Mechanical-Engineering.pdf', 'mechanical syllabus, mech syllabus'],
  ['Electrical Engineering', '/syllabus/21-Final-01-08-2024-Diploma-in-Electrical-Engineering.pdf', 'electrical syllabus'],
  ['ECE', '/syllabus/3-Final-01-08-2024-Diploma-in-Electronics-and-Communication-Engineering.pdf', 'ece syllabus'],
  ['Automobile', '/syllabus/11-Final-01-08-2024-Diploma-in-Automobile-Engineering.pdf', 'automobile syllabus'],
  ['Automation & Robotics', '/syllabus/1-Final-01-08-2024---Diploma-in-Automation-%26-Robotics.pdf', 'automation syllabus'],
  ['Chemical', '/syllabus/16-Final-01-08-2024-Diploma-in-Chemical-Engineering.pdf', 'chemical syllabus'],
  ['Agriculture', '/syllabus/10-Final-01-08-2024-Diploma-in-Agriculture-Engineering.pdf', 'agriculture syllabus'],
  ['Ceramic', '/syllabus/12-Final-01-08-2024-Diploma-in-Ceramic-Engineering.pdf', 'ceramic syllabus'],
  ['Architecture Assistantship', '/syllabus/15-Final-01-08-2024-Diploma-in-Architecture-Assistantship.pdf', 'architecture syllabus'],
  ['Business Management', '/syllabus/19-Final-01-08-2024-Diploma-in-Business-Management.pdf', 'dbm syllabus'],
  ['Food Technology', '/syllabus/23-Final-01-08-2024-Diploma-in-Food-Technology.pdf', 'food syllabus'],
  ['Hotel Management', '/syllabus/24-Final-01-08-2024-Diploma-in-Hotel-Management.pdf', 'hotel syllabus'],
  ['Instrumentation & Control', '/syllabus/25-Final-01-08-2024-Diploma-in-Instrumentation-and-Control-Engineering.pdf', 'instrumentation syllabus'],
  ['Library Science', '/syllabus/26-Final-01-08-2024-Diploma-in-Library-and-Information-Science.pdf', 'library syllabus'],
  ['Medical Electronics', '/syllabus/27-Final-01-08-2024-Diploma-in-Medical-Electronics.pdf', 'medical electronics syllabus'],
  ['Medical Lab Technology', '/syllabus/28-Final-01-08-2024-Diploma-in-Medical-Laboratory-and-Technology.pdf', 'mlt syllabus'],
  ['Office Management', '/syllabus/29-Final-01-08-2024-Diploma-in-Office-Management-%26-Computer-Application.pdf', 'office management syllabus'],
  ['Plastic Technology', '/syllabus/30-Final-01-08-2024-Diploma-in-Plastic-Technology.pdf', 'plastic syllabus'],
  ['Fashion Design', '/syllabus/4-Final-01-08-2024-Diploma-in-Fashion-Design-(2).pdf', 'fashion design syllabus'],
  ['Fashion Technology', '/syllabus/5-Final-01-08-2024-Diploma-in-Fashion-Technology.pdf', 'fashion technology syllabus'],
  ['Textile Design', '/syllabus/6-Final-01-08-2024-Diploma-in-Textile-Design.pdf', 'textile design syllabus'],
  ['Textile Processing', '/syllabus/7-Final-01-08-2024-Diploma-in-Textile-Processing.pdf', 'textile processing syllabus'],
  ['Textile Technology', '/syllabus/8-Final-01-08-2024-Diploma-in-Textile-Technology.pdf', 'textile technology syllabus'],
  ['Tool & Die (Adv Diploma)', '/syllabus/9-Final-01-08-2024-Advanced-Diploma-in-Tool-and-Die-Making.pdf', 'tool die syllabus'],
  ['Finance Accounts Auditing', '/syllabus/22-Final-01-08-2024-Diploma-in-Finance%2C-Accounts-and-Auditing.pdf', 'faa syllabus'],
  ['D Pharmacy', '/syllabus/Study-Scheme-for-Diploma-in-Pharmacy-(ER-2020).pdf', 'd pharmacy syllabus, dpharm']
];
for (const [name, url, kw] of syllabi) {
  addRes('Diploma Syllabus PDF', name + ' Syllabus PDF', 'Official HSBTE diploma syllabus PDF', BASE + url, kw, 'Direct PDF download');
}

// PYQ branches
const branches = [
  ['Computer Engineering', 'computer-pyq', true],
  ['Mechanical Engineering', 'mech', false],
  ['Civil Engineering', 'civil', false],
  ['Electrical Engineering', 'Electrical-Engineering', false],
  ['ECE', 'ece', false],
  ['AI & ML', 'ai-ml', false],
  ['Automobile', 'Automobile', false],
  ['Automation & Robotics', 'Automation', false],
  ['Chemical', 'Chemical', false],
  ['Agriculture', 'Agriculture', false],
  ['Ceramic', 'Ceramic', false],
  ['Architectural Assistantship', 'Architectural-Assistantship', false],
  ['DBM', 'dbm', false],
  ['Food Technology', 'Food', false],
  ['Hotel Management', 'Hotel-Management', false],
  ['Instrumentation & Control', 'Instrumentation-&-Control', false],
  ['Library', 'Library', false],
  ['Medical Electronics', 'Medical-Electronics', false],
  ['Medical Lab Technology', 'Medical-Laboratory-Technology', false],
  ['Office Management', 'Office-Management', false],
  ['Plastic', 'Plastic', false],
  ['Fashion Design', 'Fashion-Design', false],
  ['Fashion Technology', 'Fashion-Technology', false],
  ['Textile Design', 'Textile-Design', false],
  ['Textile Processing', 'Textile-Processing', false],
  ['Textile Technology', 'Textile-Technology', false],
  ['FAA', 'FAA', false],
  ['Advance Diploma', 'Adv-Diploma', false],
  ['D Pharmacy', 'd-pharmacy', false]
];

for (const [name, slug, isComp] of branches) {
  addRes('PYQ Branch Hub', name + ' PYQ Hub', 'Branch landing for previous year papers', BASE + '/' + slug, name.toLowerCase() + ' pyq', 'FREE');
  const maxSem = name === 'D Pharmacy' ? 2 : name.includes('Medical Lab') ? 4 : ['DBM', 'Hotel Management', 'Library', 'Office Management', 'Agriculture', 'Ceramic', 'FAA', 'Medical Electronics'].includes(name) ? 5 : name === 'Advance Diploma' ? 4 : 6;
  for (let s = 1; s <= maxSem; s++) {
    let url;
    if (isComp) url = s === 1 ? BASE + '/computer-1-semester' : BASE + '/computer-pyq-' + s + '-semester';
    else url = BASE + '/' + slug + '-' + s;
    addRes(
      'PYQ Semester',
      name + ' Sem ' + s + ' PYQ',
      'Semester-wise previous year papers page',
      url,
      name.toLowerCase() + ' ' + s + ', ' + name.toLowerCase() + ' semester ' + s + ', ' + name.toLowerCase() + ' ' + s + 'st/' + s + 'nd/' + s + 'rd/' + s + 'th',
      'FREE — send this when user asks branch+semester'
    );
  }
}

// Free btech samples
for (let i = 1; i <= 11; i++) {
  addRes('Free LEET Samples', 'B.Tech Sample Paper ' + i, 'Free LEET style sample', BASE + '/btech-sample-paper-' + i, 'free sample ' + i, 'FREE');
}

// Section papers
['a', 'b', 'c', 'd'].forEach((sec) => {
  for (let i = 1; i <= 2; i++) {
    addRes('Section Papers', 'Section ' + sec.toUpperCase() + ' Paper ' + i, 'Section-wise practice', BASE + '/section-' + sec + '-' + i, 'section ' + sec, 'May require premium depending on page');
  }
});

// Contact / official
addRes('Support', 'WhatsApp Chat Link', 'Direct WhatsApp to admin', 'https://wa.me/919992507270', 'whatsapp, admin', '9992507270');
addRes('Support', 'Email', 'Support email', 'mailto:nishant@hsbteleet.com', 'email', 'nishant@hsbteleet.com');
addRes('Official', 'HSTES', 'Official counselling site', 'https://hstes.org.in', 'hstes official', 'Government');
addRes('Official', 'DTE Haryana', 'Directorate of Technical Education', 'http://techeduhry.gov.in/', 'dte haryana', 'Government');

// Bot rule row
addRes(
  'BOT RULE',
  'Unknown / Custom Doubt Template',
  'If user question not matched OR payment issue OR personal doubt',
  BASE + '/contact',
  'doubt, unknown, custom',
  DOUBT_REPLY.replace(/\n/g, ' | ')
);

writeCsv(
  'Sheet2_All_Pages_Resources_URLs.csv',
  ['Category', 'Name', 'Description', 'URL', 'Keywords', 'Notes'],
  resourceRows
);

// ═══════════════════════════════════════════════════════════
// OVERVIEW HTML (print to PDF)
// ═══════════════════════════════════════════════════════════
const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>hsbteleet.com — Project Overview for WhatsApp Automation</title>
<style>
  @page { size: A4; margin: 16mm; }
  * { box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; color: #0f172a; line-height: 1.55; font-size: 11.5px; }
  h1 { font-size: 22px; margin: 0 0 6px; color: #1a56db; }
  h2 { font-size: 15px; margin: 22px 0 8px; color: #1e3a8a; border-bottom: 2px solid #f59e0b; padding-bottom: 4px; }
  h3 { font-size: 12.5px; margin: 14px 0 6px; color: #0f172a; }
  .sub { color: #64748b; margin-bottom: 14px; }
  .badge { display: inline-block; background: #fef3c7; color: #92400e; font-weight: 700; padding: 2px 8px; border-radius: 999px; font-size: 10px; }
  .box { border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; margin: 10px 0; background: #f8fafc; }
  .box.gold { background: linear-gradient(135deg,#fffbeb,#fef3c7); border-color: #f59e0b; }
  .box.ultra { background: linear-gradient(135deg,#eef2ff,#e0e7ff); border-color: #6366f1; }
  .box.hi { background: #fff1f2; border-color: #fb7185; }
  table { width: 100%; border-collapse: collapse; margin: 8px 0 14px; font-size: 11px; }
  th, td { border: 1px solid #e2e8f0; padding: 6px 8px; text-align: left; vertical-align: top; }
  th { background: #1a56db; color: #fff; }
  tr:nth-child(even) td { background: #f8fafc; }
  a { color: #1a56db; word-break: break-all; }
  ul { margin: 6px 0 6px 18px; padding: 0; }
  li { margin: 3px 0; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .footer { margin-top: 24px; font-size: 10px; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 8px; }
  code { background: #e2e8f0; padding: 1px 5px; border-radius: 4px; font-size: 10.5px; }
</style>
</head>
<body>
  <div class="badge">WhatsApp Automation Kit · Project Overview</div>
  <h1>hsbteleet.com — Full Project Overview</h1>
  <p class="sub">Haryana Polytechnic (HSBTE) PYQ + Haryana LEET (B.E./B.Tech &amp; B.Pharmacy Lateral Entry) preparation platform.<br/>
  Website: <a href="${BASE}/">${BASE}</a> · WhatsApp: <a href="https://wa.me/919992507270">9992507270</a> · Email: nishant@hsbteleet.com</p>

  <h2>1. What this project is</h2>
  <div class="box">
    <p><strong>hsbteleet.com</strong> helps Haryana diploma students with:</p>
    <ul>
      <li><strong>FREE:</strong> HSBTE previous year question papers (all major branches, semester-wise), diploma syllabus PDFs, LEET information pages, some free sample papers.</li>
      <li><strong>Premium ₹99:</strong> 34 exclusive LEET full-syllabus mock papers + official syllabus/prospectus PDFs + formula/topic sheets + Rank Analysis + ad-free + lifetime.</li>
      <li><strong>Ultra Premium ₹149:</strong> Everything in Premium + AI College Predictor, Rank Predictor, Cutoff tools, AI counselling/choice-filling tools, Study Planner.</li>
      <li><strong>Counseling Help ₹99:</strong> Human expert recommendations on dashboard (separate from Premium).</li>
    </ul>
  </div>

  <h2>2. Paid plans — what is included</h2>
  <div class="grid">
    <div class="box gold">
      <h3>Premium — ₹99 (one-time, lifetime)</h3>
      <ul>
        <li>34 exclusive LEET sample papers</li>
        <li>Official Haryana LEET Syllabus PDF</li>
        <li>Official B.Tech LE Prospectus</li>
        <li>Formula sheets + important topics + cheat sheets (A–D)</li>
        <li>Rank Analysis tool</li>
        <li>100% unique questions (not free sets)</li>
        <li>Zero ads</li>
      </ul>
      <p><strong>Buy:</strong> <a href="${BASE}/premium-login?tier=premium">${BASE}/premium-login?tier=premium</a></p>
    </div>
    <div class="box ultra">
      <h3>Ultra Premium — ₹149 (one-time, lifetime)</h3>
      <ul>
        <li><strong>Everything in Premium</strong></li>
        <li>AI College Predictor (2027 analytics)</li>
        <li>Rank Predictor by marks</li>
        <li>Smart Counselling Advisor (AI)</li>
        <li>AI Choice Filling Generator</li>
        <li>Cutoff Analyzer + Choice Mistake Detector</li>
        <li>College Comparison + Upgrade Chance Calculator</li>
        <li>Mock Counselling Simulator + AI Study Planner</li>
      </ul>
      <p><strong>Buy:</strong> <a href="${BASE}/premium-login?tier=ultra">${BASE}/premium-login?tier=ultra</a></p>
      <p><strong>Tools:</strong> <a href="${BASE}/ultra-premium">${BASE}/ultra-premium</a></p>
    </div>
  </div>
  <p><em>Note:</em> Prediction tools show approximate analytics (±15%). Always verify with official HSTES counselling.</p>

  <h2>3. Important buy / access URLs</h2>
  <table>
    <tr><th>Action</th><th>URL</th></tr>
    <tr><td>Plans page (Premium vs Ultra)</td><td><a href="${BASE}/btech-leet-premium">${BASE}/btech-leet-premium</a></td></tr>
    <tr><td>Buy Premium ₹99</td><td><a href="${BASE}/premium-login?tier=premium">${BASE}/premium-login?tier=premium</a></td></tr>
    <tr><td>Buy Ultra ₹149</td><td><a href="${BASE}/premium-login?tier=ultra">${BASE}/premium-login?tier=ultra</a></td></tr>
    <tr><td>After login — Papers</td><td><a href="${BASE}/premium-papers">${BASE}/premium-papers</a></td></tr>
    <tr><td>After login — Ultra tools</td><td><a href="${BASE}/ultra-premium">${BASE}/ultra-premium</a></td></tr>
    <tr><td>Counseling Help ₹99</td><td><a href="${BASE}/counseling">${BASE}/counseling</a></td></tr>
    <tr><td>Counseling dashboard</td><td><a href="${BASE}/user-counseling">${BASE}/user-counseling</a></td></tr>
  </table>

  <h2>4. FREE resources the bot must send with correct links</h2>
  <h3>A) LEET Syllabus (when user asks “LEET syllabus”)</h3>
  <div class="box">
    <p>PDF: <a href="${BASE}/pdf/B.Tech-LEET-Syllabus-2026.pdf">${BASE}/pdf/B.Tech-LEET-Syllabus-2026.pdf</a></p>
    <p>Page: <a href="${BASE}/leet-syllabus">${BASE}/leet-syllabus</a></p>
    <p>Pattern: 90 MCQ, 90 minutes, no negative marking. Sections a(25)+b(25)+c(20)+d(20).</p>
  </div>

  <h3>B) Diploma CSE Syllabus (when user asks “CSE / Computer syllabus”)</h3>
  <div class="box">
    <p>PDF: <a href="${BASE}/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf">${BASE}/syllabus/2%20Final%2001-08-2024%20-%20Diploma%20in%20Computer%20Engineering.pdf</a></p>
    <p>All branches: <a href="${BASE}/hsbte-syllabus">${BASE}/hsbte-syllabus</a></p>
  </div>

  <h3>C) CSE Semester 1 PYQ (when user asks “CSE 1st sem paper”)</h3>
  <div class="box">
    <p>Page: <a href="${BASE}/computer-1-semester">${BASE}/computer-1-semester</a></p>
    <p>Other CSE semesters:</p>
    <ul>
      <li>Sem 2: <a href="${BASE}/computer-pyq-2-semester">${BASE}/computer-pyq-2-semester</a></li>
      <li>Sem 3: <a href="${BASE}/computer-pyq-3-semester">${BASE}/computer-pyq-3-semester</a></li>
      <li>Sem 4–6: same pattern <code>/computer-pyq-{N}-semester</code></li>
    </ul>
  </div>

  <h3>D) Generic PYQ URL pattern</h3>
  <div class="box">
    <p>Hub: <a href="${BASE}/hsbte-pyq">${BASE}/hsbte-pyq</a></p>
    <p>Most branches: <code>${BASE}/{branch}-{semester}</code> e.g. Mechanical 3 → <a href="${BASE}/mech-3">${BASE}/mech-3</a>, Civil 1 → <a href="${BASE}/civil-1">${BASE}/civil-1</a></p>
    <p>Computer is special (see above).</p>
  </div>

  <h2>5. WhatsApp bot behaviour rules</h2>
  <ol>
    <li>Match user message to <strong>Sheet1 FAQ</strong> keywords → send <em>Full_Answer</em> + links.</li>
    <li>For branch+semester PYQ → use <strong>Sheet2</strong> row (Category = PYQ Semester).</li>
    <li>For branch syllabus → use Sheet2 Diploma Syllabus PDF URL.</li>
    <li>For “buy / premium / ultra” → always include buy URLs from section 3.</li>
    <li>If unmatched / payment issue / personal doubt → send HIGH PRIORITY template below.</li>
  </ol>

  <div class="box hi">
    <h3>HIGH PRIORITY doubt reply (mandatory)</h3>
    <pre style="white-space:pre-wrap;font-family:inherit;margin:0">${DOUBT_REPLY}</pre>
  </div>

  <h2>6. Files in this kit</h2>
  <table>
    <tr><th>File</th><th>Use</th></tr>
    <tr><td><code>Sheet1_FAQ_WhatsApp_Bot.csv</code></td><td>Import to Google Sheet → FAQ / auto-replies</td></tr>
    <tr><td><code>Sheet2_All_Pages_Resources_URLs.csv</code></td><td>Import to Google Sheet → all URLs (pages, PYQ, syllabus, premium)</td></tr>
    <tr><td><code>HSBTE_LEET_Project_Overview.pdf</code></td><td>This overview for team / bot training</td></tr>
    <tr><td><code>README_WhatsApp_Bot.md</code></td><td>How to import &amp; wire automation</td></tr>
  </table>

  <h2>7. Official government sites</h2>
  <ul>
    <li>HSTES: <a href="https://hstes.org.in">https://hstes.org.in</a></li>
    <li>DTE Haryana: <a href="http://techeduhry.gov.in/">http://techeduhry.gov.in/</a></li>
  </ul>

  <div class="footer">
    Generated for WhatsApp automation · hsbteleet.com · Contact nishant@hsbteleet.com · WhatsApp 9992507270<br/>
    Premium ₹99 · Ultra Premium ₹149 · Counseling Help ₹99 · Always prefer sending official PDF/page links from the site.
  </div>
</body>
</html>`;

fs.writeFileSync(path.join(ROOT, 'HSBTE_LEET_Project_Overview.html'), html, 'utf8');
console.log('Wrote HSBTE_LEET_Project_Overview.html');

const readme = `# WhatsApp Bot Kit — hsbteleet.com

## Import to Google Sheets

1. Open [Google Sheets](https://sheets.google.com) → Blank spreadsheet.
2. **File → Import → Upload** \`Sheet1_FAQ_WhatsApp_Bot.csv\` → Import location: *Replace spreadsheet* or new sheet named **FAQ**.
3. Create second sheet / second spreadsheet → Import \`Sheet2_All_Pages_Resources_URLs.csv\` → name it **Resources**.
4. Open \`HSBTE_LEET_Project_Overview.html\` in Chrome → **Ctrl+P → Save as PDF** (or use generated PDF if present).

## Suggested bot logic

\`\`\`
IF message matches FAQ.Trigger_Keywords → send FAQ.Full_Answer
ELSE IF message has branch + semester → lookup Resources where Category=PYQ Semester
ELSE IF message has "syllabus" + branch → lookup Diploma Syllabus PDF
ELSE IF message has "leet syllabus" → send LEET PDF URL
ELSE IF message has buy/premium/ultra → send Premium/Ultra buy links
ELSE → send HIGH PRIORITY doubt template (Sheet1 Category = Doubt / Unknown)
\`\`\`

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
`;

fs.writeFileSync(path.join(ROOT, 'README_WhatsApp_Bot.md'), readme, 'utf8');
console.log('Wrote README_WhatsApp_Bot.md');
console.log('Done. FAQ rows:', faqRows.length, 'Resource rows:', resourceRows.length);
