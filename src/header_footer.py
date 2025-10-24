from typing import Dict


class HeaderFooter:
    """
    用于获取一篇文档的页眉, 页脚 (主要是页码) 的 y 坐标.
    """

    HEADER_FEATURE_STRS = ["年度报告"]

    def __init__(self, page: Dict) -> None:
        self.page = page
        self.header_y = None
        self.footer_y = None
        self._analyze_page()

    def _analyze_page(self) -> None:
        """
        根据特定的一页分析页眉和页脚的 y 坐标.
        """
        blocks = self.page["blocks"]
        # 分析页眉的 y2 坐标
        init_header = False
        if blocks:
            # 取页面第一个 block 的字符串
            first_block = blocks[0]
            str_list = []
            for line in first_block["lines"]:
                str_list.append(line["text"])
            first_block_str = "".join(str_list)
            for feature_str in HeaderFooter.HEADER_FEATURE_STRS:
                if first_block_str.find(feature_str) != -1:
                    # 找到了一个特征, 认为第一个 block 是页眉
                    self.header_y = first_block["bbox"][3]
                    init_header = True
                    break
        if not init_header:
            self.header_y = 0.0  # 没有找到特征, 认为没有页眉

        # 分析页脚的 y1 坐标
        init_footer = False
        page_no = str(self.page["page_no"])
        if blocks:
            # 取页面最后一个 block 的字符串
            last_block = blocks[-1]
            str_list = []
            for line in last_block["lines"]:
                str_list.append(line["text"])
            last_block_str = "".join(str_list)
            if last_block_str.find(page_no) != -1:
                # 找到了页码, 认为最后一个 block 是页脚
                self.footer_y = last_block["bbox"][1]
                init_footer = True
        if not init_footer:
            self.footer_y = float("inf")  # 没有找到页码, 认为没有页脚
