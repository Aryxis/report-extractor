from dataclasses import dataclass, field
from typing import List, Optional
from .content_range import ContentRange


@dataclass(eq=False)
class OutlineNode:
    """
    大纲节点.
    每个节点包含以下信息:
      - level: 标题级别
      - title: 标题内容
      - content_range: 标题对应的内容范围
      - parent: 父节点
      - children: 子节点列表
    """

    level: int
    title: str
    content_range: ContentRange
    parent: Optional["OutlineNode"] = None
    children: List["OutlineNode"] = field(default_factory=list)

    def add_child(self, child: "OutlineNode"):
        """添加子节点"""
        child.parent = self
        self.children.append(child)
