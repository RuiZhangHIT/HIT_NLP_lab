import stage_2
import time


class Node:

    def __init__(self, children_number, terminal=False, char=''):
        self.children = [None] * children_number
        self.terminal = terminal
        self.char = char
        self.nonempty_children = 0  # 非空子节点个数
        self.conflict_cost = 0  # 由于冲突带来的额外查找开销

    def add_child(self, child):
        if self.conflict_cost > self.nonempty_children or self.nonempty_children == len(self.children):
            self.modify_tree()
        index = ord(child.char) % len(self.children)
        while self.children[index] is not None:
            index = (index + 1) % len(self.children)
            self.conflict_cost += 1
        self.children[index] = child
        self.nonempty_children += 1

    def get_child(self, char):
        index = ord(char) % len(self.children)
        while True:
            child = self.children[index]
            if child is None or child.char == char:
                return child
            index = (index + 1) % len(self.children)

    def modify_tree(self):
        original_children = self.children
        self.children = [None] * (2 * len(self.children))  # 将子节点数翻倍
        self.nonempty_children = self.conflict_cost = 0
        for original_child in original_children:  # 重新映射原有子节点
            if original_child is not None:
                self.add_child(original_child)


# 读取词典文件，生成trie树
def load_dic():
    word_list = []
    for line in open('../io_files/dic.txt', 'r', encoding='utf-8'):
        word_list.append(line.split()[0])
    dic = Node(5000)
    for word in word_list:
        gene_trie(dic, word)
    return dic


# 在trie树中插入新词
def gene_trie(dic, word):
    word_len = len(word)
    dic_len = 0
    pre_node, node = dic, dic.get_child(word[dic_len])

    while node is not None:  # trie树中已存在共同前缀
        dic_len += 1
        if dic_len == word_len:
            node.terminal = True  # 能作为一个词的结尾
            return
        pre_node = node
        node = pre_node.get_child(word[dic_len])

    while dic_len < word_len:  # trie树中尚未出现过的部分
        node = Node(50)
        node.char = word[dic_len]
        dic_len += 1
        pre_node.add_child(node)
        pre_node = node

    node.terminal = True  # 能作为一个词的结尾


# 优化后的正向最大匹配分词
def fmm(dic):
    file = open('../io_files/seg_FMM_optimized.txt', 'w', encoding='utf-8')
    for line in open('../io_files/199801_sent.txt', 'r', encoding='gbk').readlines():
        start, result = 0, ''
        while start != len(line) - 1:
            word_len = 0
            seg_word = line[start + word_len]
            node = dic.get_child(seg_word)
            while node is not None:  # trie树中有前缀
                word_len += 1
                if node.terminal:
                    seg_word = line[start: start + word_len]
                if word_len + start == len(line):
                    break
                node = node.get_child(line[start + word_len])
            start += len(seg_word)  # 继续对该行尚未完成分词的部分进行匹配
            result += seg_word + '/ '
        file.write(modify_seg_result(result) + '\n')


# 对分词结果进行处理，解决数词和时间词被分开的问题
def modify_seg_result(seg_line):
    buffer, modified_result = '', ''
    seg_words = seg_line.split('/ ')[: len(seg_line.split('/ ')) - 1]
    for i, word in enumerate(seg_words):
        if word.isnumeric() or word in '-．％':  # 若是数词或时间词的数字部分
            buffer += word
            if i == len(seg_words) - 1:
                modified_result += buffer + '/ '
        else:
            if word in '年月日时分秒点':  # 处理时间词的文字部分
                if buffer.isnumeric():
                    modified_result += buffer
                    buffer = ''
            if buffer:
                modified_result += buffer + '/ '
                buffer = ''
            modified_result += word + '/ '
    return modified_result


# 优化前后时间对比
def gene_time_cost():
    dic, max_len = stage_2.load_dic()
    print('正在进行优化前的正向最大匹配分词...')
    start_time = time.time()
    stage_2.fmm(dic, max_len)
    end_time = time.time()
    print('完成分词')
    result = '优化前FMM耗时:\t' + str(end_time - start_time) + 's\n'

    dic = load_dic()
    print('正在进行优化后的正向最大匹配分词...')
    start_time_optimized = time.time()
    fmm(dic)
    end_time_optimized = time.time()
    print('完成分词')
    result += '优化后FMM耗时:\t' + str(end_time_optimized - start_time_optimized) + 's\n'

    open('../io_files/TimeCost.txt', 'w', encoding='utf-8').write(result)


if __name__ == '__main__':
    gene_time_cost()
