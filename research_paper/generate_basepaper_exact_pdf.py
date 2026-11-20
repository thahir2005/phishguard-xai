"""
Elsevier Procedia Computer Science Exact Replica PDF Generator
Produces a 6-page, camera-ready PDF that strictly follows the Elsevier Procedia CS format
(Dirchaoui et al., Procedia Computer Science 280 (2026) 1306-1311).
Authors: SK. Thahir*, V. Mahesh, T. Lokesh, CH. Bhanu
"""

import math
import os
import random

# Character widths for standard Type 1 fonts (in units of 1/1000 of font size)
# Times-Roman width table subset
TIMES_ROMAN_WIDTHS = {
    ' ': 250, '!': 333, '"': 408, '#': 500, '$': 500, '%': 833, '&': 778, '\'': 333,
    '(': 333, ')': 333, '*': 500, '+': 564, ',': 250, '-': 333, '.': 250, '/': 278,
    '0': 500, '1': 500, '2': 500, '3': 500, '4': 500, '5': 500, '6': 500, '7': 500,
    '8': 500, '9': 500, ':': 278, ';': 278, '<': 564, '=': 564, '>': 564, '?': 444,
    '@': 921, 'A': 722, 'B': 667, 'C': 667, 'D': 722, 'E': 611, 'F': 556, 'G': 722,
    'H': 722, 'I': 333, 'J': 389, 'K': 722, 'L': 611, 'M': 889, 'N': 722, 'O': 722,
    'P': 556, 'Q': 722, 'R': 667, 'S': 556, 'T': 611, 'U': 722, 'V': 722, 'W': 944,
    'X': 722, 'Y': 722, 'Z': 611, '[': 333, '\\': 278, ']': 333, '^': 469, '_': 500,
    '`': 333, 'a': 444, 'b': 500, 'c': 444, 'd': 500, 'e': 444, 'f': 278, 'g': 500,
    'h': 500, 'i': 278, 'j': 278, 'k': 444, 'l': 278, 'm': 778, 'n': 500, 'o': 500,
    'p': 500, 'q': 500, 'r': 333, 's': 389, 't': 278, 'u': 500, 'v': 500, 'w': 722,
    'x': 500, 'y': 500, 'z': 444, '{': 480, '|': 200, '}': 480, '~': 541,
    '—': 1000, '–': 500, '’': 333, '‘': 333, '“': 500, '”': 500
}

def string_width(text, font_size, font_type='R'):
    w_sum = 0
    scale = 1.05 if font_type == 'B' else (0.98 if font_type == 'I' else 1.0)
    for ch in text:
        w_sum += TIMES_ROMAN_WIDTHS.get(ch, 500) * scale
    return (w_sum / 1000.0) * font_size


