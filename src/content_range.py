class ContentRange:
    """
    表示章节的范围.
    章节的范围由一个四元组表示: (start_page, start_y, end_page, end_y).
    start_page 和 end_page 是页码.
    start_y 是章节标题底部的 y 坐标, end_y 是下一章节标题顶部的 y 坐标.
    """

    def __init__(self, start_page: int, start_y: float, end_page: int, end_y: float):
        self.start_page = start_page
        self.start_y = start_y
        self.end_page = end_page
        self.end_y = end_y
