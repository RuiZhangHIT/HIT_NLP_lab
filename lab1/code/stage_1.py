# 形成分词词典
def gene_dic():
    word_set = set()  # 用于保存所有的词
    lines = open('../io_files/199801_seg&pos.txt', 'r', encoding='gbk').readlines()  # 读取已分词的文本
    with open('../io_files/dic.txt', 'w', encoding='utf-8') as file:
        for line in lines:
            for word in line.split():
                if '/m' in word:  # 数词不加入词典
                    continue
                if word[0: word.index('/') - 1].isnumeric() and word[word.index('/') - 1] in '年月日时分秒点':  # 时间不加入词典
                    continue
                word = word[1 if word[0] == '[' else 0: word.index('/')]  # 去掉词性标注与短语标注
                word_set.add(word)  # 加入词典
        word_list = list(word_set)
        word_list.sort()
        file.write('\n'.join(word_list))


if __name__ == '__main__':
    gene_dic()
