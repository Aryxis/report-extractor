from title_node import TitleNode
from title_type import TitleType


class OutlineTree:
    """
    目录树.
    OutlineTree 管理 TitleNode 节点, 形成树状结构.

    树包含根节点, 提供添加节点和遍历节点的方法.
    """

    MAX_LEVEL = 2

    def __init__(self, root_title: str) -> None:
        self.root = TitleNode(
            size=float("inf"),  # 根节点字号设为无穷大, 便于比较
            title_type=TitleType(root_title, is_root=True),
            text=root_title,
        )

        # 跟踪最后添加的节点, 便于插入新节点
        self._last_node = self.root

    def add_node(
        self, size: float, text: str, ttype: "TitleType", is_centered: bool
    ) -> None:
        # 预定义的处理函数
        def _insert(
            level: int, parent: "TitleNode | None", prev: "TitleNode | None"
        ) -> None:
            if level > OutlineTree.MAX_LEVEL:
                return  # 超过最大层级, 忽略
            cur_node = TitleNode(
                title_type=ttype,
                size=size,
                text=text,
                level=level,
                parent=parent,
                prev=prev,
            )
            if parent:
                parent.children.append(cur_node)
            self._last_node = cur_node

        if ttype == 0:
            if not is_centered:
                # 非居中, 无标题特征, 视为正文, 忽略
                return
            if self._last_node.ttype == 0:
                # 上一个节点和该节点样式相同, 同级
                _insert(
                    level=self._last_node.level,
                    parent=self._last_node.parent,
                    prev=self._last_node,
                )
                return
            else:
                # 上一个节点和该节点样式不同, 视为下一级
                _insert(
                    level=self._last_node.level + 1,
                    parent=self._last_node,
                    prev=None,
                )
                return
        else:  # 提取到了标题的某些特征
            if size < self._last_node.size:
                # 字体更小, 视为下一级
                _insert(
                    level=self._last_node.level + 1,
                    parent=self._last_node,
                    prev=None,
                )
                return
            if ttype == self._last_node.ttype:
                # 和上一个节点样式相同, 同级
                _insert(
                    level=self._last_node.level,
                    parent=self._last_node.parent,
                    prev=self._last_node,
                )
                return
            if size == self._last_node.size:
                # 字体相同
                last_parent = self._last_node.parent
                assert last_parent is not None
                if size == last_parent.size or ttype == last_parent.ttype:
                    # 和父节点字体相同或样式相同, 视为和父节点同级
                    _insert(
                        level=last_parent.level,
                        parent=last_parent.parent,
                        prev=last_parent,
                    )
                    return
                else:
                    # 视为下一级
                    _insert(
                        level=self._last_node.level + 1,
                        parent=self._last_node,
                        prev=None,
                    )
                    return
            # 字体更大, 向上查找同级节点
            cur_node = self._last_node.parent
            while cur_node and size > cur_node.size and ttype != cur_node.ttype:
                cur_node = cur_node.parent
            if not cur_node:
                # 没找到同级
                return
            if ttype == cur_node.ttype:
                # 插入为同级
                _insert(
                    level=cur_node.level,
                    parent=cur_node.parent,
                    prev=cur_node,
                )
                return
            elif size <= cur_node.size:
                # 插入为 cur_node 的下一级
                _insert(
                    level=cur_node.level + 1,
                    parent=cur_node,
                    prev=None,
                )

    def print_dump(self) -> None:
        """打印目录树, 用于调试."""

        def _dump(node: TitleNode, indent: int) -> None:
            print(" " * indent + f"[L{node.level}] {node.text}")
            for child in node.children:
                _dump(child, indent + 2)

        _dump(self.root, 0)

    def str_dump(self) -> str:
        """返回目录树的字符串表示, 用于调试."""

        def _dump(node: TitleNode, indent: int) -> str:
            result = " " * indent + f"[L{node.level}] {node.text}\n"
            for child in node.children:
                result += _dump(child, indent + 2)
            return result

        return _dump(self.root, 0)
