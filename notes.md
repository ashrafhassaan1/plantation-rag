# Build notes

A running log of problems, decisions and surprises.

## Data

- Using 3 plantation annual reports (2025): KLK, IOI, SD Guthrie.
- IOI (1587x624) and SD Guthrie (1191x842) PDFs are two-page spreads: each PDF page holds two printed pages. KLK is normal single pages.
- Citations will use the printed page number, not the PDF page number.

## Parsing problems

- Slogan and decorative pages contain no facts (e.g. IOI PDF page 10) and add noise to search.
- Navigation menu text and "Annual Report 2025 IOI CORPORATION BERHAD" repeat on every page.
- Tables lose their structure in plain text extraction: every cell lands on its own line, and Group and Company columns get mixed together (e.g. IOI balance sheet, PDF page 81).

## Decisions

- Keep all pages in the parsed files, but tag each as keep or skip.
- Skip: notice of AGM, proxy form, shareholder statistics, Malay-language duplicate sections.


printed page = 2 × PDF page − 4 or − 3 for the two spread reports; page numbers sit in different places, so we vote and verify; the menu block is repeated on IOI's financial pages; infographic pages (like IOI page 20) come out scrambled and repeated.


divider pages have no number, so numbers are verified by voting and neighbours instead.


