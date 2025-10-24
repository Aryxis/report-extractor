import yaml
from typing import Optional
from title_node import TitleNode
from content_range import ContentRange


class TargetTree:
    """
    目标树, 就是一个 `list[dict]`, 元素为 root, 表示要提取的目标, 从 yaml 文件中加载.

    寻找目标的过程就是在目录树中寻找与目标相同的路径的过程.

    该类的主要方法是匹配子树的函数 `match_subtree`.
    """

    MAX_PAGES = 10000

    def __init__(self, filename: str = "./config.yaml") -> None:
        with open(filename, "r", encoding="utf-8") as file:
            self.tree = yaml.safe_load(file)

    def match_subtree(self, node: "TitleNode") -> Optional[ContentRange]:
        """
        判断目录树中的节点 node 是否与目标树中的某个节点匹配.
        匹配指的是从目标树的 root 开始, 到叶子节点为止, 每个节点依次匹配.
        """

        def match_one_node(tar: dict, index: int) -> Optional[int]:
            # 按照路径和 TitleNode 进行查找
            if index >= len(path):
                # 目录树到底了, 目标树还没到底, 说明我们需要更细致的标题
                return None

            # 检测当前节点是否匹配
            title = path[index]
            if title != tar["name"]:
                for alias in tar.get("aliases", []):
                    if title == alias:
                        break
                else:
                    return None

            # 当前节点匹配, 继续匹配子节点
            children = tar.get("children", [])
            if not children:
                # 目标树到底了, 说明匹配成功
                return index
            for child in children:
                if node_index := match_one_node(child, index + 1):
                    return node_index
            return None

        # 通过 parent 反向构建路径
        path = []
        node_list = []
        temp = node
        while temp.parent:
            path.append(temp.get_main_text())
            node_list.append(temp)
            temp = temp.parent
        path.reverse()
        node_list.reverse()

        for root in self.tree:
            if node_index := match_one_node(root, 0):
                # 返回 ContentRange
                matched_node: "TitleNode" = node_list[node_index]
                parent = matched_node.parent
                assert parent and parent.children
                if matched_node.pos == len(parent.children) - 1:
                    # 是最后一个节点
                    p_parent = parent.parent
                    assert p_parent
                    if parent.pos == len(p_parent.children) - 1:
                        # 父节点也是最后一个节点
                        return ContentRange(
                            start_page=matched_node.page_no,
                            start_y=matched_node.y1,
                            end_page=TargetTree.MAX_PAGES,
                            end_y=float("inf"),
                        )
                    else:
                        # 范围: 该节点到父节点的下一个节点
                        next_node = p_parent.children[parent.pos + 1]
                        return ContentRange(
                            start_page=matched_node.page_no,
                            start_y=matched_node.y1,
                            end_page=next_node.page_no,
                            end_y=next_node.y0,
                        )
                else:
                    # 有后继节点
                    # 范围: 该节点到后继节点
                    next_node = parent.children[matched_node.pos + 1]
                    return ContentRange(
                        start_page=matched_node.page_no,
                        start_y=matched_node.y1,
                        end_page=next_node.page_no,
                        end_y=next_node.y0,
                    )
        return None
