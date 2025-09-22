import pdfplumber
import json
from tqdm import tqdm

all_pages = []


def helper(page):
    text_blocks = page.extract_words(
        extra_attrs=["fontname", "size", "flags"],
        x_tolerance=3,
        y_tolerance=3,
    )
    # 添加一些额外信息
    total_length = 0
    sizes_length = {}
    for block in text_blocks:
        total_length += len(block["text"])
        size_key = round(block["size"], 1)
        sizes_length[size_key] = sizes_length.get(size_key, 0) + len(block["text"])

    all_pages.append(
        {
            "page_number": page.page_number,
            "blocks": text_blocks,
            "total_length": total_length,
            "sizes_length": sizes_length,
        }
    )


# pdf_name = "input_pdf/002500_山西证券_2024.pdf"
pdf_name = "input_pdf/300059_东方财富_2024.pdf"
# pdf_name = "input_pdf/601318_中国平安_2012.pdf"
# pdf_name = "input_pdf/601166_兴业银行_2012.pdf"
# pns = list(range(len()))

with pdfplumber.open(pdf_name) as pdf:
    cnt = 0
    for page in tqdm(pdf.pages, desc="Processing pages"):
        helper(page)
        cnt += 1
        if cnt > 10:
            break
    # for pn in pns:
    #     helper(pdf.pages[pn])

with open(
    "test_part.json",
    "w",
    encoding="utf-8",
    # f"./out/p{','.join([str(pn) for pn in pns])}.json", "w", encoding="utf-8"
) as f:
    json.dump(all_pages, f, ensure_ascii=False, indent=2)
