from typing import List, Dict, Literal, Final
from pdfplumber.pdf import PDF
from os import path
from .content_range import ContentRange
from .outline_node import OutlineNode


class PDFOutline:
    """
    PDF 大纲.
    以一个 root 节点 (虚拟) 开始.
    支持根据标题查找.
    """

    # 最大标题级别, 一般为 3
    # <XX 公司 XX 年年度报告> 为 0 级标题, 以此类推
    MAX_TITLE_LVL = 3
    MIN_TITLE_SIZE = 9.0  # 标题的字号最小值, 防止有些低频率的小字号被误判为标题
    MAX_TITLE_LENGTH = 50  # 标题的最大长度, 防止某些长段落被误判为标题
    MIN_TOTAL_LENGTH = 30  # 标题的字号所对应的文本总长度下限 (防止"稀有"字号)
    # MAX_TOTAL_LENGTH = 500  # 标题的字号所对应的文本总长度上限
    MAX_PERCENT = 0.4  # 超过该比例的, 认为是正文
    MAX_BODY_OCCUR_PERCENT = 0.1  # 超过页数一定比例的, 认为不是标题
    MAX_HEADER_HEIGHT = 80  # 页眉的最大高度

    def __init__(self, pages: List[Dict], pdf: "PDF") -> None:
        """
        初始化 PDF 大纲对象.
        注意: __init__ 并不构建大纲树, 需要显示调用 build_outline 方法.
        """
        self.file_name: Final[str] = (
            "Report" if pdf.path is None else path.basename(pdf.path)
        )
        self._root = OutlineNode(
            level=0, title=self.file_name, content_range=ContentRange(-1, -1, -1, -1)
        )
        self.all_pages: Final[List[Dict]] = pages
        self.pages_count: Final[int] = pages[-1]["page_number"] - 1  # 页码从 1 开始s
        self.called_build = False

    def build_outline(self) -> None:
        """
        根据 PDF 对象构建大纲树. 仅需调用一次.

        构建方法:
          1. 遍历所有页面, 提取标题的开头位置, 构建大纲树
          2. 根据开头位置确定结束位置
        """

        # 防止重复调用
        if self.called_build:
            print("Warning: build_outline has been called before.")
            return
        self.called_build = True

        title_dict = self._get_title_dict()

        self._init_root_title()  # 首页标题特殊处理
        # 将所有出现的标题按照出现次序放到数组中
        all_titles = []
        all_titles.append("0" + self._root.title)
        title_sizes = title_dict.keys()
        for page in self.all_pages[1:]:  # 跳过首页
            blocks = page["blocks"]
            total_length = page["total_length"]
            sizes_length = page["sizes_length"]

            # 一整页为一个标题
            if total_length <= PDFOutline.MAX_TITLE_LENGTH:
                # 将该页除了页码之外的所有文本作为标题
                page_number = page["page_number"]
                title_parts = []
                for block in blocks:
                    if (
                        all(char.isdigit() for char in block["text"])
                        and int(block["text"]) == page_number
                    ):
                        continue
                    title_parts.append(block["text"])
                cur_title = "".join(title_parts).strip()
                all_titles.append("1" + cur_title)  # 视为 1 级标题
                continue

            block_index = 0
            while block_index < len(blocks):
                size_key = round(blocks[block_index]["size"], 1)
                if size_key in title_sizes and (
                    (sizes_length[str(size_key)] / total_length)
                    <= PDFOutline.MAX_PERCENT
                ):
                    title_parts = []
                    title_parts.append(str(max(1, title_dict.get(size_key, 1))))
                    title_parts.append(blocks[block_index]["text"])

                    # 将标题文本合并, 防止标题被拆分成多个块
                    block_index += 1
                    while (
                        block_index < len(blocks)
                        and round(blocks[block_index]["size"], 1) == size_key
                    ):
                        title_parts.append(blocks[block_index]["text"])
                        block_index += 1
                    cur_title = "".join(title_parts).strip()
                    if len(cur_title) <= PDFOutline.MAX_TITLE_LENGTH:
                        all_titles.append(cur_title)
                else:
                    block_index += 1

        # save to `test_mid.txt` for debug
        with open("test_mid.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(all_titles))

    def dump(self, format: Literal["indent"], include_range=False) -> None:
        """打印大纲内容"""
        pass

    def _get_title_dict(self) -> Dict[float, int]:
        """
        获取标题字号对应的标题等级.
        """

        # 统计所有字号的文本长度
        font_size_count = {}  # {字号: 文本长度}
        for page in self.all_pages:
            sizes_length = page["sizes_length"]
            for size, count in sizes_length.items():
                key = round(float(size), 1)
                font_size_count[key] = font_size_count.get(key, 0) + count

        body_dict = self._get_body_dict()

        # 综合根据正文出现的页数和文本长度来决定标题字号
        level = 0
        title_dict = {}
        threshold = self.pages_count * PDFOutline.MAX_BODY_OCCUR_PERCENT
        for size, count in sorted(
            font_size_count.items(), key=lambda x: x[0], reverse=True
        ):
            if size < PDFOutline.MIN_TITLE_SIZE:
                break
            if count < PDFOutline.MIN_TOTAL_LENGTH:
                continue
            if body_dict.get(size, 0) > threshold:
                break  # 该字号是正文, 后续更小字号也不会是标题

            title_dict[size] = level
            level += 1
            if level > PDFOutline.MAX_TITLE_LVL:
                break

        # for k, v in sorted(font_size_count.items(), key=lambda x: x[0], reverse=True):
        #     print(f"Size {k}: Count {v}")

        if not title_dict:
            raise ValueError("No suitable title size found.")

        print(title_dict)
        return title_dict

    def _get_body_dict(self) -> Dict[float, int]:
        """
        body_dict 指的是一个字号成为正文的页数, 用于判断某个字号是否为标题.
        一个字号如果多次成为正文, 则不太可能是标题.
        """

        body_dict = {}  # {字号: 成为正文的页数}

        for page in self.all_pages:
            total_length = page["total_length"]
            if total_length <= PDFOutline.MAX_TITLE_LENGTH:
                continue  # 跳过内容过少的页面

            sizes_length = page["sizes_length"]
            for size, count in sizes_length.items():
                key = round(float(size), 1)
                if (count / total_length) >= PDFOutline.MAX_PERCENT:
                    # 认为该字号在这一页是正文
                    body_dict[key] = body_dict.get(key, 0) + 1

        print(body_dict)
        return body_dict

    def _init_root_title(self) -> None:
        """
        获取根标题 (唯一一个 0 级标题).
        从第二页的 header 中获取, 如果没有则使用文件名作为根标题.
        根标题**不影响**内容定位.
        一般为'X公司X年年度报告'.
        """

        first_page = self.all_pages[1]
        blocks = first_page["blocks"]
        title_parts = []
        block_index = 0
        while block_index < len(blocks):
            if blocks[block_index]["top"] > PDFOutline.MAX_HEADER_HEIGHT:
                break
            if "公司" in blocks[block_index]["text"]:
                title_parts.append(blocks[block_index]["text"])
                block_index += 1
                break
            block_index += 1

        if title_parts:
            while (
                block_index < len(blocks)
                and blocks[block_index]["top"] <= PDFOutline.MAX_HEADER_HEIGHT
            ):
                title_parts.append(blocks[block_index]["text"])
                block_index += 1
            title = "".join(title_parts).strip()
            title = title.replace("全文", "")
            self._root.title = title
