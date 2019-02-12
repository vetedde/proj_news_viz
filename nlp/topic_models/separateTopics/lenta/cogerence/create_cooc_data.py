# Copyright 2017, Additive Regularization of Topic Models.

# Utility to generate pairwise co-occurrence information of tokens
# of collection in BigARTM batches with default dictionary.
# It will create 'cooc_data.txt' file in the directory with
# this script, that should be passed into artm.Dictionary.gather()
# method as 'cooc_data_path' parameter.

# Author: Murat Apishev (great-mel@yandex.ru)

from __future__ import print_function

import os
import sys
import glob
import time
import artm
import codecs

from six import iteritems
from six.moves import range

HELP_STR = '\nUsage: python create_cooc_dictionary '
HELP_STR += '<folder_with_batches_and_dictionary> [<window_size>]\n'
HELP_STR += '<window_size> is int greater than zero\n'
HELP_STR += 'if <window_size> is not specified, whole document window will be used\n\n'


def _read_parameters():
    win_size = -1  # window size equal to whole document
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise RuntimeError(HELP_STR)
    if len(sys.argv) > 2:
        win_size = int(sys.argv[2])

    batches_directory = sys.argv[1]
    return batches_directory, win_size


def _create_batch_dictionary(batch):
    batch_dictionary = {}
    for ind, token in enumerate(batch.token):
        batch_dictionary[ind] = token

    return batch_dictionary


def _save_dictionary(cooc_dictionary, num_tokens):
    with open('cooc_data.txt', 'w') as fout:
        for idx in range(num_tokens):
            if idx in cooc_dictionary:
                for key, value in iteritems(cooc_dictionary[idx]):
                    fout.write(f'{idx} {key} {value}\n')


def _process_batch(glob_cooc_dict, batch, win_size, accumulator):
    batch_dictionary = _create_batch_dictionary(batch)

    def _process_window(word_ids, word_weights):
        for j in range(1, len(word_ids)):
            value = min(word_weights[0], word_weights[j])
            tok_idx_1 = accumulator[batch_dictionary[word_ids[0]]]
            tok_idx_2 = accumulator[batch_dictionary[word_ids[j]]]

            if tok_idx_1 in glob_cooc_dict:
                if tok_idx_2 in glob_cooc_dict:
                    if tok_idx_2 in glob_cooc_dict[tok_idx_1]:
                        glob_cooc_dict[tok_idx_1][tok_idx_2] += value
                    else:
                        if tok_idx_1 in glob_cooc_dict[tok_idx_2]:
                            glob_cooc_dict[tok_idx_2][tok_idx_1] += value
                        else:
                            glob_cooc_dict[tok_idx_1][tok_idx_2] = value
                else:
                    if tok_idx_2 in glob_cooc_dict[tok_idx_1]:
                        glob_cooc_dict[tok_idx_1][tok_idx_2] += value
                    else:
                        glob_cooc_dict[tok_idx_1][tok_idx_2] = value
            else:
                if tok_idx_2 in glob_cooc_dict:
                    if tok_idx_1 in glob_cooc_dict[tok_idx_2]:
                        glob_cooc_dict[tok_idx_2][tok_idx_1] += value
                    else:
                        glob_cooc_dict[tok_idx_2][tok_idx_1] = value
                else:
                    glob_cooc_dict[tok_idx_1] = {}
                    glob_cooc_dict[tok_idx_1][tok_idx_2] = value

    for item in batch.item:
        real_window_size = win_size if win_size > 0 else len(item.token_id)
        for window_start_id in range(len(item.token_id)):
            end_index = window_start_id + real_window_size
            token_ids = item.token_id[
                        window_start_id: end_index if end_index < len(item.token_id) else len(item.token_id)]
            token_weights = item.token_weight[
                            window_start_id: end_index if end_index < len(item.token_id) else len(item.token_id)]
            _process_window(token_ids, token_weights)


def _get_size(cooc_dict):
    result = sys.getsizeof(cooc_dict)
    for k_1, internal in iteritems(cooc_dict):
        result += sys.getsizeof(k_1)
        for t, v in iteritems(internal):
            result += sys.getsizeof(t)
            result += sys.getsizeof(v)

    return result


if __name__ == "__main__":
    global_time_start = time.time()
    batches_folder, window_size = _read_parameters()
    batches_list = glob.glob(os.path.join(batches_folder, '*.batch'))
    dictionaries_list = [name for name in glob.glob(os.path.join(batches_folder, '*.dict'))]

    if len(batches_list) < 1 or len(dictionaries_list) < 1:
        raise RuntimeError('No batches or dictionaries were found in given folder')
    else:
        print(f'{len(batches_list)} batches were found, start processing')

    temp_dict = artm.Dictionary()
    temp_dict.load(dictionaries_list[0])
    file_name = 'cooc_info/{}_temp_dict.txt'.format(time.time())
    if not os.path.isdir('cooc_info'):
        os.mkdir('cooc_info')
    temp_dict.save_text(file_name)

    dictionary = {}
    with codecs.open(file_name, 'r', 'utf-8') as fin:
        next(fin)
        next(fin)
        for index, line in enumerate(fin):
            dictionary[line.split(' ')[0][0: -1]] = index
    os.remove(file_name)

    global_cooc_dictionary = {}
    for index, filename in enumerate(batches_list):
        local_time_start = time.time()
        print('Process batch: {}'.format(index))
        current_batch = artm.messages.Batch()
        with open(filename, 'rb') as fin:
            current_batch.ParseFromString(fin.read())
        _process_batch(global_cooc_dictionary, current_batch, window_size, dictionary)

        print(f'Finished batch, elapsed time: {time.time() - local_time_start}')

    _save_dictionary(global_cooc_dictionary, len(dictionary.keys()))
    size_gb = _get_size(global_cooc_dictionary) / 1000000000.0
    print(f'Finished collection, elapsed time: {time.time() - global_time_start}, size: {size_gb} Gb')
