from params import *
import tensorflow as tf
import numpy as np
import time
import datetime

channel = 128

def ConvBlock(x):
    x = tf.layers.conv2d(x, channel, 3, strides=1, padding='same', name='conv')
    x = tf.layers.batch_normalization(x)
    x = tf.nn.relu(x)
    return x

def ResidualBlock(h):
    with tf.variable_scope('res'):
        x = tf.layers.conv2d(h, channel, 3, strides=1, padding='same', name='conv1')
        x = tf.layers.batch_normalization(x, name='bn1')
        x = tf.nn.relu(x)
        x = tf.layers.conv2d(x, channel, 3, strides=1, padding='same', name='conv2')
        x = tf.layers.batch_normalization(x, name='bn2')
        x = x + h
        x = tf.nn.relu(x)
        return x

def PolicyOutputBlock(x, board_size, output_size):
    with tf.variable_scope('policy_output'):
        x = tf.layers.conv2d(x, 2, 1, strides=1, padding='same', name='conv')
        x = tf.layers.batch_normalization(x)
        x = tf.nn.relu(x)
        x = tf.layers.flatten(x)
        x = tf.layers.dense(x, output_size, name='fc')
        x = tf.nn.softmax(x)
        return x

def ValueOutputBlock(x, board_size):
    with tf.variable_scope('value_output'):
        x = tf.layers.conv2d(x, 1, 1, strides=1, padding='same', name='conv')
        
        x = tf.layers.flatten(x)
        x = tf.layers.batch_normalization(x)
        
        x = tf.nn.relu(x)
        x = tf.layers.dense(x, channel, name='fc1')
        x = tf.nn.relu(x)
        x = tf.layers.dense(x, 1, name='fc2')
        x = tf.nn.tanh(x)
        return x



class Network:
    def __init__(self, board_size, input_frame_num, residual_num, is_trainable):
        self.board_size = board_size
        self.input_frame_num = input_frame_num
        self.residual_num = residual_num

        self.g = tf.Graph()
        with self.g.as_default():
            self.X = tf.placeholder(tf.float32, [None, self.board_size, self.board_size, self.input_frame_num])
            self.pi = tf.placeholder(tf.float32, [None, self.board_size**2])
            self.Z = tf.placeholder(tf.float32, [None, 1])

            X = ConvBlock(self.X)
            
            for i in range(self.residual_num):
                with tf.variable_scope('res_%d' % i):
                    X = ResidualBlock(X)
            self.P = PolicyOutputBlock(X, self.board_size, self.board_size**2)
            self.V = ValueOutputBlock(X, self.board_size)
           

            var = tf.trainable_variables()
            theta = tf.reduce_mean(tf.add_n([tf.nn.l2_loss(v) for v in var]) )*1e-4
            self.value_loss = tf.reduce_mean((self.Z - self.V)**2)
            self.policy_loss = tf.reduce_mean( - tf.reduce_sum( tf.multiply(self.pi, tf.log(tf.maximum(self.P,1e-7))), 1, keep_dims=True))
            #self.policy_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=self.pi, logits=self.P))
            self.loss = self.value_loss + self.policy_loss + theta
            
            learning_rate = 1e-4 #0.01 # TODO apply learning step anneling
            optimizer = tf.train.AdamOptimizer(learning_rate, 0.9)
            self.train_model = optimizer.minimize(self.loss)
            self.init = tf.global_variables_initializer()
            
            self.saver = tf.train.Saver()


        self.sess = tf.Session(graph = self.g)
        self.is_trainable = is_trainable
        if is_trainable == True:
            self.sess.run(self.init)
        else:
            self.saver.restore(self.sess,"./AlphaGomoku.ckpt")

    def train(self, X_, pi_, Z_, TOTAL_BATCH_SIZE):
        if self.is_trainable:
            for batch in range(TOTAL_BATCH_SIZE//BATCH_SIZE):
                fd = {
                    self.X: X_[batch*BATCH_SIZE:(batch+1)*BATCH_SIZE],
                    self.pi: pi_[batch*BATCH_SIZE:(batch+1)*BATCH_SIZE],
                    self.Z: Z_[batch*BATCH_SIZE:(batch+1)*BATCH_SIZE]
                }
                self.sess.run(self.train_model, feed_dict=fd)

                fd = {self.X: X_, self.pi: pi_, self.Z: Z_}
                l, pl, vl = self.sess.run([self.loss, self.policy_loss, self.value_loss], feed_dict=fd)
                print('batch: ', batch, ' loss: ' , l, ' policy loss: ', pl, ' value loss: ', vl)

            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
            save_path = self.saver.save(self.sess,"./AlphaGomoku_"+st+".ckpt")

    def get_output(self, X_):
        return self.sess.run([self.P, self.V], feed_dict={self.X: X_})

