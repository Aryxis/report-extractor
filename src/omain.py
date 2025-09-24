import json

from title_type import TitleType
from outline_tree import OutlineTree

# outline main

# 最大标题级别, 一般为 3
# <XX 公司 XX 年年度报告> 为 0 级标题, 以此类推
MAX_TITLE_LVL = 3
MIN_TITLE_SIZE = 10.0  # 标题的字号最小值, 防止有些低频率的小字号被误判为标题
MAX_TITLE_LENGTH = 50  # 标题的最大长度, 防止某些长段落被误判为标题
MIN_TOTAL_LENGTH = 30  # 标题的字号所对应的文本总长度下限 (防止"稀有"字号)
# MAX_TOTAL_LENGTH = 500  # 标题的字号所对应的文本总长度上限
MAX_PERCENT = 0.3  # 超过该比例的, 认为是正文
MAX_X_TOLERANCE = 5.0  # 标题两个元素横坐标的最大容忍差距
MAX_BODY_OCCUR_PERCENT = 0.1  # 超过页数一定比例的, 认为不是标题
MAX_HEADER_HEIGHT = 80  # 页眉的最大高度

all_pages = []

with open("src/t.json", "r", encoding="utf-8") as f:
    all_pages = json.load(f)


def is_centered(width: float, x0: float, x1: float) -> bool:
    """判断文本块是否居中."""
    margin = (width - (x1 - x0)) / 2
    return abs(x0 - margin) < 5 and abs(x1 - (width - margin)) < 5


outlines = OutlineTree("Report")
for page in all_pages[1:]:  # 封面页特殊处理
    total_length = page["total_length"]
    width = page["width"]
    sizes_count = page["sizes_count"]
    for block in page["blocks"]:
        lines = block["lines"]
        first_size = lines[0]["size"]
        if (
            first_size < MIN_TITLE_SIZE
            or (sizes_count[str(first_size)] / total_length) > MAX_PERCENT
        ):
            continue  # 字号过小或该字号占比过大, 认为是正文
        is_whole = True
        for i, line in enumerate(lines[1:], start=1):
            if (line["x0"] - lines[i - 1]["x1"]) > MAX_X_TOLERANCE:
                is_whole = False
                break
        if not is_whole:
            continue  # 两个部分间距太远

        # 仅当"第X节"出现时, 才插入空格
        text = lines[0]["text"]
        if len(lines) > 1 and TitleType.is_root(text):
            text += " "
        text += "".join(line["text"] for line in lines[1:])

        if text.find("管理层讨论与分析") != -1:
            pass  # for debugging
        if text.isdigit():
            continue  # 纯数字, 认为是页码
        if len(text) > MAX_TITLE_LENGTH:
            continue  # 标题过长
        ttype = TitleType(text)
        centered = is_centered(width, block["bbox"][0], block["bbox"][2])
        if ttype == 0 and not centered:
            continue  # 无样式且不居中, 认为是正文

        # 认为该行是标题, 添加到大纲树中
        outlines.add_node(first_size, text, ttype, centered)

# outlines.print_dump()
with open("src/outline.txt", "w", encoding="utf-8") as f:
    f.write(outlines.str_dump())
