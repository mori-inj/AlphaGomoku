import tensorflow as tf
import numpy as np

def ConvBlock(x):
    x = tf.layers.conv2d(x, 256, 3, strides=1, padding='same', name='conv')
    x = tf.layers.batch_normalization(x)
    x = tf.nn.relu(x)
    return x

def ResidualBlock(x_):
    with tf.variable_scope('res'):
        x = tf.layers.conv2d(x_, 256, 3, strides=1, padding='same', name='conv1')
        x = tf.layers.batch_normalization(x, name='bn1')
        x = tf.nn.relu(x)
        x = tf.layers.conv2d(x, 256, 3, strides=1, padding='same', name='conv2')
        x = tf.layers.batch_normalization(x, name='bn2')
        x = x + x_
        x = tf.nn.relu(x)
        return x

def PolicyOutputBlock(x, output_size):
    with tf.variable_scope('policy_output'):
        x = tf.layers.conv2d(x, 2, 1, strides=1, padding='same', name='conv')
        x = tf.layers.batch_normalization(x)
        x = tf.nn.relu(x)
        x = tf.layers.dense(x, output_size)
        return x

def ValueOutputBlock(x):
    with tf.variable_scope('value_output'):
        x = tf.layers.conv2d(x, 1, 1, strides=1, padding='same', name='conv')
        x = tf.layers.batch_normalization(x)
        x = tf.nn.relu(x)
        x = tf.layers.dense(x, 256, name='fc1')
        x = tf.nn.relu(x)
        x = tf.layers.dense(x, 1, name='fc2')
        x = tf.nn.tanh(x)
        return x



class PolicyValueNetwork:
    def __init__(self, board_size, input_frame_num, residual_num):
        self.board_size = board_size
        self.input_frame_num = input_frame_num
        self.residual_num = residual_num

        self.g = tf.Graph()
        with self.g.as_default():
            self.X = tf.placeholder(tf.float32, [None, self.board_size, self.board_size, self.input_frame_num])
            self.pi = tf.placeholder(tf.float32, [None, self.board_size*self.board_size])
            self.Z = tf.placeholder(tf.float32, [None, 1])

            self.X = ConvBlock(self.X)
            for i in range(self.residual_num):
                with tf.variable_scope('res_%d' % i):
                    self.X = ResidualBlock(self.X)
            self.P = PolicyOutputBlock(self.X, self.board_size*self.board_size)
            self.V = ValueOutputBlock(self.X)
            
            var = tf.trainable_variables()
            theta = tf.add_n([tf.nn.l2_loss(v) for v in var]) * 1e-4
            loss = tf.reduce_mean((self.Z-self.V)**2 - self.pi * tf.log(self.P) + theta)
            learning_rate = 0.02
            optimizer = tf.train.MomentumOptimizer(learning_rate, 0.9)
            train_model = optimizer.minimize(loss)

    def train(self,):
        pass

    def get_output(self, ):
        pass
        

