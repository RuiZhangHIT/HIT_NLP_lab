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
    hmm_init()
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
        file.write(process_line(modify_seg_result(result)) + '\n')


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


Min = -3.14e+100  # 表示最小值
Pi = {}  # 初始状态概率分布
A = {}  # 状态转移概率
B = {}  # 符号发射概率
Dic = set()  # 词典


# 初始化HMM中会用到的Pi,A,B矩阵
def hmm_init():
    states = ['B', 'M', 'E', 'S']  # 状态列表
    state_count = {}  # 用于保存各状态出现次数
    for former_state in states:
        Pi[former_state], A[former_state], B[former_state] = 0.0, {}, {}
        state_count[former_state] = 0
        for latter_state in states:
            A[former_state][latter_state] = 0.0
    word_count = 0  # 用于保存总词数
    for line in open('../io_files/199802.txt', 'r', encoding='gbk').readlines():
        if line == '\n':
            continue
        char, state = [], []  # 用于保存每一行的所有单字和对应状态
        for word in line.split():
            word = word[1 if word[0] == '[' else 0:word.index('/')]  # 取出一个词，去除词性标注
            Dic.add(word)  # 将该词存入词典中
            word_count += 1
            char.extend(list(word))  # 将该词的每个单字加到该行的字列表中
            if len(word) == 1:  # 单字，标注为S
                state.append('S')
                Pi['S'] += 1
            else:  # 多字，分为B、M和E
                state.append('B')
                state.extend(['M'] * (len(word) - 2))
                state.append('E')
                Pi['B'] += 1
        for i in range(len(state)):
            if i != 0:
                A[state[i - 1]][state[i]] += 1
            B[state[i]][char[i]] = B[state[i]].get(char[i], 0) + 1
            state_count[state[i]] += 1

    for former_state in states:
        Pi[former_state] = Min if Pi[former_state] == 0 else math.log(Pi[former_state] / word_count)  # 计算初始状态概率分布
        for latter_state in states:  # 计算状态转移概率
            A[former_state][latter_state] = Min if A[former_state][latter_state] == 0 else math.log(
                A[former_state][latter_state] / state_count[former_state])
        for word in B[former_state].keys():  # 计算符号发射概率
            B[former_state][word] = math.log(B[former_state][word] / state_count[former_state])


# 对一行结果进行最后处理，完成未登录词的识别
def process_line(result):
    final_result, buffer = '', ''  # 用于保存最终分词结果和待处理的连续出现的单字词（可能为被切碎的未登录词）
    words = result.split('/ ')[: -1]  # 当前的分词结果
    for i in range(len(words)):
        if len(words[i]) == 1 and words[i] not in Dic:  # 单字且该单字不是词典中的词，加入buffer，等待后续处理
            buffer += words[i]
        else:  # 多字或存在于词典中的单字
            if buffer:  # 若该词前面有单字词，先处理掉
                final_result += process_buffer(buffer)
                buffer = ''
            final_result += words[i] + '/ '  # 输出该多字词
    if buffer:  # 处理掉buffer中所有单字词
        final_result += process_buffer(buffer)
    return final_result


# 对连续出现的单字词进行处理，使得未登录词不被切碎
def process_buffer(chars):
    if len(chars) == 1:  # 待处理词为一个字，直接分词
        return chars + '/ '
    s_p = [{}]  # 用于保存每个单字词状态及对应概率对数
    s_list = {}  # 用于保存最终划分结果对应的各单字状态
    states = ['B', 'M', 'E', 'S']  # 状态列表
    for state in states:
        s_p[0][state], s_list[state] = Pi[state] + B[state].get(chars[0], Min), [state]
    former_states = {'B': 'ES', 'M': 'BM', 'E': 'BM', 'S': 'ES'}  # 状态的前一个可能状态
    for i in range(1, len(chars)):  # 按概率最大化对各个单字词进行状态选择与标注
        s_p.append({})
        next_s_list = {}
        for latter_state in states:
            (log_p, former_state) = max((s_p[i - 1][f_state] + A[f_state].get(latter_state, Min)
                                         + B[latter_state].get(chars[i], Min), f_state)
                                        for f_state in former_states[latter_state])
            s_p[i][latter_state] = log_p
            next_s_list[latter_state] = s_list[former_state] + [latter_state]
        s_list = next_s_list
    state_result = s_list['E'] if s_p[len(chars) - 1]['E'] > s_p[len(chars) - 1]['S'] else s_list['S']  # 最终结束状态必为E或S
    start, result = 0, ''
    for i, char in enumerate(chars):
        if state_result[i] == 'B':
            start = i
        elif state_result[i] == 'E':  # 合并为多字词输出
            result += chars[start: i + 1] + '/ '
        elif state_result[i] == 'S':  # 作为单字词输出
            result += char + '/ '
    return result


if __name__ == '__main__':
    unigram_dictionary, words_number = load_unigram_dic()
    bigram_dictionary = load_bigram_dic()
    bigram(unigram_dictionary, bigram_dictionary, words_number, 0.004)
