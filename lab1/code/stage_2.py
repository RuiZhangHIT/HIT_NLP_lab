# 读取词典文件
def load_dic():
    lines = open('../io_files/dic.txt', 'r', encoding='utf-8').readlines()  # 读取词典
    dic, max_len = [], 0  # 用于存放词典和最大词长
    for line in lines:
        dic.append(line[0: len(line) - 1])  # 将该词加入词典中
        max_len = len(line) - 1 if len(line) - 1 > max_len else max_len  # 更新最大词长
    return dic, max_len


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


# 正向最大匹配分词
# 注意：写seg_FMM.txt文件选择的mode是a，如果在已有文件的情况下重复运行代码，需要先把已有文件删除，否则会重复输出内容到文件里
def fmm(dic, max_len):
    for line in open('../io_files/199801_sent.txt', 'r', encoding='gbk').readlines():
        start, result = 0, ''
        while start != len(line) - 1:
            expect_word = line[start: len(line) if len(line) - start < max_len else start + max_len]
            while expect_word not in dic:
                if len(expect_word) == 1:
                    break
                expect_word = expect_word[: -1]  # 减小匹配词长
            start += len(expect_word)  # 继续对该行尚未完成分词的部分进行匹配
            result += expect_word + '/ '
        open('../io_files/seg_FMM.txt', 'a', encoding='utf-8').write(modify_seg_result(result) + '\n')


# 逆向最大匹配分词，需要先把已有文件
# 注意：写seg_BMM.txt文件选择的mode是a，如果在已有文件的情况下重复运行代码，需要先把已有文件删除，否则会重复输出内容到文件里
def bmm(dic, max_len):
    for line in open('../io_files/199801_sent.txt', 'r', encoding='gbk').readlines():
        end, result = len(line) - 1, []
        while end != 0:
            expect_word = line[0 if end < max_len else end - max_len: end]
            while expect_word not in dic:
                if len(expect_word) == 1:
                    break
                expect_word = expect_word[1:]  # 减小匹配词长
            end -= len(expect_word)  # 继续对该行尚未完成分词的部分进行匹配
            result.insert(0, expect_word + '/')
        open('../io_files/seg_BMM.txt', 'a', encoding='utf-8').write(modify_seg_result(' '.join(result) + ' ') + '\n')


if __name__ == '__main__':
    dictionary, max_length = load_dic()
    # fmm(dictionary, max_length)
    bmm(dictionary, max_length)
