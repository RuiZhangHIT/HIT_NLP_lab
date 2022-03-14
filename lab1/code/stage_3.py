# 读取分词结果，并进行预处理
def process_ans(path, encoding):
    processed_lines = []
    for line in open(path, 'r', encoding=encoding).readlines():
        if line == '\n':
            continue
        new_line = ''
        for word in line.split():
            new_line += word[1 if word[0] == '[' else 0: word.index('/')] + '/ '
        processed_lines.append(new_line)
    return processed_lines


# 计算分词的准确率P、召回率R和F-评价
def cal_p_r_f(std_ans, my_ans, std_encoding, my_encoding):
    std_lines = process_ans(std_ans, std_encoding)
    my_lines = process_ans(my_ans, my_encoding)
    std_words = right_words = my_words = 0  # 标准分词总词数，正确分词总词数，自己分词总词数
    for i, std_line in enumerate(std_lines):
        std_line_words = std_line.split('/ ')  # 取出标准的分词文本中每行的词语
        my_line_words = my_lines[i].split('/ ')  # 取自己分词得到文本中每行的词语
        std_words_num = len(std_line_words) - 1  # 标准分词的每行分词数
        my_words_num = len(my_line_words) - 1  # 自己分词的每行分词数
        std_words += std_words_num
        my_words += my_words_num
        std_num = my_num = 0  # 标准分词和自己分词的处理词数
        std_len, my_len = len(std_line_words[std_num]), len(my_line_words[my_num])  # 标准分词和自己分词的字符串长度
        while std_num < std_words_num and my_num < my_words_num:
            if std_len == my_len:
                if len(std_line_words[std_num]) == len(my_line_words[my_num]):
                    right_words += 1
                std_num += 1
                my_num += 1
                std_len += len(std_line_words[std_num])
                my_len += len(my_line_words[my_num])
            elif std_len < my_len:
                std_num += 1
                std_len += len(std_line_words[std_num])
            else:
                my_num += 1
                my_len += len(my_line_words[my_num])
    precision = right_words / float(my_words)
    recall = right_words / float(std_words)
    f_value = 2 * precision * recall / (precision + recall)
    return precision, recall, f_value


# 形成评价结果文件
def gene_score():
    std_ans = '../io_files/199801_seg&pos.txt'
    result = '正反向最大匹配分词效果\n\n'
    result += 'FMM:\n'
    precision, recall, f_value = cal_p_r_f(std_ans, '../io_files/seg_FMM.txt', 'gbk', 'utf-8')
    result += '准确率P:\t' + str(precision * 100) + '%\n'
    result += '召回率R:\t' + str(recall * 100) + '%\n'
    result += "F-评价:\t" + str(f_value * 100) + '%\n\n'
    result += 'BMM:\n'
    precision, recall, f_value = cal_p_r_f(std_ans, '../io_files/seg_BMM.txt', 'gbk', 'utf-8')
    result += '准确率P:\t' + str(precision * 100) + '%\n'
    result += '召回率R:\t' + str(recall * 100) + '%\n'
    result += "F-评价:\t" + str(f_value * 100) + "%\n\n"
    open('../io_files/score.txt', 'w', encoding='utf-8').write(result)


def gene_score_stage_5():
    result = '二元语法分词效果:\n'
    precision, recall, f_value = cal_p_r_f('../io_files/199801_seg&pos.txt', '../io_files/seg_LM.txt', 'gbk', 'utf-8')
    result += '准确率P:\t' + str(precision * 100) + '%\n'
    result += '召回率R:\t' + str(recall * 100) + '%\n'
    result += "F-评价:\t" + str(f_value * 100) + '%\n\n'
    open('../io_files/score_stage_5.txt', 'w', encoding='utf-8').write(result)


if __name__ == '__main__':
    # gene_score()
    gene_score_stage_5()
