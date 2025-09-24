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
        text: str = "",
        level: int = 0,
        parent: "TitleNode | None" = None,
        prev: "TitleNode | None" = None,
    ) -> None:
        self.ttype = title_type
        self.size = size
        self.text = text
        self.level = level
        self.parent = parent
        self.prev = prev
        self.children: List["TitleNode"] = []
