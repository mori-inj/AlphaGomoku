import tensorflow as tf
import numpy as np
import os

def ConvBlock(x):
    x = tf.layers.conv2d(x, 256, 3, strides=1, padding='same', name='conv')
    x = tf.layers.batch_normalization(x)
    x = tf.nn.relu(x)
    return x

def ResidualBlock(h):
    with tf.variable_scope('res'):
        x = tf.layers.conv2d(h, 256, 3, strides=1, padding='same', name='conv1')
        x = tf.layers.batch_normalization(x, name='bn1')
        x = tf.nn.relu(x)
        x = tf.layers.conv2d(x, 256, 3, strides=1, padding='same', name='conv2')
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
        x = tf.layers.dense(x, 256, name='fc1')
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
            
            learning_rate = 0.001 #0.01 # TODO apply learning step anneling
            optimizer = tf.train.MomentumOptimizer(learning_rate, 0.9)
            self.train_model = optimizer.minimize(self.loss)
            self.init = tf.global_variables_initializer()
            
            self.saver = tf.train.Saver()


        self.sess = tf.Session(graph = self.g)
        self.is_trainable = is_trainable
        if is_trainable == True:
            self.sess.run(self.init)
        else:
            self.saver.restore(self.sess,"./AlphaGomoku.ckpt")

        f = open("/dev/shm/con_network_ready","w")
        f.close()
            
        while os.path.isfile("/dev/shm/con_python_enable"):
            if os.path.isfile("/dev/shm/con_network_input.txt"):
                input_data = []
                while len(input_data) == 0:
                    with open("/dev/shm/con_network_input.txt") as f:
                        input_data = f.readlines() 
                os.system("rm /dev/shm/con_network_input.txt")
                input_data = [x.strip() for x in input_data]

                cnt = 0
                s = [0] * input_frame_num
                for fn in range(input_frame_num):
                    f = np.zeros([board_size, board_size])
                    for i in range(board_size):
                        t = input_data[cnt].split(' ')
                        t = [float(x) for x in t]
                        cnt += 1
                        for j in range(board_size):
                            f[i][j] = t[j]
                    s[fn] = f
                    cnt += 1
                s = np.asarray([s])
                s = np.transpose(s, [0, 2, 3, 1])

                P,V = self.get_output(s)
                P = np.reshape(P, [board_size, board_size])
                
                f = open("/dev/shm/con_network_output.txt_","w")
                for i in range(board_size):
                    s = ""
                    for j in range(board_size):
                        s += str(float(P[i][j])) + " "
                    f.write(s+"\n")
                f.write(str(float(V))+"\n")
                f.close()
                os.system("mv /dev/shm/con_network_output.txt_ /dev/shm/con_network_output.txt")

            if os.path.isfile("/dev/shm/con_train_data.txt"):
                f = open("/dev/shm/con_network_training","w")
                f.close()

                input_data = []
                while len(input_data) == 0:
                    with open("/dev/shm/con_train_data.txt") as f:
                        input_data = f.readlines() 
                os.system("rm /dev/shm/con_train_data.txt")
                input_data = [x.strip() for x in input_data]

                data_num = int(input_data[0].split(' ')[0])
                iteration = int(input_data[0].split(' ')[1])
                print_iter = int(input_data[0].split(' ')[2])

                input_data = input_data[1:]

                X = np.zeros([data_num, input_frame_num]).tolist()
                P = [0] * data_num
                Z = [0] * data_num

                cnt = 0
                for n in range(data_num):
                    for fn in range(input_frame_num):
                        X[n][fn] = np.zeros([board_size, board_size])
                        for i in range(board_size):
                            t = input_data[cnt].split(' ')
                            t = [float(x) for x in t]
                            for j in range(board_size):
                                X[n][fn][i][j] = t[j]
                            cnt += 1
                        cnt += 1

                    P[n] = np.zeros([board_size, board_size])
                    for i in range(board_size):
                        t = input_data[cnt].split(' ')
                        t = [float(x) for x in t]
                        for j in range(board_size):
                            P[n][i][j] = t[j]
                        cnt += 1
                    Z[n] = [float(input_data[cnt])]
                    cnt += 1
                    cnt += 1

                X = np.asarray(X)
                P = np.asarray(P)
                Z = np.asarray(Z)

                X = np.transpose(X, [0,2,3,1])
                P = np.reshape(P, [-1,board_size*board_size])

                self.train(X, P, Z, iteration, print_iter)

                os.system("rm /dev/shm/con_network_training")


    def train(self, X_, pi_, Z_, it, prt_it):
        if self.is_trainable:
            for i in range(it): # TODO should change # of iteration steps
                for batch in range(BATCH_SIZE//MINI_BATCH_SIZE):
                    fd = {
                            self.X: X_[batch*MINI_BATCH_SIZE:(batch+1)*MINI_BATCH_SIZE],
                            self.pi: pi_[batch*MINI_BATCH_SIZE:(batch+1)*MINI_BATCH_SIZE],
                            self.Z: Z_[batch*MINI_BATCH_SIZE:(batch+1)*MINI_BATCH_SIZE]
                    }
                    self.sess.run(self.train_model, feed_dict=fd)

                fd = {self.X: X_, self.pi: pi_, self.Z: Z_}
                if i % prt_it == 0:
                    print('======= ' + str(i) + ' =======')
                    l, pl, vl = self.sess.run([self.loss, self.policy_loss, self.value_loss], feed_dict=fd)
                    print('loss: ' , l)
                    print('policy loss: ', pl)
                    print('value loss: ', vl)
                    save_path = self.saver.save(self.sess,"./AlphaGomoku.ckpt")

    def get_output(self, X_):
        return self.sess.run([self.P, self.V], feed_dict={self.X: X_})

