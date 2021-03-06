import os, datetime
import numpy as np
import tensorflow as tf
from DataLoader import *

# Dataset Parameters
batch_size = 200
load_size = 256
fine_size = 224
c = 3
data_mean = np.asarray([0.45834960097, 0.44674252445, 0.41352266842])

# Training Parameters
learning_rate = 0.001
dropout = 0.5  # Dropout, probability to keep units
training_iters = 100000
step_display = 1
step_save = 10000
path_save = 'dylannet'
start_from = ''


def alexnet(x, keep_dropout):
    weights = {
        'wc1_top': tf.Variable(tf.random_normal([11, 11, 3, 96], stddev=np.sqrt(2. / (11 * 11 * 3)))),
        'wc2_top': tf.Variable(tf.random_normal([5, 5, 96, 256], stddev=np.sqrt(2. / (5 * 5 * 96)))),
        'wc3_top': tf.Variable(tf.random_normal([3, 3, 256, 384], stddev=np.sqrt(2. / (3 * 3 * 256)))),
        'wc4_top': tf.Variable(tf.random_normal([3, 3, 384, 256], stddev=np.sqrt(2. / (3 * 3 * 384)))),
        'wc5_top': tf.Variable(tf.random_normal([3, 3, 256, 256], stddev=np.sqrt(2. / (3 * 3 * 256)))),

        'wc1_bot': tf.Variable(tf.random_normal([11, 11, 3, 96], stddev=np.sqrt(2. / (11 * 11 * 3)))),
        'wc2_bot': tf.Variable(tf.random_normal([5, 5, 96, 256], stddev=np.sqrt(2. / (5 * 5 * 96)))),
        'wc3_bot': tf.Variable(tf.random_normal([3, 3, 256, 384], stddev=np.sqrt(2. / (3 * 3 * 256)))),
        'wc4_bot': tf.Variable(tf.random_normal([3, 3, 384, 256], stddev=np.sqrt(2. / (3 * 3 * 384)))),
        'wc5_bot': tf.Variable(tf.random_normal([3, 3, 256, 256], stddev=np.sqrt(2. / (3 * 3 * 256)))),

        'wf6_tt': tf.Variable(tf.random_normal([7 * 7 * 256, 4096], stddev=np.sqrt(2. / (7 * 7 * 256)))),
        'wf6_tb': tf.Variable(tf.random_normal([7 * 7 * 256, 4096], stddev=np.sqrt(2. / (7 * 7 * 256)))),
        'wf6_bb': tf.Variable(tf.random_normal([7 * 7 * 256, 4096], stddev=np.sqrt(2. / (7 * 7 * 256)))),
        'wf6_bt': tf.Variable(tf.random_normal([7 * 7 * 256, 4096], stddev=np.sqrt(2. / (7 * 7 * 256)))),

        'wf7_tt': tf.Variable(tf.random_normal([4096, 4096], stddev=np.sqrt(2. / 4096))),
        'wf7_tb': tf.Variable(tf.random_normal([4096, 4096], stddev=np.sqrt(2. / 4096))),
        'wf7_bb': tf.Variable(tf.random_normal([4096, 4096], stddev=np.sqrt(2. / 4096))),
        'wf7_bt': tf.Variable(tf.random_normal([4096, 4096], stddev=np.sqrt(2. / 4096))),

        'wo_top': tf.Variable(tf.random_normal([4096, 100], stddev=np.sqrt(2. / 4096))),
        'wo_bot': tf.Variable(tf.random_normal([4096, 100], stddev=np.sqrt(2. / 4096)))
    }

    biases = {
        'bc1_top': tf.Variable(tf.zeros(96)),
        'bc2_top': tf.Variable(tf.zeros(256)),
        'bc3_top': tf.Variable(tf.zeros(384)),
        'bc4_top': tf.Variable(tf.zeros(256)),
        'bc5_top': tf.Variable(tf.zeros(256)),

        'bc1_bot': tf.Variable(tf.zeros(96)),
        'bc2_bot': tf.Variable(tf.zeros(256)),
        'bc3_bot': tf.Variable(tf.zeros(384)),
        'bc4_bot': tf.Variable(tf.zeros(256)),
        'bc5_bot': tf.Variable(tf.zeros(256)),

        'bf6_top': tf.Variable(tf.zeros(4096)),
        'bf6_bot': tf.Variable(tf.zeros(4096)),

        'bf7_top': tf.Variable(tf.zeros(4096)),
        'bf7_bot': tf.Variable(tf.zeros(4096)),

        'bo': tf.Variable(tf.zeros(100))
    }

    # ------------------------------Top Convolutions------------------------------- #
    # Conv + ReLU + LRN + Pool, 224->55->27
    conv1_top = tf.nn.conv2d(x, weights['wc1_top'], strides=[1, 4, 4, 1], padding='SAME')
    conv1_top = tf.nn.relu(tf.nn.bias_add(conv1_top, biases['bc1_top']))
    lrn1_top = tf.nn.local_response_normalization(conv1_top, depth_radius=5, bias=1.0, alpha=1e-4, beta=0.75)
    pool1_top = tf.nn.max_pool(lrn1_top, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

    # Conv + ReLU + LRN + Pool, 27-> 13
    conv2_top = tf.nn.conv2d(pool1_top, weights['wc2_top'], strides=[1, 1, 1, 1], padding='SAME')
    conv2_top = tf.nn.relu(tf.nn.bias_add(conv2_top, biases['bc2_top']))
    lrn2_top = tf.nn.local_response_normalization(conv2_top, depth_radius=5, bias=1.0, alpha=1e-4, beta=0.75)
    pool2_top = tf.nn.max_pool(lrn2_top, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

    # Conv + ReLU, 13-> 13
    conv3_top = tf.nn.conv2d(pool2_top, weights['wc3_top'], strides=[1, 1, 1, 1], padding='SAME')
    conv3_top = tf.nn.relu(tf.nn.bias_add(conv3_top, biases['bc3_top']))

    # Conv + ReLU, 13-> 13
    conv4_top = tf.nn.conv2d(conv3_top, weights['wc4_top'], strides=[1, 1, 1, 1], padding='SAME')
    conv4_top = tf.nn.relu(tf.nn.bias_add(conv4_top, biases['bc4_top']))

    # Conv + ReLU + Pool, 13->6
    conv5_top = tf.nn.conv2d(conv4_top, weights['wc5_top'], strides=[1, 1, 1, 1], padding='SAME')
    conv5_top = tf.nn.relu(tf.nn.bias_add(conv5_top, biases['bc5_top']))
    pool5_top = tf.nn.max_pool(conv5_top, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

    # ------------------------------Bot Convolutions------------------------------- #
    # Conv + ReLU + LRN + Pool, 224->55->27
    conv1_bot = tf.nn.conv2d(x, weights['wc1_bot'], strides=[1, 4, 4, 1], padding='SAME')
    conv1_bot = tf.nn.relu(tf.nn.bias_add(conv1_bot, biases['bc1_bot']))
    lrn1_bot = tf.nn.local_response_normalization(conv1_bot, depth_radius=5, bias=1.0, alpha=1e-4, beta=0.75)
    pool1_bot = tf.nn.max_pool(lrn1_bot, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

    # Conv + ReLU + LRN + Pool, 27-> 13
    conv2_bot = tf.nn.conv2d(pool1_bot, weights['wc2_bot'], strides=[1, 1, 1, 1], padding='SAME')
    conv2_bot = tf.nn.relu(tf.nn.bias_add(conv2_bot, biases['bc2_bot']))
    lrn2_bot = tf.nn.local_response_normalization(conv2_bot, depth_radius=5, bias=1.0, alpha=1e-4, beta=0.75)
    pool2_bot = tf.nn.max_pool(lrn2_bot, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

    # Conv + ReLU, 13-> 13
    conv3_bot = tf.nn.conv2d(pool2_bot, weights['wc3_bot'], strides=[1, 1, 1, 1], padding='SAME')
    conv3_bot = tf.nn.relu(tf.nn.bias_add(conv3_bot, biases['bc3_bot']))

    # Conv + ReLU, 13-> 13
    conv4_bot = tf.nn.conv2d(conv3_bot, weights['wc4_bot'], strides=[1, 1, 1, 1], padding='SAME')
    conv4_bot = tf.nn.relu(tf.nn.bias_add(conv4_bot, biases['bc4_bot']))

    # Conv + ReLU + Pool, 13->6
    conv5_bot = tf.nn.conv2d(conv4_bot, weights['wc5_bot'], strides=[1, 1, 1, 1], padding='SAME')
    conv5_bot = tf.nn.relu(tf.nn.bias_add(conv5_bot, biases['bc5_bot']))
    pool5_bot = tf.nn.max_pool(conv5_bot, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')
    
    # ------------------------------Fully Connected------------------------------- #

    pool5_top_1d = tf.reshape(pool5_top, [-1, weights['wf6_top'].get_shape().as_list()[0]])
    pool5_bot_1d = tf.reshape(pool5_top, [-1, weights['wf6_top'].get_shape().as_list()[0]])

    # FC cross
    # fc6_top = tf.add(tf.matmul(pool5_top_1d, weights['wf6_tt']), biases['bf7_top'])
    fc6_top = tf.add(tf.add(tf.matmul(pool5_top_1d, weights['wf6_tt']), tf.matmul(pool5_bot_1d, weights['wf6_bt'])), biases['bf6_top'])
    fc6_top = tf.nn.relu(fc6_top)
    fc6_top = tf.nn.dropout(fc6_top, keep_dropout)

    # fc6_bot = tf.add(tf.matmul(pool5_bot_1d, weights['wf7_bb']), biases['bf7_bot'])
    fc6_bot = tf.add(tf.add(tf.matmul(pool5_top_1d, weights['wf6_tb']), tf.matmul(pool5_bot_1d, weights['wf6_bb'])), biases['bf6_bot'])
    fc6_bot = tf.nn.relu(fc6_bot)
    fc6_bot = tf.nn.dropout(fc6_bot, keep_dropout)

    # FC cross
    # fc7_top = tf.add(tf.matmul(fc6_top, weights['wf7_tt']), biases['bf7_top'])
    fc7_top = tf.add(tf.add(tf.matmul(fc6_top, weights['wf7_tt']), tf.matmul(fc6_bot, weights['wf7_bt'])), biases['bf7_top'])
    fc7_top = tf.nn.relu(fc7_top)
    fc7_top = tf.nn.dropout(fc7_top, keep_dropout)

    # fc7_bot = tf.add(tf.matmul(fc6_bot, weights['wf7_bb']), biases['bf7_bot'])
    fc7_bot = tf.add(tf.add(tf.matmul(fc6_top, weights['wf7_tb']), tf.matmul(fc6_bot, weights['wf7_bb'])), biases['bf7_bot'])
    fc7_bot = tf.nn.relu(fc7_bot)
    fc7_bot = tf.nn.dropout(fc7_bot, keep_dropout)

    # Output FC
    out = tf.add(tf.add(tf.matmul(fc7_top, weights['wo_top']), tf.matmul(fc7_bot, weights['wo_bot'])), biases['bo'])

    return out


# Construct dataloader
opt_data_train = {
    'data_h5': 'miniplaces_256_train.h5',
    # 'data_root': 'YOURPATH/images/',   # MODIFY PATH ACCORDINGLY
    # 'data_list': 'YOURPATH/train.txt', # MODIFY PATH ACCORDINGLY
    'load_size': load_size,
    'fine_size': fine_size,
    'data_mean': data_mean,
    'randomize': True
}
opt_data_val = {
    'data_h5': 'miniplaces_256_val.h5',
    # 'data_root': 'YOURPATH/images/',   # MODIFY PATH ACCORDINGLY
    # 'data_list': 'YOURPATH/val.txt',   # MODIFY PATH ACCORDINGLY
    'load_size': load_size,
    'fine_size': fine_size,
    'data_mean': data_mean,
    'randomize': False
}

# loader_train = DataLoaderDisk(**opt_data_train)
# loader_val = DataLoaderDisk(**opt_data_val)
loader_train = DataLoaderH5(**opt_data_train)
loader_val = DataLoaderH5(**opt_data_val)

# tf Graph input
x = tf.placeholder(tf.float32, [None, fine_size, fine_size, c])
y = tf.placeholder(tf.int64, None)
keep_dropout = tf.placeholder(tf.float32)

# Construct model
logits = alexnet(x, keep_dropout)

# Define loss and optimizer
loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits, y))
train_optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(loss)

# Evaluate model
accuracy1 = tf.reduce_mean(tf.cast(tf.nn.in_top_k(logits, y, 1), tf.float32))
accuracy5 = tf.reduce_mean(tf.cast(tf.nn.in_top_k(logits, y, 5), tf.float32))

# define initialization
init = tf.initialize_all_variables()

# define saver
saver = tf.train.Saver()

# define summary writer
# writer = tf.train.SummaryWriter('.', graph=tf.get_default_graph())

# Launch the graph
with tf.Session() as sess:
    # Initialization
    if len(start_from) > 1:
        saver.restore(sess, start_from)
    else:
        sess.run(init)

    step = 0

    while step < training_iters:
        # Load a batch of training data
        images_batch, labels_batch = loader_train.next_batch(batch_size)

        if step % step_display == 0:
            print '[%s]:' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            # Calculate batch loss and accuracy on training set
            l, acc1, acc5 = sess.run([loss, accuracy1, accuracy5],
                                     feed_dict={x: images_batch, y: labels_batch, keep_dropout: 1.})
            print "-Iter " + str(step) + ", Training Loss= " + \
                  "{:.4f}".format(l) + ", Accuracy Top1 = " + \
                  "{:.2f}".format(acc1) + ", Top5 = " + \
                  "{:.2f}".format(acc5)

            # Calculate batch loss and accuracy on validation set
            images_batch_val, labels_batch_val = loader_val.next_batch(batch_size)
            l, acc1, acc5 = sess.run([loss, accuracy1, accuracy5],
                                     feed_dict={x: images_batch_val, y: labels_batch_val, keep_dropout: 1.})
            print "-Iter " + str(step) + ", Validation Loss= " + \
                  "{:.4f}".format(l) + ", Accuracy Top1 = " + \
                  "{:.2f}".format(acc1) + ", Top5 = " + \
                  "{:.2f}".format(acc5)

        # Run optimization op (backprop)
        sess.run(train_optimizer, feed_dict={x: images_batch, y: labels_batch, keep_dropout: dropout})

        step += 1

        # Save model
        if step % step_save == 0:
            saver.save(sess, path_save, global_step=step)
            print "Model saved at Iter %d !" % (step)

    print "Optimization Finished!"

    # Evaluate on the whole validation set
    print 'Evaludation on the whole validation set...'
    num_batch = loader_val.size() / batch_size
    acc1_total = 0.
    acc5_total = 0.
    loader_val.reset()
    for i in range(num_batch):
        images_batch, labels_batch = loader_val.next_batch(batch_size)
        acc1, acc5 = sess.run([accuracy1, accuracy5], feed_dict={x: images_batch, y: labels_batch, keep_dropout: 1.})
        acc1_total += acc1
        acc5_total += acc5
        print "Validation Accuracy Top1 = " + \
              "{:.2f}".format(acc1) + ", Top5 = " + \
              "{:.2f}".format(acc5)

    acc1_total /= num_batch
    acc5_total /= num_batch
    print 'Evaluation Finished! Accuracy Top1 = ' + "{:.4f}".format(acc1_total) + ", Top5 = " + "{:.4f}".format(
        acc5_total)
