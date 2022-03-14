# 形成一元语法词典
def gene_unigram_dic():
    words = dict()  # 用于保存所有的词及其出现次数
    with open('../io_files/unigram_dic.txt', 'w', encoding='utf-8') as file:
        for line in open('../io_files/199802.txt', 'r', encoding='gbk').readlines():  # 读取已分词的文本
            for word in line.split():
                word = word[1 if word[0] == '[' else 0: word.index('/')]
                if words.get(word):
                    words[word] += 1
                else:
                    words[word] = 1
        for word in sorted(words):  # 写入词典
            file.write(word + ' ' + str(words[word]) + '\n')


# 形成二元语法词典
def gene_bigram_dic():
    word_pairs = dict()  # 用于保存所有的词对与出现次数
    with open('../io_files/bigram_dic.txt', 'w', encoding='utf-8') as file:
        for line in open('../io_files/199802.txt', 'r', encoding='gbk').readlines():  # 读取已分词的文本
            word_list = []
            if line != '\n':
                line = '<BOS>/ ' + line + '<EOS>/ '
            for word in line.split():
                word = word[1 if word[0] == '[' else 0: word.index('/')]
                word_list.append(word)
            i = 0
            while len(word_list) > 1 and i != len(word_list) - 1:
                former_word = word_list[i]
                latter_word = word_list[i + 1]
                pair = (former_word, latter_word)
                if pair in word_pairs:
                    word_pairs[pair] += 1
                    i += 1
                else:
                    word_pairs[pair] = 1
                    i += 1
        for pair in word_pairs:  # 写入词典
            file.write(pair[0] + ' ' + pair[1] + ' ' + str(word_pairs[pair]) + '\n')


if __name__ == '__main__':
    gene_unigram_dic()
    gene_bigram_dic()
