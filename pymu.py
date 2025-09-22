import pymupdf
import json

pymupdf.TEXTFLAGS_TEXT


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


def dump_all_blocks_with_details(page_dict: dict) -> None:
    """
    打印页面中所有文本块的详细信息, 供调试使用.
    """

    print("size, flags, char_flags, text")
    for block in page_dict["blocks"]:
        if block["type"] != 0:  # 不是文本块
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if not text:
                    continue
                # print(span["font"], end=", ")
                print(f"{span['size']:.1f}", end=", ")
                print(span["flags"], end=", ")
                print(span["char_flags"], end=", ")
                # flag = span.get("flags", 0)
                # flag_list = []
                # if flag & pymupdf.TEXT_FONT_SUPERSCRIPT:
                #     flag_list.append("superscript")
                # if flag & pymupdf.TEXT_FONT_ITALIC:
                #     flag_list.append("italic")
                # if flag & pymupdf.TEXT_FONT_SERIFED:
                #     flag_list.append("serifed")
                # if flag & pymupdf.TEXT_FONT_MONOSPACED:
                #     flag_list.append("monospaced")
                # if flag & pymupdf.TEXT_FONT_BOLD:
                #     flag_list.append("bold")
                # print(" | ".join(flag_list), end=", ")
                print("", text, "", sep='"')


doc = pymupdf.open("input_pdf/300059_东方财富_2024.pdf")
first = doc[75]
result = first.get_text(option="json")

result_dict = json.loads(result)
fix_font_encoding(result_dict)
result_dict["blocks"] = [
    block for block in result_dict["blocks"] if block.get("type") != 1
]

with open("pymu.json", "w", encoding="utf-8") as f:
    json.dump(result_dict, f, ensure_ascii=False, indent=2)

dump_all_blocks_with_details(result_dict)

# for res in result

# print(result)

# print(result)


# with open("pymu.json", "w", encoding="utf-8") as f:
#     f.write(result)

# with open("pymu.json", "w", encoding="utf-8") as f:
#     json.dump(result, f, ensure_ascii=False, indent=2)

# for res in result:
#     print(res)
