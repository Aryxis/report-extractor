import re


class TitleType:
    """
    标题类型.

    我们以下列特征定义标题类型, 如果任意特征不同, 则认为是不同的标题类型:
        - 是否是"第X章"
        - 中文/西文数字
        - 有括号/无括号
            - 全括号/半括号
        - 是否有顿号或点号

    不同级别的标题, 类型理应不同; 同级别的标题, 类型理应相同.
    """

    # 预定义一些组成标题的部分
    ZH_NUM = r"零一二三四五六七八九十"
    DOT = r"、."
    RE_SPACE = r"\s"
    RE_L_PAREN = r"[(（]"
    RE_R_PAREN = r"[)）]"

    # 标题的几种类型
    RE_ZH_NUM = rf"[{ZH_NUM}]+"
    RE_LAT_NUM = r"[0-9]+"
    RE_ROOT = rf"^第{RE_ZH_NUM}[节章]"
    RE_FULL_PAREN = rf"^({RE_L_PAREN}.*?{RE_R_PAREN})"  # 捕获以计算长度
    RE_RIGHT_PAREN = rf"^.*?{RE_R_PAREN}"
    RE_DOT = rf"[{DOT}]"

    # 标题类型的常量
    TITLE_ROOT = 1  # 第X章
    TITLE_ZH_NUM = 2  # 中文数字
    TITLE_HAS_PAREN = 4  # 有括号
    TITLE_FULL_PAREN = 8  # 全括号
    TITLE_DOT = 16  # 顿号或点号

    # 标题前缀的最大长度, 前缀是正文以外的部分
    MAX_PRE_LEN = 5

    def __init__(self, title: str, is_root: bool = False) -> None:
        if is_root:
            self._id = -1
        else:
            title_pre = self._find_title_prefix(title)
            self._id = self._calc_title_id(title_pre)

    def _find_title_prefix(self, title: str) -> str:
        """
        找到标题的前缀部分, 以下是几个前缀的示例:
        - 第一节
        - （一）
        - 1、
        """
        title = title.lstrip()
        if not title:
            raise ValueError("Title is empty")

        length = min(len(title), TitleType.MAX_PRE_LEN)

        # 分别寻找顿号, 右括号和空格试图截断标题前缀
        match_dot = re.search(TitleType.RE_DOT, title)
        if match_dot:
            length = min(length, match_dot.start() + 1)
        match_r_paren = re.search(TitleType.RE_R_PAREN, title)
        if match_r_paren:
            length = min(length, match_r_paren.start() + 1)
        match_space = re.search(TitleType.RE_SPACE, title)
        if match_space:
            length = min(length, match_space.start() + 1)

        return title[:length]

    def _calc_title_id(self, prefix: str) -> int:
        """
        计算标题的类型 ID.

        标题的类型是一个整数, 其二进制表示的每一位代表一种特征, 1 表示有该特征, 0 表示没有该特征.
        """

        res = 0
        if re.search(TitleType.RE_ROOT, prefix):
            res |= TitleType.TITLE_ROOT
        if re.search(TitleType.RE_ZH_NUM, prefix):
            res |= TitleType.TITLE_ZH_NUM
        # 括号的处理, 先判断全括号, 再判断右括号
        if re.search(TitleType.RE_FULL_PAREN, prefix):
            res |= TitleType.TITLE_HAS_PAREN | TitleType.TITLE_FULL_PAREN
        elif re.search(TitleType.RE_RIGHT_PAREN, prefix):
            res |= TitleType.TITLE_HAS_PAREN
        if re.search(TitleType.RE_DOT, prefix):
            res |= TitleType.TITLE_DOT

        return res

    def __eq__(self, other: object) -> bool:
        if not (isinstance(other, TitleType) or isinstance(other, int)):
            return False
        if isinstance(other, int):
            return self._id == other
        return self._id == other._id

    def empty(self) -> bool:
        """判断标题类型是否为空, 即没有任何标题特征"""
        return self._id == 0

    @staticmethod
    def is_root(title: str) -> bool:
        """判断标题是否为根标题"""
        return re.search(TitleType.RE_ROOT, title) is not None
