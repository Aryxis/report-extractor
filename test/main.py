import fitz  # pymupdf
import json
from typing import List, Tuple

pdf_path = "test.pdf"
out_md = "output.md"


def table_to_markdown(table) -> str:
    """Convert a PyMuPDF Table object to a markdown table string.

    We preserve empty cells and attempt to keep the original cell content.
    """
    # table.rows -> list of rows; each row is list of cells with .text
    rows = []
    for r in range(table.nrows):
        row_cells = []
        for c in range(table.ncols):
            cell = table.cell(r, c)
            text = cell.text.strip() if cell and cell.text else ""
            # Escape pipe characters
            text = text.replace("|", "\\|")
            row_cells.append(text)
        rows.append(row_cells)

    if not rows:
        return ""

    # Build markdown
    md_lines = []
    header = rows[0]
    md_lines.append("| " + " | ".join(header) + " |")
    md_lines.append("|" + " --- |" * len(header))
    for r in rows[1:]:
        md_lines.append("| " + " | ".join(r) + " |")

    return "\n".join(md_lines)


def extract_page_markdown(page: fitz.Page) -> str:
    """Extract tables and text from a page and return a markdown string preserving order.

    Strategy:
    - Use page.find_tables() to detect tables.
    - For each table, record its bbox and convert to markdown.
    - Extract text blocks via page.get_text("dict") and keep blocks that are not inside table bboxes.
    - Sort all items (tables + text blocks) by their vertical position (top to bottom) to preserve flow.
    """
    items = []  # list of tuples (y0, type, content)

    # Detect tables
    # find_tables() may return a TableFinder or list depending on PyMuPDF version
    table_bboxes: List[Tuple[float, float, float, float]] = []
    tables = []
    try:
        tf = page.find_tables()
        # TableFinder is iterable but may not have len(); try to convert to list or call extract()
        try:
            # Some versions allow iteration
            tables = list(tf)
        except TypeError:
            # TableFinder may have an extract() method
            if hasattr(tf, "extract"):
                tables = tf.extract()
            else:
                # fallback: treat tf as single table-like
                tables = [tf]
    except Exception:
        tables = []

    for i, t in enumerate(tables):
        # Table object shapes vary. For this environment Table has attributes observed by inspector:
        # bbox (tuple), cells (list), row_count, col_count, rows, to_markdown, to_pandas
        md = ""
        bbox = None

        # bbox may be a tuple (x0, y0, x1, y1)
        try:
            if hasattr(t, "bbox"):
                b = t.bbox
                if isinstance(b, (list, tuple)) and len(b) == 4:
                    bbox = fitz.Rect(b)
                elif isinstance(b, fitz.Rect):
                    bbox = b
        except Exception:
            bbox = None

        # prefer a builtin markdown conversion if available
        try:
            if hasattr(t, "to_markdown"):
                md = t.to_markdown()
            elif hasattr(t, "to_pandas"):
                df = t.to_pandas()
                md = df.to_markdown(index=False)
            else:
                md = table_to_markdown(t)
        except Exception:
            try:
                md = str(t)
            except Exception:
                md = ""

        # if bbox still None, try to compute from row/col cells
        if bbox is None:
            try:
                if hasattr(t, "rows") and isinstance(t.rows, (list, tuple)) and t.rows:
                    # rows is list of row objects; each row has cells with bbox
                    all_x0 = []
                    all_y0 = []
                    all_x1 = []
                    all_y1 = []
                    for row in t.rows:
                        for cell in getattr(row, "cells", []) or []:
                            cb = getattr(cell, "bbox", None)
                            if cb:
                                # cb may be tuple
                                if isinstance(cb, (list, tuple)):
                                    x0, y0, x1, y1 = cb
                                elif isinstance(cb, fitz.Rect):
                                    x0, y0, x1, y1 = cb.x0, cb.y0, cb.x1, cb.y1
                                else:
                                    continue
                                all_x0.append(x0)
                                all_y0.append(y0)
                                all_x1.append(x1)
                                all_y1.append(y1)
                    if all_x0:
                        bbox = fitz.Rect(
                            min(all_x0), min(all_y0), max(all_x1), max(all_y1)
                        )
            except Exception:
                bbox = None

        if bbox is None:
            bbox = fitz.Rect(0, 0, 0, 0)

        items.append(
            (
                bbox.y0,
                "table",
                {"md": md, "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1], "index": i},
            )
        )
        table_bboxes.append((bbox.x0, bbox.y0, bbox.x1, bbox.y1))

    # Extract text blocks
    txt = page.get_text("dict")
    for block in txt.get("blocks", []):
        if block.get("type") != 0:
            # not a text block (image or other)
            continue
        bbox = block.get("bbox")  # [x0, y0, x1, y1]
        x0, y0, x1, y1 = bbox
        # check intersection with any table bbox; if mostly inside table, skip (we'll use table text)
        inside_table = False
        for tb in table_bboxes:
            tx0, ty0, tx1, ty1 = tb
            # compute intersection area
            ix0 = max(x0, tx0)
            iy0 = max(y0, ty0)
            ix1 = min(x1, tx1)
            iy1 = min(y1, ty1)
            if ix1 > ix0 and iy1 > iy0:
                inter_area = (ix1 - ix0) * (iy1 - iy0)
                block_area = (x1 - x0) * (y1 - y0)
                # if more than 60% of block area is inside a table, skip it
                if inter_area / (block_area + 1e-9) > 0.6:
                    inside_table = True
                    break
        if inside_table:
            continue

        # collect text spans
        lines = []
        for line in block.get("lines", []):
            spans = [s.get("text", "") for s in line.get("spans", [])]
            lines.append("".join(spans))
        text = "\n".join(lines).strip()
        if text:
            items.append((y0, "text", {"text": text, "bbox": bbox}))

    # sort items by y (top to bottom). If same y, tables before text.
    items.sort(key=lambda x: (x[0], 0 if x[1] == "table" else 1))

    md_parts = []
    for typ in items:
        if typ[1] == "table":
            meta = typ[2]
            md_parts.append(f"<!-- TABLE bbox={meta['bbox']} index={meta['index']} -->")
            md_parts.append("")
            md_parts.append(meta["md"])
            md_parts.append("")
        else:
            meta = typ[2]
            md_parts.append(f"<!-- TEXT bbox={meta['bbox']} -->")
            md_parts.append("")
            # preserve paragraphs
            md_parts.append(meta["text"])
            md_parts.append("")

    return "\n".join(md_parts)


def main():
    doc = fitz.open(pdf_path)
    md_all = []
    for i, page in enumerate(doc):
        print(f"Processing page {i + 1}/{len(doc)}")
        md_all.append(f"# Page {i + 1}\n")
        md_all.append(extract_page_markdown(page))

    out = "\n---\n\n".join(md_all)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote markdown to {out_md}")


if __name__ == "__main__":
    main()
