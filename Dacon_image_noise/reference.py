import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.preprocessing.image import ImageDataGenerator
from numpy import expand_dims
from sklearn.model_selection import StratifiedKFold
from keras import Sequential
from keras.layers import *
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.optimizers import Adam



train = pd.read_csv('../data/csv/practice/train.csv')
test = pd.read_csv('../data/csv/practice/test.csv')
sub = pd.read_csv('../data/csv/practice/submission.csv')

train2 = train.drop(['id','digit','letter'],1)
test2 = test.drop(['id','letter'],1)

# convert pandas dataframe to numpy array
train2 = train2.values
test2 = test2.values

# reshape
train2 = train2.reshape(-1,28,28,1)
test2 = test2.reshape(-1,28,28,1)

# data normalization
train2 = train2/255.0
test2 = test2/255.0

# # show augmented image data
# sample_data = train2[100].copy()
# sample = expand_dims(sample_data,0)
# sample_datagen = ImageDataGenerator(height_shift_range=(-1,1), width_shift_range=(-1,1))
# sample_generator = sample_datagen.flow(sample, batch_size=1)

# plt.figure(figsize=(16,10))

# for i in range(9) : 
#     plt.subplot(3,3,i+1)
#     sample_batch = sample_generator.next()
#     sample_image=sample_batch[0]
#     plt.imshow(sample_image.reshape(28,28))


# from sklearn.model_selection import train_test_split

# x_train, x_test, y_train, y_test = train_test_split(x,y1, test_size=0.2,
#                                             random_state =110) 

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Conv2D,MaxPooling2D,Dropout,Flatten


idg = ImageDataGenerator(height_shift_range=(-1,1),width_shift_range=(-1,1))
idg2 = ImageDataGenerator()


reLR = ReduceLROnPlateau(patience=100,verbose=1,factor=0.5) #learning rate scheduler
es = EarlyStopping(patience=160, verbose=1)

val_loss_min = []
result = 0
nth = 0

# cross validation
skf = StratifiedKFold(n_splits=40, random_state=42, shuffle=True)

for train_index, valid_index in skf.split(train2,train['digit']) :
    
    mc = ModelCheckpoint('best_cvision.h5',save_best_only=True, verbose=1)
    
    x_train = train2[train_index]
    x_valid = train2[valid_index]    
    y_train = train['digit'][train_index]
    y_valid = train['digit'][valid_index]
    
    train_generator = idg.flow(x_train,y_train,batch_size=8)
    valid_generator = idg2.flow(x_valid,y_valid)
    test_generator = idg2.flow(test2,shuffle=False)
    
    model = Sequential()
    
    model.add(Conv2D(16,(3,3),activation='relu',input_shape=(28,28,1),padding='same'))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))
    
    model.add(Conv2D(32,(3,3),activation='relu',padding='same'))
    model.add(BatchNormalization())
    model.add(Conv2D(32,(5,5),activation='relu',padding='same')) 
    model.add(BatchNormalization())
    model.add(Conv2D(32,(5,5),activation='relu',padding='same'))
    model.add(BatchNormalization())
    model.add(Conv2D(32,(5,5),activation='relu',padding='same'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D((3,3)))
    model.add(Dropout(0.3))
    
    model.add(Conv2D(64,(3,3),activation='relu',padding='same'))
    model.add(BatchNormalization())
    model.add(Conv2D(64,(5,5),activation='relu',padding='same')) 
    model.add(BatchNormalization())
    model.add(MaxPooling2D((3,3)))
    model.add(Dropout(0.3))
    
    model.add(Flatten())

    model.add(Dense(128,activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))
    model.add(Dense(64,activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.3))

    model.add(Dense(10,activation='softmax'))
    
    model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(lr=0.002,epsilon=None),
                    metrics=['acc'])
    
    learning_history = model.fit_generator(train_generator,epochs=2000, 
        validation_data=valid_generator, callbacks=[es,mc,reLR])
    
    # predict
    model.load_weights('best_cvision.h5')
    result += model.predict_generator(test_generator,verbose=True)/40
    
    # save val_loss
    hist = pd.DataFrame(learning_history.history)
    val_loss_min.append(hist['val_loss'].min())
    
    nth += 1
    print(nth, '?????? ????????? ??????????????????.')

sub['digit'] = result.argmax(1)
sub.to_csv('../data/csv/practice/Dacon3.csv',index=False)