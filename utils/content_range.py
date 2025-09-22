from dataclasses import dataclass


@dataclass(eq=False)
class ContentRange:
    """
    表示内容的范围.
    内容的范围由一个四元组表示: (start_page, start_block, end_page, end_block).
    范围为闭区间.
    通过这四个索引可以在 O(1) 时间定位一段内容.
    """

    start_page: int
    start_block: int
    end_page: int
    end_block: int

    def set_end(self, page: int, block: int):
        self.end_page = page
        self.end_block = block
