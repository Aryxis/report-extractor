from utils.pdf_outline import PDFOutline
import pdfplumber
import json
import time
# import os


# pdf_path = "input_pdf/002500_山西证券_2024.pdf"
pdf_path = "input_pdf/300059_东方财富_2024.pdf"
doc = pdfplumber.open(pdf_path)


# with pdfplumber.open(pdf_name) as pdf:
#     for pn in pns:
#         helper(pdf.pages[pn])


# def eall():
#     """初始化 PDF, 提取所有页面的文字块信息"""
#     for page in doc.pages:
#         text_blocks = page.extract_words(
#             extra_attrs=["fontname", "size"],
#             x_tolerance=3,
#             y_tolerance=3,
#         )
#         all_pages.append({"page_number": page.page_number, "blocks": text_blocks})

# Read from pre-extracted JSON file

start_time = time.time()
with open("test_all1.json", "r", encoding="utf-8") as f:
    all_pages = json.load(f)
end_time = time.time()
print(f"Loaded JSON: {end_time - start_time:.2f}s.")

start_time = time.time()
outline = PDFOutline(all_pages, pdf=doc)
outline.build_outline()
end_time = time.time()
print(f"Built outline: {end_time - start_time:.2f}s.")

outline.dump(format="indent", include_range=True)
