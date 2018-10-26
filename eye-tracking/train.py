import os
from keras.optimizers import SGD, Adam
from keras.callbacks import  EarlyStopping, ModelCheckpoint, History
from load_data import load_data_from_npz, load_batch, load_data_names, load_batch_from_names_random
from model_vgg import get_eye_tracker_model


# generator for data loaded from the npz file
def generator_npz(data, batch_size, img_ch, img_cols, img_rows):

    while True:
        for it in list(range(0, data[0].shape[0], batch_size)):
            x, y = load_batch([l[it:it + batch_size] for l in data], img_ch, img_cols, img_rows)
            yield x, y


# generator with random batch load (train)
def generator_train_data(names, path, batch_size,img_ch, img_cols, img_rows):

    while True:
        x, y = load_batch_from_names_random(names, path, batch_size, img_ch, img_cols, img_rows)
        yield x, y


# generator with random batch load (validation)
def generator_val_data(names, path, batch_size, img_ch, img_cols, img_rows):

    while True:
        x, y = load_batch_from_names_random(names, path, batch_size, img_ch, img_cols, img_rows)
        yield x, y


def train(args):

    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = args.dev

    #todo: manage parameters in main
    if args.data == "big":
        dataset_path = r"D:\gazecapture_small"
    if args.data == "small":
        dataset_path = "/cvgl/group/GazeCapture/eye_tracker_train_and_val.npz"

    if args.data == "big":
        train_path = r"C:\Users\Aliab\PycharmProjects\data_small\train"
        val_path = r"C:\Users\Aliab\PycharmProjects\data_small\validation"
        test_path = r"C:\Users\Aliab\PycharmProjects\data_small\test"

    print("{} dataset: {}".format(args.data, dataset_path))

    # train parameters
    n_epoch = args.max_epoch
    batch_size = args.batch_size
    patience = args.patience

    # image parameter
    img_cols = 128
    img_rows = 128
    img_ch = 3

    # model
    model = get_eye_tracker_model(img_ch, img_cols, img_rows)

    # model summary
    model.summary()

    # weights
    # print("Loading weights...",  end='')
    # weights_path = "weights/weights.003-4.05525.hdf5"
    # model.load_weights(weights_path)
    # print("Done.")

    # optimizer
    sgd = SGD(lr=0.001, decay=1e-4, momentum=9e-1, nesterov=True)
    adam = Adam(lr=1e-3)

    # compile model
    model.compile(loss='mse', optimizer=sgd, metrics=['accuracy'])

    # data
    # todo: parameters not hardocoded
    if args.data == "big":
        # train data
        train_names = load_data_names(train_path)
        # validation data
        val_names = load_data_names(val_path)
        # test data
        test_names = load_data_names(test_path)

    if args.data == "small":
        train_data, val_data = load_data_from_npz(dataset_path)

    # debug
    # x, y = load_batch([l[0:batch_size] for l in train_data], img_ch, img_cols, img_rows)
    # x, y = load_batch_from_names(train_names[0:batch_size], dataset_path, img_ch, img_cols, img_rows)

    # last dataset checks
    if args.data == "small":
        print("train data sources of size: {} {} {} {} {}".format(
            train_data[0].shape[0], train_data[1].shape[0], train_data[2].shape[0],
            train_data[3].shape[0], train_data[4].shape[0]))
        print("validation data sources of size: {} {} {} {} {}".format(
            val_data[0].shape[0], val_data[1].shape[0], val_data[2].shape[0],
            val_data[3].shape[0], val_data[4].shape[0]))

    if args.data == "big":
        history = History()

        history = model.fit_generator(
            generator=generator_train_data(train_names, dataset_path, batch_size, img_ch, img_cols, img_rows),
            steps_per_epoch=(len(train_names)) / batch_size,
            epochs=n_epoch,
            verbose=1,
            validation_data=generator_val_data(val_names, dataset_path, batch_size, img_ch, img_cols, img_rows),
            validation_steps=(len(val_names)) / batch_size,
            callbacks=[EarlyStopping(patience=patience), history,
                       ModelCheckpoint(r"weights.hdf5", monitor='val_loss', save_best_only=True)
                       ]
        )
        print(history.history)
