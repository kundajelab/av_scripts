#!/usr/bin/env python

import avutils.util as util
import avutils.file_processing as fp


def get_other_data_loaders(train_file_prefix):
    return {
        "train": {
            "class": "hdf5_data_loader.MultimodalAtOnceDataLoader",
            "kwargs": {
                "batch_size": 100,
                "path_to_hdf5": train_file_prefix+"train_data.hdf5",
                "num_to_load_for_eval": 1000,
                "bundle_x_and_y_in_generator": False,
                "strip_enclosing_dictionary": True
            }
        }
    }


def get_model_trainer(seed, pos_weight):
    return {
        "class": "keras_model_trainer.KerasFitGeneratorModelTrainer",
        "kwargs": {
            "seed": seed,
            "samples_per_epoch": 5000,
            "stopping_criterion_config": {
                "class": "EarlyStopping" ,
                "kwargs": {
                   "max_epochs": 80, 
                   "epochs_to_wait": 80,
                   "running_mean_over_epochs": 1
                } 
            },
            "class_weight": {"0":1, "1":pos_weight}
        }
    }


def get_model_creator(nlayers, stride, nb_filter, revcomp):
    if revcomp:
        conv_class =  "keras.layers.convolutional.RevCompConv1D"
        batchnorm_class = "keras.layers.normalization.RevCompConv1DBatchNorm"
        dense_class = "keras.layers.core.DenseAfterRevcompConv1D"
        dense_init = "glorot_uniform_2xin"
    else:
        conv_class =  "keras.layers.convolutional.Convolution1D"
        batchnorm_class = "keras.layers.normalization.BatchNormalization"
        dense_class = "keras.layers.core.Dense"
        dense_init = "glorot_uniform"

    conv_block = []
    assert nlayers <= 3
    if (nlayers == 3):
        filter_lengths = [15, 14, 14]     
    elif (nlayers == 2):
        filter_lengths = [21, 21]
    elif (nlayers == 1):
        filter_lengths = [41]

    for filter_length in filter_lengths: 
        conv_block.extend([
            {
                "class": conv_class, 
                "kwargs": {
                    "input_shape": [1000,4],
                    "nb_filter": nb_filter,
                    "filter_length": filter_length,
                }
            },
            {
                "class": batchnorm_class,
                "kwargs": {}
            },
            {
                "class": "keras.layers.core.Activation", 
                "kwargs": {"activation": "relu"}
            }])

    return {
        "class": "flexible_keras.FlexibleKerasSequential",
        "kwargs": {
            "layers_config": (conv_block+[
                {
                    "class": "keras.layers.convolutional.MaxPooling1D", 
                    "kwargs": {"pool_length": 40, "stride": stride}
                }]+([{
                     "class": "keras.layers.core.Flatten", 
                     "kwargs": {}
                     }] if revcomp==False else [])
                +[
                {
                    "class": dense_class, 
                    "kwargs": {"output_dim": 1,
                               "init": dense_init}
                },
                {
                    "class": "keras.layers.core.Activation", 
                    "kwargs": {"activation": "sigmoid"}
                }]),
            "optimizer_config": {
                "class": "keras.optimizers.Adam",
                "kwargs": {"lr": 0.001}
            },
            "loss": "binary_crossentropy" 
        } 
    }


def get_hyperparameter_configs(prefix, nlayers, stride,
                               nb_filter, revcomp,
                               seed, pos_weight,
                               train_file_prefix=""):
    message = (prefix
               +("-"+train_file_prefix if (len(train_file_prefix) > 0) else "")
               +" nlay_"+str(nlayers)
               +"-rc_"+('t' if revcomp else 'f')
               +"-nbf_"+str(nb_filter)
               +"_str-"+str(stride)
               +" seed-"+str(seed))
    return {
        "message": message,
        "other_data_loaders": get_other_data_loaders(train_file_prefix=train_file_prefix),
        "model_creator": get_model_creator(nlayers=nlayers, stride=stride,
                            nb_filter=nb_filter,
                            revcomp=revcomp),
        "model_trainer": get_model_trainer(seed=seed, pos_weight=pos_weight)   
    }


def main(args):
    stride=20
    possible_settings = [
        {"nlayers": 3,"nb_filter": 16, "revcomp":True,
         "train_file_prefix":"subsets/10pc/"}, #rev
        {"nlayers": 3,"nb_filter": 32, "revcomp":False,
         "train_file_prefix":"rc/subsets/10pc/"}, #norev
        {"nlayers": 3,"nb_filter": 16, "revcomp":False,
         "train_file_prefix":"rc/subsets/10pc/"}, #no rev
    ]
    hyperparameter_configs_0to4 = []
    hyperparameter_configs_5to9 = []
    for seed in range(0,5):
        for settings in possible_settings: 
            hyperparameter_configs_0to4.append(
                get_hyperparameter_configs(prefix=args.prefix,
                 stride=stride, seed=seed,
                 pos_weight=args.pos_weight, **settings))
            hyperparameter_configs_5to9.append(
                get_hyperparameter_configs(prefix=args.prefix,
                 stride=stride, seed=seed+5,
                 pos_weight=args.pos_weight, **settings))
            
    #fp.write_to_file("hyperparameter_configs.yaml",
    #                 util.format_as_json(hyperparameter_configs_0to4+
    #                                     hyperparameter_configs_5to9))
    fp.write_to_file("set1_hyperparameter_configs.yaml",
                     util.format_as_json(hyperparameter_configs_0to4))
    fp.write_to_file("set2_hyperparameter_configs.yaml",
                     util.format_as_json(hyperparameter_configs_5to9))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix")
    parser.add_argument("pos_weight", type=float)
    main(parser.parse_args())
