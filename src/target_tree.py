import yaml
from title_node import TitleNode


class TargetTree:
    """
    目标树, 就是一个 `list[dict]`, 元素为 root, 表示要提取的目标, 从 yaml 文件中加载.

    寻找目标的过程就是在目录树中寻找与目标树匹配的子树的过程.

    该类的主要方法是匹配子树的函数 `match_subtree`.
    """

    def __init__(self, filename: str = "./config.yaml") -> None:
        with open(filename, "r", encoding="utf-8") as file:
            self.tree = yaml.safe_load(file)

    def match_subtree(self, node: "TitleNode") -> bool:
        """
        判断目录树中的节点 node 是否与目标树中的某个节点匹配.
        匹配指的是从目标树的 root 开始, 到叶子节点为止, 每个节点依次匹配.
        """

        def match_one_node(tar: dict, index: int) -> bool:
            # 按照路径和 TitleNode 进行查找
            if index >= len(path):
                # 目录树到底了, 目标树还没到底, 说明我们需要更细致的标题
                return False

            # 检测当前节点是否匹配
            title = path[index]
            if title != tar["name"]:
                for alias in tar.get("aliases", []):
                    if title == alias:
                        break
                else:
                    return False

            # 当前节点匹配, 继续匹配子节点
            index += 1
            children = tar.get("children", [])
            if not children:
                # 目标树到底了, 说明匹配成功
                return True
            for child in tar.get("children", []):
                if match_one_node(child, index):
                    return True
            return False

        # 通过 parent 反向构建路径
        path = []
        temp = node
        while temp.parent:
            path.append(temp.get_main_text())
            temp = temp.parent
        path.reverse()

        for root in self.tree:
            if match_one_node(root, 0):
                return True
        return False