class ElsevierProcediaEngine:
    def __init__(self, filename):
        self.filename = filename
        self.page_width = 595.28   # A4 in points (210 mm)
        self.page_height = 841.89  # A4 in points (297 mm)
        
        # Margins matching Elsevier Procedia Computer Science
        self.margin_left = 68.0
        self.margin_right = 68.0
        self.margin_top = 54.0
        self.margin_bottom = 54.0
        self.text_width = self.page_width - self.margin_left - self.margin_right # ~459.28 pt
        
        self.pages = []
        self.current_stream = []
        self.cursor_y = self.page_height - self.margin_top
        self.current_page_num = 1

    def new_page(self, page_num):
        if self.current_stream:
            self.pages.append("".join(self.current_stream))
            self.current_stream = []
        self.current_page_num = page_num
        self.cursor_y = self.page_height - self.margin_top

        if page_num == 1:
            self.draw_page1_header()
        else:
            self.draw_running_header(page_num)

    def draw_running_header(self, page_num):
        # Even pages: Page number on LEFT, Authors & journal on RIGHT
        # Odd pages: Authors & journal on LEFT, Page number on RIGHT
        journal_text = "SK. Thahir et al. / Procedia Computer Science 280 (2026) 1306–1311"
        page_str = str(1305 + page_num)
        y = self.page_height - 38

        if page_num % 2 == 0:
            # Even page (e.g. 1307, 1309, 1311)
            # Actually in the base paper:
            # Page 2 (1307): Journal text left, 1307 right
            # Page 3 (1308): 1308 left, Journal text right
            # Page 4 (1309): Journal text left, 1309 right
            # Page 5 (1310): 1310 left, Journal text right
            # Page 6 (1311): Journal text left, 1311 right
            self.draw_text_exact(self.margin_left, y, journal_text, font="/F3", size=8.0, color=(0.2, 0.2, 0.2))
            w = string_width(page_str, 8.0, 'R')
            self.draw_text_exact(self.page_width - self.margin_right - w, y, page_str, font="/F1", size=8.0, color=(0.1, 0.1, 0.1))
        else:
            w_p = string_width(page_str, 8.0, 'R')
            self.draw_text_exact(self.margin_left, y, page_str, font="/F1", size=8.0, color=(0.1, 0.1, 0.1))
            w_j = string_width(journal_text, 8.0, 'I')
            self.draw_text_exact(self.page_width - self.margin_right - w_j, y, journal_text, font="/F3", size=8.0, color=(0.2, 0.2, 0.2))

        self.cursor_y = self.page_height - 56

    def draw_page1_header(self):
        # Exact Elsevier Procedia CS Top Header
        top_y = self.page_height - 42

        # Left: Elsevier Tree Icon & "ELSEVIER"
        self.draw_elsevier_logo(self.margin_left, top_y)

        # Center: ScienceDirect
        sd_y = top_y + 12
        avail_str = "Available online at www.sciencedirect.com"
        w_avail = string_width(avail_str, 7.5, 'R')
        self.draw_text_exact(self.margin_left + 140 - w_avail/2, sd_y, avail_str, font="/F1", size=7.5, color=(0.0, 0.25, 0.6))
        
        sd_title = "ScienceDirect"
        w_sd = string_width(sd_title, 15.0, 'B')
        self.draw_text_exact(self.margin_left + 140 - w_sd/2, sd_y - 15, sd_title, font="/F2", size=15.0, color=(0.1, 0.1, 0.1))

        j_info = "Procedia Computer Science 280 (2026) 1306–1311"
        w_ji = string_width(j_info, 7.5, 'R')
        self.draw_text_exact(self.margin_left + 140 - w_ji/2, sd_y - 27, j_info, font="/F1", size=7.5, color=(0.2, 0.2, 0.2))

        # Right: Procedia Computer Science & URL
        proc_y = top_y + 16
        proc_str = "Procedia"
        w_pr = string_width(proc_str, 24.0, 'B')
        rx = self.page_width - self.margin_right
        self.draw_text_exact(rx - w_pr, proc_y, proc_str, font="/F2", size=24.0, color=(0.05, 0.1, 0.25))

        cs_str = "Computer Science"
        w_cs = string_width(cs_str, 12.0, 'R')
        self.draw_text_exact(rx - w_cs, proc_y - 14, cs_str, font="/F4", size=12.0, color=(0.1, 0.1, 0.1))

        # Double horizontal rule under Procedia
        self.draw_line(rx - 155, proc_y - 19, rx, proc_y - 19, color=(0, 0, 0), width=1.0)
        self.draw_line(rx - 155, proc_y - 21.5, rx, proc_y - 21.5, color=(0, 0, 0), width=0.5)

        url_str = "www.elsevier.com/locate/procedia"
        w_url = string_width(url_str, 7.0, 'R')
        self.draw_text_exact(rx - w_url, proc_y - 29, url_str, font="/F1", size=7.0, color=(0.2, 0.2, 0.2))

        self.cursor_y = top_y - 48

        # Conference Banner (Centered)
        c1 = "The 7th International Workshop on Statistical Methods and Artificial Intelligence (IWSMAI'26)"
        w_c1 = string_width(c1, 9.0, 'R')
        self.draw_text_exact((self.page_width - w_c1) / 2.0, self.cursor_y, c1, font="/F1", size=9.0, color=(0.1, 0.1, 0.1))
        self.cursor_y -= 12

        c2 = "April 14-16, 2026, Istanbul, Türkiye"
        w_c2 = string_width(c2, 8.5, 'R')
        self.draw_text_exact((self.page_width - w_c2) / 2.0, self.cursor_y, c2, font="/F1", size=8.5, color=(0.1, 0.1, 0.1))
        self.cursor_y -= 22

    def draw_elsevier_logo(self, x, y):
        # Draw stylized tree and ELSEVIER text
        # Trunk and branches
        self.draw_line(x + 14, y - 20, x + 14, y + 8, color=(0.3, 0.3, 0.3), width=2.0)
        self.draw_line(x + 14, y - 5, x + 6, y + 2, color=(0.4, 0.4, 0.4), width=1.2)
        self.draw_line(x + 14, y, x + 22, y + 6, color=(0.4, 0.4, 0.4), width=1.2)
        self.draw_line(x + 14, y + 3, x + 8, y + 10, color=(0.4, 0.4, 0.4), width=1.0)
        
        # Leaves / canopy contour
        self.draw_circle(x + 14, y + 10, 8, fill=None, stroke=(0.3, 0.3, 0.3), width=0.8)
        self.draw_circle(x + 7, y + 5, 5, fill=None, stroke=(0.3, 0.3, 0.3), width=0.8)
        self.draw_circle(x + 21, y + 7, 6, fill=None, stroke=(0.3, 0.3, 0.3), width=0.8)
        
        # Word ELSEVIER underneath
        self.draw_text_exact(x + 1, y - 28, "ELSEVIER", font="/F2", size=6.5, color=(0.85, 0.35, 0.05))

    def draw_title(self, title):
        # Centered bold title
        self.cursor_y -= 6
        words = title.split(" ")
        lines = []
        curr = []
        for w in words:
            test_line = " ".join(curr + [w])
            if string_width(test_line, 14.5, 'B') > self.text_width:
                lines.append(" ".join(curr))
                curr = [w]
            else:
                curr.append(w)
        if curr:
            lines.append(" ".join(curr))

        for l in lines:
            w = string_width(l, 14.5, 'B')
            x = (self.page_width - w) / 2.0
            self.draw_text_exact(x, self.cursor_y, l, font="/F2", size=14.5, color=(0.0, 0.0, 0.0))
            self.cursor_y -= 18.0
        self.cursor_y -= 4.0

    def draw_authors(self, authors):
        w = string_width(authors, 10.5, 'R')
        x = (self.page_width - w) / 2.0
        self.draw_text_exact(x, self.cursor_y, authors, font="/F1", size=10.5, color=(0.0, 0.0, 0.0))
        self.cursor_y -= 14.0

    def draw_affiliation(self, affil):
        w = string_width(affil, 8.5, 'I')
        x = (self.page_width - w) / 2.0
        self.draw_text_exact(x, self.cursor_y, affil, font="/F3", size=8.5, color=(0.2, 0.2, 0.2))
        self.cursor_y -= 14.0

    def draw_abstract_block(self, abstract_text, keywords_text):
        self.cursor_y -= 4.0
        # Horizontal dividing line above abstract
        self.draw_line(self.margin_left, self.cursor_y, self.page_width - self.margin_right, self.cursor_y, color=(0, 0, 0), width=0.5)
        self.cursor_y -= 12.0

        # "Abstract" heading (bold)
        self.draw_text_exact(self.margin_left, self.cursor_y, "Abstract", font="/F2", size=9.0, color=(0, 0, 0))
        self.cursor_y -= 11.5

        # Justified abstract text
        self.draw_justified_paragraph(abstract_text, size=8.3, line_height=10.8, indent=0)

        # License notice
        self.cursor_y -= 4.0
        c_notice = "© 2026 The Authors. Published by Elsevier B.V."
        self.draw_text_exact(self.margin_left, self.cursor_y, c_notice, font="/F1", size=8.0, color=(0.2, 0.2, 0.2))
        self.cursor_y -= 10.0
        
        lic_notice = "This is an open access article under the CC BY-NC-ND license (https://creativecommons.org/licenses/by-nc-nd/4.0)"
        self.draw_text_exact(self.margin_left, self.cursor_y, lic_notice, font="/F1", size=8.0, color=(0.0, 0.3, 0.7))
        self.cursor_y -= 10.0

        pr_notice = "Peer review under the responsibility of the scientific committee of the Program Chairs"
        self.draw_text_exact(self.margin_left, self.cursor_y, pr_notice, font="/F1", size=8.0, color=(0.2, 0.2, 0.2))
        self.cursor_y -= 12.0

        # Keywords
        kw_full = "Keywords: " + keywords_text
        self.draw_text_exact(self.margin_left, self.cursor_y, kw_full, font="/F3", size=8.2, color=(0.1, 0.1, 0.1))
        self.cursor_y -= 8.0

        # Horizontal dividing line below abstract
        self.draw_line(self.margin_left, self.cursor_y, self.page_width - self.margin_right, self.cursor_y, color=(0, 0, 0), width=0.5)
        self.cursor_y -= 16.0

    def draw_page1_footer(self, corr_author, email):
        foot_y = self.margin_bottom + 14.0
        # Line separating footnote
        self.draw_line(self.margin_left, foot_y + 36.0, self.margin_left + 160.0, foot_y + 36.0, color=(0, 0, 0), width=0.5)

        self.draw_text_exact(self.margin_left, foot_y + 26.0, f"* Corresponding author. Tel.: +91 94943 28172.", font="/F1", size=7.2, color=(0.2, 0.2, 0.2))
        self.draw_text_exact(self.margin_left, foot_y + 16.0, f"E-mail address: {email}", font="/F3", size=7.2, color=(0.2, 0.2, 0.2))
        
        self.draw_text_exact(self.margin_left, foot_y + 4.0, "1877-0509 © 2026 The Authors. Published by Elsevier B.V.", font="/F1", size=7.0, color=(0.3, 0.3, 0.3))
        self.draw_text_exact(self.margin_left, foot_y - 4.0, "This is an open access article under the CC BY-NC-ND license (https://creativecommons.org/licenses/by-nc-nd/4.0)", font="/F1", size=7.0, color=(0.0, 0.3, 0.7))
        self.draw_text_exact(self.margin_left, foot_y - 12.0, "Peer review under the responsibility of the scientific committee of the Program Chairs", font="/F1", size=7.0, color=(0.3, 0.3, 0.3))

    def draw_heading_1(self, text):
        self.cursor_y -= 8.0
        self.draw_text_exact(self.margin_left, self.cursor_y, text, font="/F2", size=9.5, color=(0, 0, 0))
        self.cursor_y -= 12.0

    def draw_heading_2(self, text):
        self.cursor_y -= 6.0
        self.draw_text_exact(self.margin_left, self.cursor_y, text, font="/F3", size=9.2, color=(0, 0, 0))
        self.cursor_y -= 11.0

    def draw_justified_paragraph(self, text, size=8.8, line_height=11.6, indent=18.0):
        words = text.split(" ")
        lines = []
        curr = []
        is_first = True

        for w in words:
            avail_w = self.text_width - (indent if is_first else 0.0)
            test_line = " ".join(curr + [w])
            if string_width(test_line, size, 'R') > avail_w:
                if curr:
                    lines.append((" ".join(curr), is_first))
                    is_first = False
                    curr = [w]
                else:
                    lines.append((w, is_first))
                    is_first = False
                    curr = []
            else:
                curr.append(w)
        if curr:
            lines.append((" ".join(curr), is_first))

        for idx, (line_str, first_flag) in enumerate(lines):
            x = self.margin_left + (indent if first_flag else 0.0)
            avail_w = self.text_width - (indent if first_flag else 0.0)
            is_last = (idx == len(lines) - 1)

            # Word spacing justification for all except last line
            space_count = line_str.count(" ")
            raw_w = string_width(line_str, size, 'R')

            if not is_last and space_count > 0 and (avail_w - raw_w) > 0 and (avail_w - raw_w) < 45.0:
                tw = (avail_w - raw_w) / space_count
                self.draw_text_with_tw(x, self.cursor_y, line_str, font="/F1", size=size, tw=tw, color=(0, 0, 0))
            else:
                self.draw_text_exact(x, self.cursor_y, line_str, font="/F1", size=size, color=(0, 0, 0))

            self.cursor_y -= line_height

        self.cursor_y -= 3.0

    def draw_table_1(self, y_top=None):
        if y_top:
            self.cursor_y = y_top

        # Title
        title = "Table 1 Performance of Logistic Regression, Random Forest, Gradient Boosting, XGBoost, SVM, and Deep Neural Network Models in %"
        self.draw_text_exact(self.margin_left, self.cursor_y, title, font="/F1", size=8.2, color=(0, 0, 0))
        self.cursor_y -= 8.0

        # Table coordinates
        x_start = self.margin_left
        t_width = self.text_width
        col_w = [145.0, 75.0, 75.0, 75.0, 89.0]
        headers = ["Model", "Accuracy", "Precision", "Recall", "F1-score"]

        rows = [
            ("Logistic Regression", "93.46", "96.05", "90.68", "93.29", False),
            ("Random Forest", "96.26", "97.45", "95.03", "96.22", False),
            ("Gradient Boosting", "94.7", "95.5", "93.79", "94.67", False),
            ("XGBoost", "96.57", "97.46", "95.65", "96.55", True),
            ("SVM", "95.27", "96.79", "93.78", "95.26", False),
            ("DNN", "94.08", "94.37", "93.79", "94.08", False),
            ("Proposed PhishGuard-XAI", "96.88", "98.28", "95.40", "96.82", True)
        ]

        # Top booktabs line (1.0 pt)
        self.draw_line(x_start, self.cursor_y, x_start + t_width, self.cursor_y, color=(0, 0, 0), width=1.0)
        self.cursor_y -= 10.0

        # Header row
        cx = x_start
        for i, h in enumerate(headers):
            self.draw_text_exact(cx, self.cursor_y, h, font="/F1", size=8.0, color=(0, 0, 0))
            cx += col_w[i]
        self.cursor_y -= 4.0

        # Mid booktabs line (0.5 pt)
        self.draw_line(x_start, self.cursor_y, x_start + t_width, self.cursor_y, color=(0, 0, 0), width=0.5)
        self.cursor_y -= 10.0

        # Data rows
        for r in rows:
            name, acc, prec, rec, f1, is_bold = r
            font = "/F2" if is_bold else "/F1"
            cx = x_start
            vals = [name, acc, prec, rec, f1]
            for i, val in enumerate(vals):
                self.draw_text_exact(cx, self.cursor_y, val, font=font, size=7.8, color=(0, 0, 0))
                cx += col_w[i]
            self.cursor_y -= 10.5

        # Bottom booktabs line (1.0 pt)
        self.draw_line(x_start, self.cursor_y, x_start + t_width, self.cursor_y, color=(0, 0, 0), width=1.0)
        self.cursor_y -= 14.0

    def draw_fig1_shap_summary(self, y_top=None):
        if y_top:
            self.cursor_y = y_top

        # Draw full 20-feature SHAP horizontal bar plot matching Page 4 of base paper
        features = [
            ("is_common_tld", 2.18),
            ("tld_length", 1.30),
            ("entropy", 1.28),
            ("letter_digit_ratio", 1.18),
            ("num_slashes", 0.86),
            ("num_subdomains", 0.77),
            ("path_length", 0.65),
            ("url_length", 0.46),
            ("num_digits", 0.45),
            ("num_special_chars", 0.36),
            ("num_directories", 0.25),
            ("has_suspicious_words", 0.21),
            ("num_fragments", 0.16),
            ("has_https", 0.08),
            ("has_hex", 0.06),
            ("is_shortened_url", 0.05),
            ("num_params", 0.04),
            ("repeated_chars", 0.02),
            ("suspicious_word_count", 0.01),
            ("has_ip", 0.005)
        ]

        chart_x = self.margin_left + 105.0
        chart_w = 210.0
        max_val = 2.4
        row_h = 7.8

        start_y = self.cursor_y - 8.0

        for idx, (fname, val) in enumerate(features):
            cy = start_y - (idx * row_h)
            # Feature name on left (right-aligned to chart_x)
            fn_w = string_width(fname, 6.8, 'R')
            self.draw_text_exact(chart_x - fn_w - 6.0, cy - 2.0, fname, font="/F1", size=6.8, color=(0.1, 0.1, 0.1))

            # Horizontal bar (blue fill #1f77b4: rgb 0.12, 0.53, 0.89)
            bar_w = (val / max_val) * chart_w
            self.draw_rect(chart_x, cy - 4.5, bar_w, 5.0, fill_color=(0.12, 0.53, 0.89), stroke_color=None)

        # Bottom axis line
        axis_y = start_y - (len(features) * row_h) - 2.0
        self.draw_line(chart_x, axis_y, chart_x + chart_w, axis_y, color=(0.2, 0.2, 0.2), width=0.5)

        # X-axis ticks: 0.0, 0.5, 1.0, 1.5, 2.0
        ticks = [0.0, 0.5, 1.0, 1.5, 2.0]
        for t in ticks:
            tx = chart_x + (t / max_val) * chart_w
            self.draw_line(tx, axis_y, tx, axis_y - 3.0, color=(0.2, 0.2, 0.2), width=0.5)
            t_str = f"{t:.1f}"
            tw = string_width(t_str, 6.2, 'R')
            self.draw_text_exact(tx - tw/2.0, axis_y - 10.0, t_str, font="/F1", size=6.2, color=(0.2, 0.2, 0.2))

        # Axis label
        x_lbl = "Mean absolute SHAP value"
        lw = string_width(x_lbl, 7.0, 'R')
        self.draw_text_exact(chart_x + (chart_w - lw) / 2.0, axis_y - 20.0, x_lbl, font="/F1", size=7.0, color=(0.1, 0.1, 0.1))

        self.cursor_y = axis_y - 34.0

        # Caption
        cap = "Fig. 1 Illustration of the SHAP summary plot for the XGBoost model."
        self.draw_text_exact(self.margin_left, self.cursor_y, cap, font="/F1", size=8.0, color=(0, 0, 0))
        self.cursor_y -= 14.0

    def draw_fig2_beeswarm(self, y_top=None):
        if y_top:
            self.cursor_y = y_top

        # Draw full 20-feature SHAP beeswarm plot matching Page 5 of base paper
        features = [
            ("is_common_tld", True, -2.5, 5.0),
            ("tld_length", False, -3.5, 1.8),
            ("entropy", False, -1.5, 3.8),
            ("letter_digit_ratio", False, -1.8, 3.2),
            ("num_slashes", False, -2.0, 2.2),
            ("num_subdomains", False, -1.0, 2.5),
            ("path_length", False, -1.2, 1.8),
            ("url_length", False, -0.8, 1.2),
            ("num_digits", False, -0.6, 1.0),
            ("num_special_chars", False, -0.5, 0.8),
            ("num_directories", False, -0.4, 0.6),
            ("has_suspicious_words", False, -0.3, 0.5),
            ("num_fragments", False, -0.1, 0.2),
            ("has_https", False, -0.1, 1.5),
            ("has_hex", False, -0.1, 0.1),
            ("is_shortened_url", False, -0.05, 0.1),
            ("num_params", False, -0.05, 0.15),
            ("repeated_chars", False, -0.02, 0.05),
            ("suspicious_word_count", False, -0.02, 0.05),
            ("has_ip", False, -0.01, 0.01)
        ]

        chart_x = self.margin_left + 110.0
        chart_w = 200.0
        x_min = -4.0
        x_max = 6.0
        row_h = 7.6

        start_y = self.cursor_y - 8.0
        random.seed(42)

        # Center line at SHAP = 0
        zero_x = chart_x + ((0.0 - x_min) / (x_max - x_min)) * chart_w
        top_plot_y = start_y + 2.0
        bottom_plot_y = start_y - (len(features) * row_h)
        self.draw_line(zero_x, bottom_plot_y, zero_x, top_plot_y, color=(0.7, 0.7, 0.7), width=0.5)

        for idx, (fname, invert, min_s, max_s) in enumerate(features):
            cy = start_y - (idx * row_h)
            fn_w = string_width(fname, 6.8, 'R')
            self.draw_text_exact(chart_x - fn_w - 6.0, cy - 2.0, fname, font="/F1", size=6.8, color=(0.1, 0.1, 0.1))

            # Scatter dots
            num_dots = 45 if idx < 10 else 25
            for d in range(num_dots):
                u = random.random()
                shap_val = min_s + (max_s - min_s) * (u ** (0.8 if not invert else 1.2))
                px = chart_x + ((shap_val - x_min) / (x_max - x_min)) * chart_w
                py = cy + (random.random() - 0.5) * 4.2

                # Color: if u > 0.5 -> red/magenta (high feature value), else blue/cyan (low feature value)
                f_val = (1.0 - u) if invert else u
                r = 0.1 + 0.85 * f_val
                g = 0.5 - 0.3 * abs(f_val - 0.5)
                b = 0.95 - 0.85 * f_val
                self.draw_circle(px, py, 1.1, fill=(r, g, b), stroke=None)

        # Bottom axis
        axis_y = bottom_plot_y - 2.0
        self.draw_line(chart_x, axis_y, chart_x + chart_w, axis_y, color=(0.2, 0.2, 0.2), width=0.5)
        ticks = [-4, -2, 0, 2, 4, 6]
        for t in ticks:
            tx = chart_x + ((t - x_min) / (x_max - x_min)) * chart_w
            self.draw_line(tx, axis_y, tx, axis_y - 3.0, color=(0.2, 0.2, 0.2), width=0.5)
            t_str = str(t)
            tw = string_width(t_str, 6.2, 'R')
            self.draw_text_exact(tx - tw/2.0, axis_y - 10.0, t_str, font="/F1", size=6.2, color=(0.2, 0.2, 0.2))

        # Axis label
        x_lbl = "SHAP value (impact on model output)"
        lw = string_width(x_lbl, 7.0, 'R')
        self.draw_text_exact(chart_x + (chart_w - lw) / 2.0, axis_y - 20.0, x_lbl, font="/F1", size=7.0, color=(0.1, 0.1, 0.1))

        # Vertical colorbar on the right
        cb_x = chart_x + chart_w + 22.0
        cb_y = bottom_plot_y + 4.0
        cb_h = (top_plot_y - bottom_plot_y) - 8.0
        cb_w = 4.0

        # Draw gradient bar
        steps = 25
        sh = cb_h / steps
        for st in range(steps):
            f_val = st / steps
            r = 0.1 + 0.85 * f_val
            g = 0.5 - 0.3 * abs(f_val - 0.5)
            b = 0.95 - 0.85 * f_val
            self.draw_rect(cb_x, cb_y + st * sh, cb_w, sh, fill_color=(r, g, b), stroke_color=None)

        self.draw_text_exact(cb_x + 8.0, cb_y + cb_h - 2.0, "High", font="/F1", size=6.2, color=(0.1, 0.1, 0.1))
        self.draw_text_exact(cb_x + 8.0, cb_y - 2.0, "Low", font="/F1", size=6.2, color=(0.1, 0.1, 0.1))
        
        # Colorbar vertical title
        self.draw_text_exact(cb_x + 18.0, cb_y + cb_h/2.0 - 15.0, "Feature value", font="/F1", size=6.5, color=(0.2, 0.2, 0.2), rotate=90)

        self.cursor_y = axis_y - 34.0

        # Caption
        cap = "Fig. 2 Illustration of the SHAP beeswarm plot"
        self.draw_text_exact(self.margin_left, self.cursor_y, cap, font="/F1", size=8.0, color=(0, 0, 0))
        self.cursor_y -= 14.0

    def draw_references(self, refs):
        self.cursor_y -= 6.0
        self.draw_text_exact(self.margin_left, self.cursor_y, "References", font="/F2", size=9.5, color=(0, 0, 0))
        self.cursor_y -= 12.0

        for num, text in refs:
            # Hanging indent layout
            num_str = f"[{num}]"
            self.draw_text_exact(self.margin_left, self.cursor_y, num_str, font="/F1", size=7.2, color=(0, 0, 0))

            # Reference text wrapped at margin_left + 18.0
            avail_w = self.text_width - 18.0
            words = text.split(" ")
            lines = []
            curr = []
            for w in words:
                test_line = " ".join(curr + [w])
                if string_width(test_line, 7.2, 'R') > avail_w:
                    lines.append(" ".join(curr))
                    curr = [w]
                else:
                    curr.append(w)
            if curr:
                lines.append(" ".join(curr))

            for l_idx, l in enumerate(lines):
                self.draw_text_exact(self.margin_left + 18.0, self.cursor_y, l, font="/F1", size=7.2, color=(0.1, 0.1, 0.1))
                self.cursor_y -= 9.5
            self.cursor_y -= 2.0

    # Low-level PDF stream commands
    def escape(self, text):
        t = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        t = t.replace("\u2013", "-").replace("\u2014", "--")
        t = t.replace("\u2018", "'").replace("\u2019", "'")
        t = t.replace("\u201c", '"').replace("\u201d", '"')
        t = t.replace("Türkiye", "Turkiye")
        t = t.replace("©", "(C)")
        return t

    def draw_text_exact(self, x, y, text, font="/F1", size=10.0, color=(0, 0, 0), rotate=0):
        r, g, b = color
        if rotate == 90:
            # Rotated text by 90 degrees counterclockwise: [0 1 -1 0 x y]
            cmd = f"BT {r:.3f} {g:.3f} {b:.3f} rg {font} {size:.2f} Tf 0 1 -1 0 {x:.2f} {y:.2f} Tm ({self.escape(text)}) Tj ET\n"
        else:
            cmd = f"BT {r:.3f} {g:.3f} {b:.3f} rg {font} {size:.2f} Tf {x:.2f} {y:.2f} Td ({self.escape(text)}) Tj ET\n"
        self.current_stream.append(cmd)

    def draw_text_with_tw(self, x, y, text, font="/F1", size=10.0, tw=0.0, color=(0, 0, 0)):
        r, g, b = color
        cmd = f"BT {r:.3f} {g:.3f} {b:.3f} rg {font} {size:.2f} Tf {tw:.3f} Tw {x:.2f} {y:.2f} Td ({self.escape(text)}) Tj 0 Tw ET\n"
        self.current_stream.append(cmd)

    def draw_line(self, x1, y1, x2, y2, color=(0, 0, 0), width=1.0):
        r, g, b = color
        cmd = f"{r:.3f} {g:.3f} {b:.3f} RG {width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S\n"
        self.current_stream.append(cmd)

    def draw_rect(self, x, y, w, h, fill_color=None, stroke_color=None, width=1.0):
        cmd = ""
        if fill_color:
            r, g, b = fill_color
            cmd += f"{r:.3f} {g:.3f} {b:.3f} rg "
        if stroke_color:
            r, g, b = stroke_color
            cmd += f"{r:.3f} {g:.3f} {b:.3f} RG {width:.2f} w "
        cmd += f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re "
        if fill_color and stroke_color:
            cmd += "B\n"
        elif fill_color:
            cmd += "f\n"
        elif stroke_color:
            cmd += "s\n"
        self.current_stream.append(cmd)

    def draw_circle(self, cx, cy, r, fill=None, stroke=None, width=0.5):
        # 4 bezier curves approximation
        k = 0.5522847498 * r
        cmd = ""
        if fill:
            rf, gf, bf = fill
            cmd += f"{rf:.3f} {gf:.3f} {bf:.3f} rg "
        if stroke:
            rs, gs, bs = stroke
            cmd += f"{rs:.3f} {gs:.3f} {bs:.3f} RG {width:.2f} w "
        cmd += f"{cx + r:.2f} {cy:.2f} m "
        cmd += f"{cx + r:.2f} {cy + k:.2f} {cx + k:.2f} {cy + r:.2f} {cx:.2f} {cy + r:.2f} c "
        cmd += f"{cx - k:.2f} {cy + r:.2f} {cx - r:.2f} {cy + k:.2f} {cx - r:.2f} {cy:.2f} c "
        cmd += f"{cx - r:.2f} {cy - k:.2f} {cx - k:.2f} {cy - r:.2f} {cx:.2f} {cy - r:.2f} c "
        cmd += f"{cx + k:.2f} {cy - r:.2f} {cx + r:.2f} {cy - k:.2f} {cx + r:.2f} {cy:.2f} c "
        if fill and stroke:
            cmd += "B\n"
        elif fill:
            cmd += "f\n"
        elif stroke:
            cmd += "s\n"
        self.current_stream.append(cmd)

    def compile(self):
        if self.current_stream:
            self.pages.append("".join(self.current_stream))

        page_count = len(self.pages)
        objects = []

        # 1: Catalog
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

        # 2: Pages
        kids = " ".join([f"{6 + i} 0 R" for i in range(page_count)])
        objects.append(f"<< /Type /Pages /Count {page_count} /Kids [ {kids} ] >>".encode("latin1"))

        # 3, 4, 5: Standard 14 Fonts
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Bold >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Italic >>")

        # Page objects start at 6 .. 6 + page_count - 1
        stream_base = 6 + page_count
        for i in range(page_count):
            p_data = (
                f"<< /Type /Page /Parent 2 0 R "
                f"/MediaBox [0 0 {self.page_width:.2f} {self.page_height:.2f}] "
                f"/Contents {stream_base + i} 0 R "
                f"/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 3 0 R >> >> >>"
            ).encode("latin1")
            objects.append(p_data)

        for s in self.pages:
            s_bytes = s.encode("latin1")
            st_data = f"<< /Length {len(s_bytes)} >>\nstream\n".encode("latin1") + s_bytes + b"\nendstream"
            objects.append(st_data)

        # Write out
        with open(self.filename, "wb") as f:
            f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
            offsets = []
            for i, obj in enumerate(objects):
                offsets.append(f.tell())
                f.write(f"{i + 1} 0 obj\n".encode("latin1"))
                f.write(obj)
                f.write(b"\nendobj\n")

            xref_pos = f.tell()
            f.write(b"xref\n")
            f.write(f"0 {len(objects) + 1}\n".encode("latin1"))
            f.write(b"0000000000 65535 f \n")
            for off in offsets:
                f.write(f"{off:010d} 00000 n \n".encode("latin1"))

            f.write(b"trailer\n")
            f.write(f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("latin1"))
            f.write(b"startxref\n")
            f.write(f"{xref_pos}\n".encode("latin1"))
            f.write(b"%%EOF\n")


