def get_file_sequences(raw_path):    # raw_path examples: //gdsgfd/gsdf/a2_stencil_masked_3_$F5.jpg  or //gdsgfd/gsdf/a2_stencil_masked_3_`padzero(5,$F%250)`.jpg

    reg_ex = r'[_.]\$F\d?[_.]'
    reg_ex_match = re.search(reg_ex, raw_path)

    if reg_ex_match is not None:

        left_side = raw_path[:reg_ex_match.start() + 1].rsplit('/', 1)[-1]    # a2_stencil_masked_3_
        right_side = raw_path[reg_ex_match.end() - 1:]    # .jpg

        dir_path = raw_path.rsplit("/", 1)[0]
        file_list = os.listdir(dir_path)
        file_list = [dir_path + "/" + each for each in file_list if re.fullmatch(left_side + r'\d+' + right_side, each)]

        return file_list

    else:
        return None