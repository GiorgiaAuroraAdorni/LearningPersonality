#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tensorflow as tf
import preprocess_dataset as ppd
import TFRecord_dataset as exp_TFR

# pre-trained Punkt tokenizer for English
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('crubadan')
# sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

filename = "Dataset/shuf_review.json.gz"
dataset = tf.data.TextLineDataset(filename, compression_type="GZIP")

# file_json = "Dataset/review10.json"
# dataset = tf.data.TextLineDataset(file_json)

# json parsing and reviews extraction
texts = dataset.map(lambda input_line:
                    tf.py_func(ppd.parse_function, [input_line], [tf.string, tf.string]))

# Generate training and test dataset
train_dataset, test_dataset = ppd.split_dataset(texts, 80, 5261669)  # 5261669

texts_words = ppd.text2words(texts)
train_words = ppd.text2words(train_dataset)
test_words = ppd.text2words(test_dataset)

# dataset = dataset.batch(5)

# Create iterator from dataset
words_iterator = texts_words.make_one_shot_iterator()
train_iterator = train_words.make_one_shot_iterator()
test_iterator = test_words.make_one_shot_iterator()

# Tensor from iterator
words_element = words_iterator.get_next()
train_element = train_iterator.get_next()
test_element = test_iterator.get_next()

# Address to save the TFRecords file
words_filename = 'Dataset/TFRecords/words_sentence.tfrecords.gz'
train_filename = 'Dataset/TFRecords/train.tfrecords.gz'  
test_filename = 'Dataset/TFRecords/test.tfrecords.gz'  

# Options to zip file
opts = tf.python_io.TFRecordOptions(tf.python_io.TFRecordCompressionType.GZIP)

# Open the TFRecords file
writer = tf.python_io.TFRecordWriter(words_filename, opts)
train_writer = tf.python_io.TFRecordWriter(train_filename, opts)
test_writer = tf.python_io.TFRecordWriter(test_filename, opts)

# Consumption dataset
with tf.Session() as sess:

    while True:
        try:
            (a, b) = (sess.run(train_element))
            #print('training', a, b)
            exp_TFR.write_tfrecords(a, b, train_writer)

        except tf.errors.OutOfRangeError:
                break

    train_writer.close()

    while True:
        try:
            (c, d) = (sess.run(test_element))
            #print('test', c, d)
            exp_TFR.write_tfrecords(c, d, test_writer)

        except tf.errors.OutOfRangeError:
                break

    test_writer.close()
    
    while True:
        try:
            ids, text = (sess.run(words_element))
            # print('WORDS', id, text)
            exp_TFR.write_tfrecords(ids, text, writer)
            
        except tf.errors.OutOfRangeError:
            break

    writer.close()

# divido le sentences (stemming) es. tempi verbali, nomi maschili
# We also removed numbers, non-English words, urls, and extraneous information contained in PDF versions