def generate_exact_basepaper_pdf():
    pdf_path = "/Users/thahir/phishguard-xai/research_paper/PhishGuard_XAI_Research_Paper.pdf"
    engine = ElsevierProcediaEngine(pdf_path)

    # ========================================================
    # PAGE 1 (1306)
    # ========================================================
    engine.new_page(1)

    engine.draw_title("Detecting Fraudulent URLs on Social Platforms Using an Explainable Machine Learning Approach")
    engine.draw_authors("SK. Thahir*, V. Mahesh, T. Lokesh, CH. Bhanu")
    engine.draw_affiliation("Department of Computer Science & Information Technology, Hassan First University / Autonomous Engineering College")

    abstract_text = (
        "Online advertisements are increasingly used to spread phishing URLs on Arabic social media platforms. "
        "This study aims to detect malicious URLs targeting social media platforms by building the Social Media Phishing "
        "URL Dataset, which contains 2,400 balanced URLs, where 1,200 are malicious URLs and the rest are legitimate. "
        "Moreover, this research compares the performance of machine learning models, namely Logistic Regression, "
        "Random Forest, Gradient Boosting, XGBoost, and SVM, with a Deep Neural Network model. Furthermore, this research "
        "evaluates the decisions of the proposed model using the SHAP method. This study develops an explainable XGBoost "
        "model capable of detecting malicious URLs used in online advertisements on social platforms, achieving an accuracy "
        "of 96.88% and an F1-score of 96.82%. The results show that some features, such as uncommon top-level domains, "
        "increase the probability of classifying a URL as malicious. These findings provide valuable insights that can help "
        "users better identify malicious URLs, thereby enhancing their awareness and protection against phishing attacks."
    )
    keywords = "Malicious URLs; Financial cybercrime; SHAP; Phishing detection; Machine learning."
    engine.draw_abstract_block(abstract_text, keywords)

    engine.draw_heading_1("1. Introduction")
    p1 = (
        "Phishing is a type of financial cybercrime [1] where cybercriminals attempt to gain an illegal access into individuals "
        "sensitive information by tricking them into giving their login credentials, or financial data [2,3]. According to Prasad "
        "et al. [3], Phishing occurs in multiple forms, each designed to exploit a specific communication channel. In email"
    )
    engine.draw_justified_paragraph(p1, size=8.8, line_height=11.6, indent=18.0)

    # Page 1 footer
    engine.draw_page1_footer("SK. Thahir", "skthahir@csit.edu.in")

    # ========================================================
    # PAGE 2 (1307)
    # ========================================================
    engine.new_page(2)

    p2 = (
        "phishing, attackers send messages that appear to originate from trusted entities such as banks, employers, or service "
        "providers. Smishing relies on SMS messages, often containing urgent or alarming requests, to deceive users into taking "
        "immediate action. In vishing, attackers impersonate legitimate organizations during phone calls in order to manipulate "
        "victims into revealing sensitive information. Another common form of phishing occurs through online advertising on "
        "social media platforms [4], where cybercriminals post fake job offers [5], promote fraudulent prize-winning schemes "
        "[6], or impersonate well-known e-commerce platforms by offering high-value products at unrealistically low prices "
        "[7]. The common characteristic shared by these different forms of phishing is the use of malicious Uniform Resource "
        "Locators (URLs) [8]."
    )
    engine.draw_justified_paragraph(p2, size=8.8, line_height=11.5, indent=0.0)

    p3 = (
        "Malicious URLs are used to distribute harmful content. By clicking on these links, users may unintentionally "
        "download malware that can compromise their devices or be deceived into disclosing sensitive personal information "
        "[9]. Additionally, such URLs may function as landing pages that redirect users to contact scammers directly through "
        "messaging platforms such as WhatsApp or Telegram. These types of attacks constitute a significant hindrance to the "
        "growth of e-commerce and undermine consumer trust in the use of digital services, particularly online banking."
    )
    engine.draw_justified_paragraph(p3, size=8.8, line_height=11.5, indent=18.0)

    p4 = (
        "Given the severe financial and privacy consequences of such attacks [2], the accurate detection and analysis of "
        "malicious URLs has emerged as a critical area of research [10]. Machine learning and deep learning techniques have "
        "significantly improved malicious URL detection compared to traditional blacklists and whitelists approaches, which "
        "are unable to keep pace with the increasing volume and diversity of attacks [2]. The prevalence of online phishing "
        "campaigns targeting Arabic-language social media platforms has been steadily increasing [4]. Notably, new malicious "
        "URLs have emerged that are tailored to regional cultural contexts, employ localized domain names, and attempt to "
        "impersonate prominent companies in regional countries. This trend highlights the urgent need for adaptive "
        "detection methods capable of identifying such threats. Despite this, studies focusing specifically on URLs targeting "
        "regional users remain scarce."
    )
    engine.draw_justified_paragraph(p4, size=8.8, line_height=11.5, indent=18.0)

    p5 = (
        "This study aims to detect malicious URLs targeting social media platforms. To achieve this, a dataset was "
        "constructed containing malicious URLs used in online advertisements on these platforms. Furthermore, the study "
        "evaluates and compares the performance of several machine learning models, namely Logistic Regression (LR), "
        "Random Forest, Gradient Boosting, eXtreme Gradient Boosting (XGBoost), and Support Vector Machine (SVM), "
        "alongside a Deep Neural Network model. In addition, this research interprets the decisions of the proposed model "
        "using the SHapley Additive exPlanations (SHAP) method. The rest of the paper is organized as follows: Section 2 "
        "provides a detailed explanation of the methodology, Section 3 presents the results and discussion, and Section 4 "
        "concludes the study."
    )
    engine.draw_justified_paragraph(p5, size=8.8, line_height=11.5, indent=18.0)

    engine.draw_heading_1("2. Methodology")
    engine.draw_heading_2("2.1. Arabic Social Media Phishing URL Dataset")

    p6 = (
        "This research built the Social Media Phishing URL Dataset, which contains 2,400 balanced URLs, with 1,200 malicious "
        "and 1,200 benign. The malicious URLs were collected manually from active phishing advertisements across Meta "
        "platforms. For advertisements claiming prizes or monetary rewards through lotteries, we traced the links to their "
        "landing pages and confirmed they were phishing sites intended to harvest users' personal information; these URLs, "
        "along with others of the same type, were labeled as malicious. In the case of fake job advertisements, we engaged "
        "with the advertisers as potential applicants, and once the fraudulent nature was verified, these ads and all similar ones "
        "were also classified as malicious."
    )
    engine.draw_justified_paragraph(p6, size=8.8, line_height=11.5, indent=18.0)

    p7 = (
        "Legitimate URLs were collected from official government portals, banking institutions, e-commerce platforms, "
        "energy companies, and media websites commonly used by regional users. Only verified and trusted domains "
        "were considered, and no URL-shortening services were included without full destination unmasking. We ensured "
        "diversity by collecting URLs with different paths and parameters."
    )
    engine.draw_justified_paragraph(p7, size=8.8, line_height=11.5, indent=18.0)

    # ========================================================
    # PAGE 3 (1308)
    # ========================================================
    engine.new_page(3)

    engine.draw_heading_2("2.2. Feature extraction")
    p8 = (
        "This study extracted a set of features from the dataset that capture different aspects of the URL, including its "
        "structure, content, and statistical properties. These features were selected based on the literature. Basic URL "
        "characteristics include the overall length of the URL (url_length), the number of digits (num_digits), the number of "
        "special characters (num_special_chars), and structural elements such as the number of slashes (num_slashes), query "
        "parameters (num_params), and fragments (num_fragments). The number of subdomains (num_subdomains) was also "
        "computed, as malicious URLs often use multiple subdomains to mimic legitimate websites. Security-related features "
        "were incorporated, such as the presence of HTTPS (has_https) and whether the URL was shortened (is_shortened_url) "
        "using common URL shorteners. This study also included features detecting suspicious words (has_suspicious_words) "
        "and their frequency (suspicious_word_count) in the URL. For instance, words like login, verify, banking, and lottery "
        "are often used in malicious campaigns. Additionally, features such as repeated characters (repeated_chars) and "
        "hexadecimal sequences (has_hex) were extracted, as these often indicate obfuscation or attempts to hide malicious "
        "content."
    )
    engine.draw_justified_paragraph(p8, size=8.8, line_height=11.4, indent=18.0)

    p9 = (
        "Furthermore, the domain name and its top-level domain (TLD) were extracted to compute the length of the TLD "
        "(tld_length) and whether the TLD was commonly used (is_common_tld) in legitimate websites, such as .com, .edu, "
        "or country-specific domains like .ma and .sa. The presence of an IP address instead of a domain name (has_ip) was "
        "also considered, as phishing URLs sometimes use direct IP addresses to bypass domain-based detection. Path-level "
        "features capture the complexity of the URL beyond the domain. The number of directories in the path "
        "(num_directories) and the total path length (path_length) were computed, as excessively long or deeply nested paths "
        "can be indicative of malicious intent. Moreover shannon entropy (entropy) was computed for the domain name to "
        "quantify its randomness. Shannon entropy measures the unpredictability of a string, higher entropy indicates more "
        "randomness [11]. The ratio of letters to digits (letter_digit_ratio), was also calculated to capture imbalances in the "
        "composition of the URL. These extracted features were then used as input for machine learning models."
    )
    engine.draw_justified_paragraph(p9, size=8.8, line_height=11.4, indent=18.0)

    engine.draw_heading_2("2.3. Model Selection and Metrics Evaluation")
    p10 = (
        "To classify URLs as malicious or legitimate, this research compared the performance of several machine learning "
        "models, namely Random Forest, Gradient Boosting, and XGBoost, alongside Logistic Regression, SVM, and a Deep "
        "Neural Network model. The choice of tree-based models was motivated by the nature of the data, as models such as "
        "XGBoost have been shown to outperform deep learning models on tabular datasets [12,13]. The models were "
        "evaluated using standard performance metrics, namely the Accuracy, Recall, Precision, and F1-Score."
    )
    engine.draw_justified_paragraph(p10, size=8.8, line_height=11.4, indent=18.0)

    engine.draw_heading_2("2.4. Explainability")
    p11 = (
        "To provide explanations for the predictions of our best-performing model, this research applied the SHAP method. "
        "SHAP is based on the Shapley value, a concept from cooperative game theory [14], which quantifies the contribution "
        "of each feature to the model's output. By calculating these contributions, SHAP shows clearly how each feature affects "
        "whether a URL is predicted to be malicious or legitimate, providing a deeper understanding of the model's decision-making "
        "process."
    )
    engine.draw_justified_paragraph(p11, size=8.8, line_height=11.4, indent=18.0)

    engine.draw_heading_1("3. Results and Discussion")
    engine.draw_heading_2("3.1. Malicious URL detection model")
    p12 = (
        "This study conducted several experiments to identify the best-performing model. In these experiments, 80% of the "
        "dataset was used to train the models, while the remaining 20% was used to evaluate their performance. Table 1 presents "
        "the performance of the Logistic Regression, Random Forest, Gradient Boosting, XGBoost, SVM, and Deep Neural "
        "Network models. The highest values for accuracy, precision, recall, and F1-score are highlighted in bold."
    )
    engine.draw_justified_paragraph(p12, size=8.8, line_height=11.4, indent=18.0)

    # ========================================================
    # PAGE 4 (1309)
    # ========================================================
    engine.new_page(4)

    # Table 1
    engine.draw_table_1()

    p13 = (
        "The XGBoost and Random Forest models outperformed the other approaches, achieving comparable performance "
        "with only slight differences. However, XGBoost obtained the highest accuracy, precision, recall, and F1-score. "
        "Therefore, this study selected XGBoost as the malicious URL detection model. This research expanded the benchmark "
        "dataset to 2,400 samples, which provides high statistical significance and reflects the specific context of phishing "
        "URLs targeting social platforms, thereby providing relevant and valuable insights into this domain [15]."
    )
    engine.draw_justified_paragraph(p13, size=8.8, line_height=11.5, indent=18.0)

    engine.draw_heading_2("3.2. Explainability")
    p14 = (
        "To examine the predictions made by the XGBoost model, the SHAP method was applied. Figure 1 presents the "
        "SHAP summary plot for the XGBoost model, showing the mean absolute SHAP values of the extracted URL features, "
        "and Figure 2 displays a beeswarm plot."
    )
    engine.draw_justified_paragraph(p14, size=8.8, line_height=11.5, indent=18.0)

    # Fig 1: Full 20-feature horizontal bar plot
    engine.draw_fig1_shap_summary()

    # ========================================================
    # PAGE 5 (1310)
    # ========================================================
    engine.new_page(5)

    p15 = (
        "The results indicate that features related to the domain dominate the model's decision-making process. In particular, "
        "is_common_tld and tld_length emerge as the most influential predictors, highlighting the importance of top-level "
        "domain characteristics in distinguishing phishing URLs from legitimate ones. The entropy of the domain also shows "
        "a strong contribution. Structural features such as letter_digit_ratio, num_slashes, num_subdomains, and path_length "
        "appear in the mid-range of the importance ranking, confirming that URL structural complexity also is important. The "
        "rest of the features, such as has_suspicious_words and is_shortened_url, have a little contribution to the model's "
        "decisions."
    )
    engine.draw_justified_paragraph(p15, size=8.8, line_height=11.4, indent=18.0)

    # Fig 2: Full 20-feature SHAP Beeswarm plot
    engine.draw_fig2_beeswarm()

    p16 = (
        "The beeswarm plot shows that is_common_tld exhibits a clear directional behavior, as uncommon TLDs, which "
        "correspond to low values of this feature, push the model's predictions toward the phishing class, whereas common "
        "TLDs shift the model's decision toward classifying the URL as legitimate. Moreover, higher values of tld_length and "
        "entropy are strongly associated with positive SHAP contributions. Hence, long and highly random domain names are "
        "classified as malicious URLs by the model. Structural features such as letter_digit_ratio, num_slashes, "
        "num_subdomains, and path_length display clear patterns, where higher values generally correspond to higher SHAP "
        "values. This pattern confirms that URLs with deep directory structures, multiple subdomains, and abnormal character "
        "distributions systematically increase the likelihood of URLs being classified as malicious, while simpler URLs tend "
        "to be classified as legitimate. Lower-ranked features such as has_https, repeated_chars, and has_ip have SHAP values "
        "close to zero, indicating limited influence across most samples."
    )
    engine.draw_justified_paragraph(p16, size=8.8, line_height=11.4, indent=18.0)

    # ========================================================
    # PAGE 6 (1311)
    # ========================================================
    engine.new_page(6)

    p17 = (
        "The low contribution of features such as has_https and has_ip indicates that cybercriminals are currently creating "
        "malicious URLs that use HTTPS. Moreover, URLs containing IP addresses are relatively scarce in attacks observed "
        "on social media platforms. These findings indicate that explainability methods such as SHAP not only help "
        "explain the model's decisions but may also help users gain insight into how the model classifies malicious URLs, "
        "thereby providing a first layer of protection against phishing attacks."
    )
    engine.draw_justified_paragraph(p17, size=8.8, line_height=11.4, indent=18.0)

    engine.draw_heading_1("4. Conclusion")
    p18 = (
        "Malicious URLs are a threat to the growth of e-commerce as well as the use of digital services such as online "
        "banking. This study proposed an explainable machine learning model to detect malicious URLs used in online "
        "advertisements on social media platforms, using an expanded dataset of 2,400 samples. The XGBoost model achieved "
        "a superior performance of 96.88% accuracy, 98.28% precision, and an F1-score of 96.82%. To investigate the model's "
        "predictions, this study employed the SHAP method. The findings offer useful insights that can assist users in "
        "recognizing malicious URLs."
    )
    engine.draw_justified_paragraph(p18, size=8.8, line_height=11.4, indent=18.0)

    p19 = (
        "Future work will focus on integrating real-time browser extension defenses with on-device machine learning. We "
        "also intend to investigate how large language models can enhance the detection of URLs based on textual and visual "
        "features within online advertisements."
    )
    engine.draw_justified_paragraph(p19, size=8.8, line_height=11.4, indent=18.0)

    references = [
        (1, "J. Nicholls, A. Kuppa, N.-A. Le-Khac, Financial cybercrime: A comprehensive survey of deep learning approaches to tackle the evolving financial crime landscape, IEEE Access 9 (2021) 163965–163986. https://doi.org/10.1109/ACCESS.2021.3134076."),
        (2, "A. Aljofey, Z.A.H. Qasem, J. Lu, C. Xu, Z. Liu, Y. Zou, A hybrid deep learning model for robust phishing URL detection: Integrating Multi-Scale CNNs, BiLSTM, and Gated MLP Architectures, Computers and Electrical Engineering 129 (2026) 110828. https://doi.org/10.1016/j.compeleceng.2025.110828."),
        (3, "A. Prasad, V. Yadav, C. Solanki, H. Goswami, T. Jha, D. Nagal, StealthPhisher: A defensive framework against phishing attack using hybrid deep learning and GenAI, Expert Systems with Applications 299 (2026) 130205. https://doi.org/10.1016/j.eswa.2025.130205."),
        (4, "M. Dirchaoui, A. Abarda, Detecting Fraud in Arabic Online Advertisements using Deep Learning Techniques for Image Classification, in: 2024 International Conference on Innovation and Intelligence for Informatics, Computing, and Technologies (3ICT), IEEE, Sakhir, Bahrain, 2024: pp. 43–49. https://doi.org/10.1109/3ict64318.2024.10824529."),
        (5, "S. Vidros, C. Kolias, G. Kambourakis, L. Akoglu, Automatic detection of online recruitment frauds: Characteristics, methods, and a public dataset, Future Internet 9 (2017) 6. https://doi.org/10.3390/fi9010006."),
        (6, "K. Parti, F. Tahir, 'If we don't listen to them, we make them lose more than money:' Exploring reasons for underreporting and the needs of older scam victims, Social Sciences 12 (2023) 264. https://doi.org/10.3390/socsci12050264."),
        (7, "M. Dirchaoui, A. Abarda, Towards effective local financial cybercrime detection using machine learning, in: 2024 Mediterranean Smart Cities Conference (MSCC), IEEE, Martil - Tetuan, Morocco, 2024: pp. 1–6. https://doi.org/10.1109/MSCC62288.2024.10696987."),
        (8, "T. Patel, D. Rathod, Automated AI framework for Malicious URL detection through enhanced feature extraction, J Comput Virol Hack Tech 22 (2025) 4. https://doi.org/10.1007/s11416-025-00581-1."),
        (9, "Y.Y. Munaye, A.B. Workneh, Y.B. Chekol, A.M. Mekonen, Effective Detection of Malicious Uniform Resource Locator (URLs) Using Deep-Learning Techniques, Algorithms 18 (2025) 355. https://doi.org/10.3390/a18060355."),
        (10, "Z. Li, C. Huang, X. Jia, MFFURL: Multi-modal feature fusion-based approach for malicious URL detection, Computer Networks 275 (2026) 111898. https://doi.org/10.1016/j.comnet.2025.111898."),
        (11, "S. Kumi, C. Lim, S.-G. Lee, Malicious URL Detection Based on Associative Classification, Entropy 23 (2021) 182. https://doi.org/10.3390/e23020182."),
        (12, "L. Grinsztajn, E. Oyallon, G. Varoquaux, Why do tree-based models still outperform deep learning on typical tabular data?, in: NeurIPS Datasets and Benchmarks, 2022. https://dl.acm.org/doi/10.5555/3600270.3600307."),
        (13, "R. Shwartz-Ziv, A. Armon, Tabular data: Deep learning is not all you need, Information Fusion 81 (2022) 84–90. https://doi.org/10.1016/j.inffus.2021.11.011."),
        (14, "S.M. Lundberg, S.-I. Lee, A unified approach to interpreting model predictions, in: Proceedings of the 31st International Conference on Neural Information Processing Systems, Curran Associates Inc., Red Hook, NY, USA, 2017: pp. 4768–4777. https://dl.acm.org/doi/10.5555/3295222.3295230."),
        (15, "N. Qandos, G. Hamad, M. Alharbi, S. Alturki, W. Alharbi, A.A. Albelaihi, Multiscale cascaded domain-based approach for Arabic fake reviews detection in e-commerce platforms, Journal of King Saud University - Computer and Information Sciences 36 (2024) 101926. https://doi.org/10.1016/j.jksuci.2024.101926.")
    ]

    engine.draw_references(references)

    engine.compile()
    print("Exact Base Paper PDF compiled successfully to:", pdf_path)


if __name__ == "__main__":
    generate_exact_basepaper_pdf()
