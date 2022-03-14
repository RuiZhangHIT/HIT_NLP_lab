import math


# 读取一元语法的词典
def load_unigram_dic():
    uni_dic = {}  # 用于保存词典中的所有的词及其出现次数
    words_num = 0  # 记录总词数
    for line in open('../io_files/unigram_dic.txt', 'r', encoding='utf-8').readlines():
        word, count = line.split()
        uni_dic[word] = int(count)  # 将该词加入词典中
        words_num += int(count)  # 增加总词数
        for count in range(len(word)):  # 获取词典中每个词的前缀词
            prefix_word = word[: count + 1]
            if prefix_word not in uni_dic:
                uni_dic[prefix_word] = 0  # 将新前缀存入并置词频为0
    return uni_dic, words_num


# 读取二元语法的词典
def load_bigram_dic():
    bi_dic = {}  # 用于保存词典中的所有的词对及其出现次数
    for line in open('../io_files/bigram_dic.txt', 'r', encoding='utf-8').readlines():
        former_word, latter_word, count = line.split()
        if latter_word not in bi_dic.keys():
            bi_dic[latter_word] = {former_word: int(count)}
        else:
            bi_dic[latter_word][former_word] = int(count)
    return bi_dic


# 通过词典获得有向无环图DAG
def gene_dag(line, uni_dic):
    dag = {}  # 用于保存最终的有向无环图DAG
    length = len(line)
    for start in range(length):  # 遍历句子中的每一个字，判断其分词情况
        end = start
        dag[start] = []  # 处于第k个位置上的字所能构成词的结束下标
        seg_word = line[start: end + 1]
        while seg_word in uni_dic:
            if uni_dic[seg_word] > 0:  # 从k位置开始的词在词典中且词频>0
                dag[start].append(end)  # 将对应的结束下标加入到DAG中
            end += 1
            if end == length:
                break
            seg_word = line[start: end + 1]
        if not dag[start]:
            dag[start].append(start)  # 未找到词则将单字词加入DAG
    return dag


# 计算给定前词情况下，后词出现的概率(进行平滑处理)
def cal_p(former_word, latter_word, uni_dic, bi_dic, words_num, alpha):
    # 若后词与前词不独立，计算给定前词时后词出现的概率，采用加1平滑
    cond_p = math.log(bi_dic.get(latter_word, {}).get(former_word, 0) + 1) - math.log(uni_dic.get(former_word, 0) + words_num)
    # 若后词与前词条件独立，计算后词出现的概率，对于未在词典出现的，频数记为1
    indep_p = math.log(uni_dic.get(latter_word, 0) + 1) - math.log(words_num)
    return alpha * cond_p + (1 - alpha) * indep_p


