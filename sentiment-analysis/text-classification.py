import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt

print("tf.version: " + str(tf.__version__))

# download imdb dataset
imdb = keras.datasets.imdb
(train_data, train_labels), (test_data, test_labels) = imdb.load_data(num_words=25000)

# explore data
print("training entries: {}, labels: {}".format(len(train_data), len(train_labels)))

print("first entry in train_data: " + str(train_data[0]))

print("length of first entry in train_data: " + str(len(train_data[0])))
print("length of second entry in train_data: "+ str(len(train_data[1])))

# dictionary mapping words to an integer index
word_index = imdb.get_word_index()

# The first indices are reserved
word_index = {k:(v+3) for k,v in word_index.items()}
word_index["<PAD>"] = 0
word_index["<START>"] = 1
word_index["<UNK>"] = 2  # unknown
word_index["<UNUSED>"] = 3

reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def decode_review(text):
    return ' '.join([reverse_word_index.get(i, '?') for i in text])

print("train_data[0] decoded: " + str(decode_review(train_data[0])))

# prepare data
train_data = keras.preprocessing.sequence.pad_sequences(train_data,
                                                        value=word_index["<PAD>"],
                                                        padding='post',
                                                        maxlen=256)

test_data = keras.preprocessing.sequence.pad_sequences(test_data,
                                                       value=word_index["<PAD>"],
                                                       padding='post',
                                                       maxlen=256)

print("length of first padded entry in train_data: " + str(len(train_data[0])))
print("length of second padded entry in train_data: "+ str(len(train_data[1])))

print("first padded entry in train_data: " + str(train_data[0]))

# build model
vocab_size = 25000

model = keras.Sequential()
model.add(keras.layers.Embedding(vocab_size, 16))
model.add(keras.layers.GlobalAveragePooling1D())
model.add(keras.layers.Dense(16, activation=tf.nn.relu))
model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

print("model summary: " + str(model.summary()))

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['acc'])

# create validation set 
x_val = train_data[:10000]
partial_x_train = train_data[10000:]

y_val = train_labels[:10000]
partial_y_train = train_labels[10000:]

# train model
history = model.fit(partial_x_train,
                    partial_y_train,
                    epochs=40,
                    batch_size=512,
                    validation_data=(x_val, y_val),
                    verbose=1)

# evaluate model
results = model.evaluate(test_data, test_labels)
print("results: " + str(results))

# create graph
history_dict = history.history
print("history keys: " + str(history_dict.keys()))

acc = history_dict['acc']
val_acc = history_dict['val_acc']
loss = history_dict['loss']
val_loss = history_dict['val_loss']

epochs = range(1, len(acc) + 1)

# "bo" is for "blue dot"
plt.plot(epochs, loss, 'bo', label='Training loss')
# b is for "solid blue line"
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.savefig("epochs_loss.svg")

plt.clf()   # clear figure

plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

plt.savefig("epochs_accuracy.svg")

