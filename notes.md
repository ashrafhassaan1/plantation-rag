# Project notes: what I found and what went wrong

## Parsing and cleaning

### Two reports are two-page spreads
IOI (1587 x 624) and SD Guthrie (1191 x 842) have two printed pages side by side on every PDF page. KLK is normal single pages. I split each spread into a left and a right half so every chunk belongs to exactly one printed page.

### Printed page numbers differ from PDF page numbers
For the two spread reports, printed page = 2 x PDF page - 4 (left half) or - 3 (right half). KLK is PDF page - 2. I find the offset by letting every page vote on it, then check each page against it. Number confirmed on 92% (IOI), 96% (KLK) and 96% (SD Guthrie) of pages. Citations use printed page numbers, so they match what a person sees in the report.

### Page numbers sit in different places in each report
IOI prints them at the top, SD Guthrie at the bottom, and IOI moves them between narrative and financial pages. A fixed position would not work. Other digits near the edges (table values) look like page numbers, so the vote-and-verify approach was needed.

### Divider pages have no number
Pages such as KLK printed p.50 (start of the Sustainability section) carry a mini contents list and no page number. I give them the number from their neighbours and flag them as unverified.

### Repeated navigation menu text (IOI)
IOI prints a menu block (Group Overview, Key Messages, Strategic Value Creation...) on its financial pages. I removed it by matching the exact 19-line sequence, because a single word like "Group" is also a real table header. On narrative pages the menu appears in a different format, for example "Annual Report 2025 Governance Financial Report Additional Information 97 IOI CORPORATION BERHAD", and my cleaner does not catch that yet.

### Decorative and infographic pages
Slogan pages (IOI PDF page 10) contain no facts. Infographic pages (IOI PDF page 20) come out with lines repeated three times and the labels in scrambled order.

### Tables lose their structure
Every cell of a table lands on its own line, so "Share capital" is no longer connected to its numbers, and Group and Company columns are mixed together (IOI balance sheet, printed p.158). Chart pages are worse: KLK p.33-34 (planted area chart) became a jumble of axis numbers. I am keeping plain text as the baseline on purpose, so a table-aware version can later be measured against it.

### Very short pages
Some real content pages are only 300 to 600 characters (IOI p.18 is the Chairman's page). A length cutoff would delete useful pages, so I keep them and let the chunker merge them with their neighbours.

### My own mistake: wrong test page
I checked page numbers by looking for "equity and liabilities" on IOI p.159, and it failed. The page was fine. I had picked 159 from a messy text dump, and the balance sheet is actually on p.158. Lesson: verify against the page itself, not just against extracted text.

### Embedding model limit
bge-small-en-v1.5 reads at most about 512 tokens. Number-heavy table text uses many tokens per character, so a 1200-character chunk of a table may be cut off silently. Another reason to test chunk sizes.

## First search results (plain vector search, chunk size 1200, k=5)

### "Who is the Chairman of IOI Corporation?"
The right chunk (p.18-19, Tan Sri Peter Chin Fah Kui, Non-Independent Non-Executive Chairman) came 3rd. Ranked above it were director and management profiles that repeat the company name often. Right chunk, wrong rank.

### "What climate change risks does SD Guthrie identify?"
The useful chunk (p.49-50, uncertain weather conditions and global warming) came 4th, behind general sustainability text.

### "How many hectares of oil palm does KLK have planted in Indonesia?" (bad question, not bad retrieval)
The top result (p.28-29) was the right page. But the report gives only a percentage there: 57% of oil palm planted area is in Indonesia (out of 301,090 ha planted). It never states an Indonesia-only hectare figure in the text. Multiplying the percentages would give about 168,000 ha, but that is my own arithmetic on rounded numbers, so it cannot be a gold answer. Lesson: a question the document cannot answer directly makes a correct system look wrong. I rewrote it as "What share of KLK's oil palm planted area is in Indonesia?" (57%, p.28).
