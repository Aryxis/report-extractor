from typing import List
from title_type import TitleType


class TitleNode:
    """
    标题节点.
    TitleNode 是目录树中的节点.

    节点包含标题文本, 标题级别, 子节点列表以及父节点引用.
    """

    def __init__(
        self,
        title_type: "TitleType",
        size: float,
        y0: float = 0.0,
        y1: float = 0.0,
        page_no: int = 0,
        text: str = "",
        level: int = 0,
        parent: "TitleNode | None" = None,
        pos: int = 0,
    ) -> None:
        self.ttype = title_type
        self.size = size
        self.y0 = y0  # 标题底部的 y 坐标
        self.y1 = y1  # 标题顶部的 y 坐标
        self.page_no = page_no
        self.text = text
        self.level = level
        self.parent = parent
        self.pos = pos
        self.children: List["TitleNode"] = []

    def get_main_text(self) -> str:
        """获取标题文本."""
        return self.text[self.ttype.prefix_length :]
