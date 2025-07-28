import os
import json
from collections import Counter, defaultdict
from pathlib import Path
import fitz  # PyMuPDF


ZERO_BASED_PAGE_NUM = False        
MIN_HEADING_LEN = 2               
FONT_SIZE_MIN = 6.0               
FONT_SIZE_MAX = 80.0               
TITLE_TOP_BAND_FRAC = 0.30        
DEBUG = False




def page_number(pnum: int) -> int:
    """Return page number according to the expected convention (0 or 1 based)."""
    return pnum if ZERO_BASED_PAGE_NUM else (pnum + 1)


def collect_font_sizes(doc):
    """Collect and return a list of (rounded) font sizes used in the document."""
    sizes = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = round(span["size"], 1)
                    if FONT_SIZE_MIN <= size <= FONT_SIZE_MAX:
                        sizes.append(size)
    return sizes


def pick_heading_levels(font_sizes):
    """
    Decide which three font sizes correspond to H1, H2, H3.
    Heuristic: sort by (size DESC, frequency DESC)
    """
    if not font_sizes:
        return None, None, None

    counter = Counter(font_sizes)
    # sort by size DESC, then freq DESC
    sorted_sizes = sorted(counter.items(), key=lambda x: (-x[0], -x[1]))
    h1 = sorted_sizes[0][0] if len(sorted_sizes) > 0 else None
    h2 = sorted_sizes[1][0] if len(sorted_sizes) > 1 else None
    h3 = sorted_sizes[2][0] if len(sorted_sizes) > 2 else None

    if DEBUG:
        print("Font sizes (size -> count):", sorted(counter.items(), reverse=True))
        print(f"Chosen: H1={h1}, H2={h2}, H3={h3}")
    return h1, h2, h3


def extract_headings(doc, h1_size, h2_size, h3_size):
    """
    Go through each page, join spans per line, and classify lines as H1/H2/H3
    by the largest font size that occurs in the line.
    """
    headings = []

    for pnum, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                parts = []
                sizes = []
                for span in line.get("spans", []):
                    txt = span["text"].strip()
                    if not txt:
                        continue
                    size = round(span["size"], 1)
                    if FONT_SIZE_MIN <= size <= FONT_SIZE_MAX:
                        sizes.append(size)
                        parts.append(txt)

                if not parts or not sizes:
                    continue

                text = " ".join(parts).strip()
                if len(text) < MIN_HEADING_LEN:
                    continue

                max_size = max(sizes)

                if max_size == h1_size:
                    level = "H1"
                elif max_size == h2_size:
                    level = "H2"
                elif max_size == h3_size:
                    level = "H3"
                else:
                    continue  

                headings.append({
                    "level": level,
                    "text": text,
                    "page": page_number(pnum)
                })

    seen = set()
    uniq = []
    for h in headings:
        key = (h["level"], h["text"], h["page"])
        if key not in seen:
            uniq.append(h)
            seen.add(key)

    return uniq


def guess_title(doc, headings, h1_size):

    
    candidates = [h["text"].strip() for h in headings if h["page"] in (0, 1) and len(h["text"].split()) >= 3]
    if candidates:
        # choose the longest
        best = max(candidates, key=len)
        if DEBUG:
            print("Title from headings:", best)
        return best

    try:
        page1 = doc.load_page(0)
        page_height = page1.rect.height
        top_band_y = page_height * TITLE_TOP_BAND_FRAC

        spans = []
        for block in page1.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = round(span["size"], 1)
                    x0, y0, _, _ = span["bbox"]
                    text = span["text"].strip()
                    if not text:
                        continue
                    if size == h1_size and y0 <= top_band_y:
                        spans.append((round(y0), round(x0), text))

        spans.sort()  
        seen = set()
        frags = []
        for _, __, t in spans:
            if t not in seen:
                frags.append(t)
                seen.add(t)

        if frags:
            title = " ".join(frags).strip()
            if DEBUG:
                print("Title from spans:", title)
            return title

    except Exception as e:
        if DEBUG:
            print("Title-from-spans fallback failed:", e)

    return "Untitled Document"


def process_pdf(pdf_path: Path, out_dir: Path):
    doc = fitz.open(pdf_path.as_posix())

    font_sizes = collect_font_sizes(doc)
    h1_size, h2_size, h3_size = pick_heading_levels(font_sizes)

    headings = extract_headings(doc, h1_size, h2_size, h3_size)

    title = guess_title(doc, headings, h1_size)

    output = {
        "title": title,
        "outline": headings
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / (pdf_path.stem + ".json")
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f" {pdf_path.name} -> {out_file.name}")


def main():
    in_dir = Path("input")
    out_dir = Path("output")

    pdfs = sorted(in_dir.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in ./input")
        return

    for pdf in pdfs:
        try:
            process_pdf(pdf, out_dir)
        except Exception as e:
            print(f" Failed on {pdf.name}: {e}")


if __name__ == "__main__":
    main()