# 二元文法分词
def bigram(uni_dic, bi_dic, words_num, param):
    file = open('../io_files/seg_LM.txt', 'w', encoding='utf-8')
    for line in open('../io_files/199801_sent.txt', 'r', encoding='gbk').readlines():
        line = '<BOS>' + line + '<EOS>'
        latter_words_dic = {}
        # 初始化latter_words_dic,格式为{前词: {后词: 后词概率}}
        # 单独考虑<BOS>的后词及概率
        start = 5
        dag = gene_dag(line, uni_dic)
        tmp_dic = {}  # 用于存放<BOS>的后词(起始与结束下标)及概率
        for end in dag[start]:
            tmp_dic[(start, end + 1)] = cal_p('<BOS>', line[start: end + 1], uni_dic, bi_dic, words_num, param)
        latter_words_dic['<BOS>'] = tmp_dic
        # <BOS>后<EOS>前的所有可能分词的后词及概率
        while start < len(line) - 5:
            for end in dag[start]:
                former_word = line[start: end + 1]  # 当前前词(起始与结束下标)
                latter_start = end + 1
                tmp_dic = {}  # 用于存放当前前词的后词(起始与结束下标)及概率
                for latter_end in dag[latter_start]:
                    latter_word = line[latter_start: latter_end + 1]
                    if latter_word == '<':
                        tmp_dic['<EOS>'] = cal_p(former_word, '<EOS>', uni_dic, bi_dic, words_num, param)
                    else:
                        tmp_dic[(latter_start, latter_end + 1)] = cal_p(former_word, latter_word, uni_dic, bi_dic,
                                                                        words_num, param)
                latter_words_dic[(start, end + 1)] = tmp_dic
            start += 1
        # 初始化former_words_dic,格式为{后词: 前词}
        former_words_dic = {}
        former_words = list(latter_words_dic.keys())
        for former_word in former_words:
            for latter_word in latter_words_dic[former_word].keys():
                former_words_dic[latter_word] = former_words_dic.get(latter_word, list())
                former_words_dic[latter_word].append(former_word)
        former_words.append('<EOS>')  # 提取所有词
        all_words = former_words
        # 动态规划计算route,格式为{后词: (概率对数, 前词)}
        route = {}
        for latter_word in all_words:
            if latter_word == '<BOS>':  # <BOS>必出现，必在句首位置
                route['<BOS>'] = (0, None)
            else:
                former_words = former_words_dic.get(latter_word, list())
                if former_words != list():
                    route[latter_word] = max((latter_words_dic[former_word][latter_word] + route[former_word][0],
                                              former_word) for former_word in former_words)  # 取有最大概率的词作为前词
                else:  # 没有前词，将其概率对数赋值为一个极小值保证下一步计算能正常进行
                    route[latter_word] = (-99999999, None)
                    continue
        # 从句尾向句首整理分词结果
        result = []
        seg_word = '<EOS>'
        while True:
            seg_word = route[seg_word][1]  # 定位前词
            if seg_word == '<BOS>':
                break
            result.insert(0, line[seg_word[0]: seg_word[1]])  # 将前词放入分词结果列表句首位置
        file.write(modify_seg_result(result) + '\n')


# 对分词结果进行处理，解决数词和时间词被分开的问题
def modify_seg_result(result):
    buffer, modified_result = '', ''
    for i, word in enumerate(result):
        change = False
        changed_word = ""
        for char in word:  # 全角字符（除空格）转为半角字符
            inside_code = ord(char)
            if 65281 <= inside_code <= 65374:
                inside_code -= 65248
                change = True
            changed_word += chr(inside_code)
        word = changed_word if change else word
        # 若是数词或时间词的数字部分或英文字母，合并输出
        flag = True  # 用于标志整个词是否满足数字或字母的条件
        for char in word:
            if not char.isnumeric() and char not in '-—.·%/qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM':
                flag = False
        if flag:
            if change:
                changed_word = ""
                for char in word:  # 半角字符（除空格）转为全角字符
                    inside_code = ord(char)
                    if 33 <= inside_code <= 126:
                        inside_code += 65248
                    changed_word += chr(inside_code)
                word = changed_word
            buffer += word
            if i == len(result) - 1:
                modified_result += buffer + '/ '
        else:
            if word in '年月日时分秒点':  # 处理时间词的文字部分
                if buffer.isnumeric():
                    modified_result += buffer
                    buffer = ''
            if buffer:
                modified_result += buffer + '/ '
                buffer = ''
            if change:
                changed_word = ""
                for char in word:  # 半角字符（除空格）转为全角字符
                    inside_code = ord(char)
                    if 33 <= inside_code <= 126:
                        inside_code += 65248
                    changed_word += chr(inside_code)
                word = changed_word
            modified_result += word + '/ '
    if modified_result[-3] == '\n':  # 每行最后的换行符不参与分词
        modified_result = modified_result[:-3]
    return modified_result


if __name__ == '__main__':
    unigram_dictionary, words_number = load_unigram_dic()
    bigram_dictionary = load_bigram_dic()
    bigram(unigram_dictionary, bigram_dictionary, words_number, 0.004)
