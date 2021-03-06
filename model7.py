# モデル7
#
# Early Stopping
#

import time
from datetime import datetime
from load_data import load2d
from saver import save_arch, save_history
from utils import reshape2d_by_image_dim_ordering
from plotter import plot_hist, plot_model_arch
import pickle

import numpy as np
# This module will be removed in 0.20.
from sklearn.cross_validation import train_test_split

from data_generator import FlippedImageDataGenerator
from keras.models import Sequential
from keras.layers import Convolution2D, MaxPooling2D, Flatten, Dense, Activation, Dropout
from keras.optimizers import SGD
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping
from keras import backend as K


# 変数
model_name = 'model7'
nb_epoch = 5000
validation_split = 0.2
lr = 0.01
start = 0.03
stop = 0.001
learning_rates = np.linspace(start, stop, nb_epoch)
patience = 100 # EarlyStoppingでn回連続でエラーの最小値が更新されなかったらストップさせる
momentum = 0.9
nesterov = True
loss_method = 'mean_squared_error'
arch_path = 'model/' + model_name + '-arch-' + str(nb_epoch) + '.json'
weights_path = 'model/' + model_name + '-weights-' + str(nb_epoch) + '.hdf5'


# データ読み込み
X, y = load2d()
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=validation_split, random_state=42)

# image_dim_orderring に合わせて2D画像のshapeを変える
X_train, input_shape = reshape2d_by_image_dim_ordering(X_train)
X_val,   _           = reshape2d_by_image_dim_ordering(X_val)


# モデル定義
model = Sequential()

model.add(Convolution2D(32, 3, 3, input_shape=input_shape))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.1))

model.add(Convolution2D(64, 2, 2))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.2))

model.add(Convolution2D(128, 2, 2))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.3))

model.add(Flatten())
model.add(Dense(1000))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1000))
model.add(Activation('relu'))
model.add(Dense(30))

save_arch(model, arch_path) # モデルを保存しておく


# トレーニングの準備
checkpoint_collback = ModelCheckpoint(filepath = weights_path,
                                      monitor='val_loss',
                                      save_best_only=True,
                                      mode='auto')

change_lr = LearningRateScheduler(lambda epoch: float(learning_rates[epoch]))

early_stop = EarlyStopping(patience=patience) # patience回連続でエラーの最小値が更新されなかったらストップさせる

flip_gen = FlippedImageDataGenerator()

sgd = SGD(lr=lr, momentum=momentum, nesterov=nesterov)
model.compile(loss=loss_method, optimizer=sgd)


# トレーニング
start_time = time.time()
print('start_time: %s' % (datetime.now()))
hist = model.fit_generator(flip_gen.flow(X_train, y_train),
                           samples_per_epoch=X_train.shape[0],
                           nb_epoch=nb_epoch,
                           validation_data=(X_val, y_val),
                           callbacks=[checkpoint_collback, change_lr, early_stop])
print('end_time: %s, duracion(min): %d' % (datetime.now(), int(time.time()-start_time) / 60))


# プロットしてファイルとして保存する
# plot_hist(hist, model_name)
# plot_model_arch(model, model_name)
save_history(hist, model_name)
