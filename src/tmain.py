import pymupdf
import json
import time
from tqdm import tqdm


def fix_font_encoding(page_dict: dict) -> None:
    """
    就地修改 pymupdf 的字体编码问题.

    问题来源: 字体名称 (对应 page_dict['blocks']['lines']['spans']['font']) 会被 pymupdf 错误地以 latin1 编码读取.

    解决办法: 如果字体名称中包含非 ASCII 字符, 则尝试将其从 latin1 解码为 utf-8.
    """
    for block in page_dict["blocks"]:
        if block["type"] != 0:  # 不是文本块
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if any(ord(ch) > 127 for ch in span["font"]):
                    try:
                        font = span["font"]
                        span["font"] = font.encode("latin1").decode("utf-8")
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        pass  # 保留原值


def process():
    for pn in tqdm(range(len(doc)), desc="Processing pages"):
        page = doc[pn]
        page_dict = page.get_text("dict")

        # page_dict["blocks"] = [
        #     block for block in page_dict["blocks"] if block.get("type") != 1
        # ]  # 去除图片块

        cropped_blocks = []  # 只保留文本块的必要信息 (bbox, lines)
        sizes_count = {}  # 统计字体大小对应内容的长度
        for block in page_dict["blocks"]:
            if block["type"] != 0:  # 不是文本块
                continue
            cropped_lines = []
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    size = round(span["size"], 2)
                    bbox = span["bbox"]
                    sizes_count[size] = sizes_count.get(size, 0) + len(text)
                    cropped_lines.append(
                        {
                            "x0": round(bbox[0], 2),
                            "x1": round(bbox[2], 2),
                            "size": size,
                            "text": text,
                        }
                    )  # 只保留横坐标, 字号和文本
            if cropped_lines:
                cropped_blocks.append(
                    {
                        "bbox": block["bbox"],
                        "lines": cropped_lines,
                    }
                )

        all_pages.append(
            {
                "page_number": pn + 1,
                "width": round(page.rect.width, 2),
                "blocks": cropped_blocks,
                "sizes_count": sizes_count,
                "total_length": sum(sizes_count.values()),
            }
        )


pdf_path = "input_pdf/300059_东方财富_2024.pdf"

doc = pymupdf.open(pdf_path)

page_numbers = list(range(4))

all_pages = []

start_time = time.time()
process()
end_time = time.time()
print(f"Processed {len(doc)} pages in {end_time - start_time:.2f}s.")

with open("src/t.json", "w", encoding="utf-8") as f:
    json.dump(all_pages, f, ensure_ascii=False, indent=2)

# print(page_dict)
