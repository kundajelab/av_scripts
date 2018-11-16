#!/usr/bin/env python

import avutils.util as util
import avutils.file_processing as fp
from collections import OrderedDict


def get_other_data_loaders(train_size):
    return {
        "train": {
            "class": "hdf5_data_loader.MultimodalAtOnceDataLoader",
            "kwargs": {
                "batch_size": 50,
                "path_to_hdf5": "train_data_"+str(train_size)+".hdf5",
                "num_to_load_for_eval": 1000,
                "bundle_x_and_y_in_generator": False,
                "strip_enclosing_dictionary": False
            }
        }
    }


def get_model_trainer(seed):
    return {
        "class": "keras_model_trainer.KerasFitGeneratorModelTrainer",
        "kwargs": {
            "seed": seed,
            "samples_per_epoch": 5000,
            "stopping_criterion_config": {
                "class": "EarlyStopping" ,
                "kwargs": {
                   "max_epochs": 30, 
                   "epochs_to_wait": 30,
                   "running_mean_over_epochs": 1
                } 
            },
            "class_weight": {"0":1, "1":1}
        }
    }


def get_model_creator(weights_file, num_filt, maxpoolfilt, fullysep):

    return {
        "class": "flexible_keras.FlexibleKerasFunctional",
        "kwargs": {
            "input_names": ["sequence"],
            "shared_layers_config": {},
            "nodes_config": OrderedDict([
                ("sequence", {
                    "layer": {
                        "class": "keras.layers.Input",
                        "kwargs": {"shape": [200,4]}
                    }
                }),
                ("conv1", {
                    "layer": {
                        "class": "keras.layers.convolutional.Convolution1DFromWeightFile", 
                        "kwargs": {
                            "weight_file": weights_file+".npy",
                            "trainable": False
                        }
                    },
                    "input_node_names": "sequence"
                }),
                ("relu1", {
                    "layer": {
                        "class": "keras.layers.core.Activation", 
                        "kwargs": {"activation": "relu"}
                    },
                    "input_node_names": "conv1"
                })]+([
                ("mp_filter", {
                    "layer": {
                        "class": "keras.layers.pooling.MaxPoolingFilter1D", 
                        "kwargs": {"pool_length": 5}
                    },
                    "input_node_names": "relu1"
                })] if maxpoolfilt else [])
                +[("conv2", {
                    "layer": {
                        "class": ("keras.layers.convolutional."
                                 +("FullySepSplitConv1D" if fullysep else "Convolution1D")), 
                        "kwargs": {
                            "nb_filter": num_filt,
                            ("half_filter_length" if fullysep
                              else "filter_length"): (15 if fullysep else 30),
                            "border_mode": "same",
                        }
                    },
                    "input_node_names": ("mp_filter" if maxpoolfilt else "relu1")
                }),
                ("relu2", {
                    "layer": {
                        "class": "keras.layers.core.Activation", 
                        "kwargs": {"activation": "relu"}
                    },
                    "input_node_names": "conv2"
                }),
                ("maxpool", {
                    "layer": {
                        "class": "keras.layers.convolutional.MaxPooling1D", 
                        "kwargs": {"pool_length": 40, "stride": 40}
                    },
                    "input_node_names": "relu2"
                }),
                ("dense", {
                    "layer": {
                        "class": "keras.layers.convolutional.SeparableFC", 
                        "kwargs": {"output_dim": 1,
                                   "symmetric": True}
                    },
                    "input_node_names": "maxpool"
                }),
                ("output", {
                    "layer": {
                        "class": "keras.layers.core.Activation", 
                        "kwargs": {"activation": "sigmoid"}
                    },
                    "input_node_names": "dense"
                })
            ]),
            "output_names": ["output"],
            "optimizer_config": {
                "class": "keras.optimizers.Adam",
                "kwargs": {"lr": 0.001}
            },
            "loss_dictionary": {
                "output": "binary_crossentropy" 
            }
        } 
    }


def get_hyperparameter_configs(prefix, seed,
                               weights_file, num_filt,
                               maxpoolfilt, fullysep, 
                               train_size):
    message = (prefix
               +" fullysep_"+str(fullysep)
               +"-maxpoolfilt_"+str(maxpoolfilt)
               +"-trainsize_"+str(train_size)
               +"-weightsfile_"+str(weights_file)
               +"-numfilt_"+str(num_filt)
               +" seed-"+str(seed))
    return {
        "message": message,
        "other_data_loaders": get_other_data_loaders(train_size=train_size),
        "model_creator": get_model_creator(
                            weights_file=weights_file,
                            num_filt=num_filt,
                            maxpoolfilt=maxpoolfilt,
                            fullysep=fullysep),
        "model_trainer": get_model_trainer(seed=seed)   
    }


def main(args):
    possible_settings = [
        {"weights_file": "weights_minimal", "num_filt": 1, "maxpoolfilt": False, "fullysep": False},
        #{"weights_file": "weights_minimal", "num_filt": 1, "maxpoolfilt": True, "fullysep": False},
        {"weights_file": "weights_minimal", "num_filt": 1, "maxpoolfilt": False, "fullysep": True},
        {"weights_file": "weights_minimal", "num_filt": 2, "maxpoolfilt": False, "fullysep": True},
        #{"weights_file": "weights_minimal", "num_filt": 1, "maxpoolfilt": True, "fullysep": True},
        {"weights_file": "weights_all", "num_filt": 1, "maxpoolfilt": False, "fullysep": False},
        {"weights_file": "weights_all", "num_filt": 1, "maxpoolfilt": False, "fullysep": True},
        {"weights_file": "weights_all", "num_filt": 11, "maxpoolfilt": False, "fullysep": True},
       # {"weights_file": "weights_all", "num_filt": 5, "maxpoolfilt": False, "fullysep": True},
    ]
    hyperparameter_configs = []
    for seed in range(0,10):
        for train_size in [100]:#, 200, 400, 800, 1600, 3200, 6400, 12800]:
            for settings in possible_settings: 
                hyperparameter_configs.append(
                    get_hyperparameter_configs(prefix=args.prefix,
                     seed=seed,
                     train_size=train_size,
                     **settings))
    fp.write_to_file("config/hyperparameter_configs_list.yaml",
                     util.format_as_json(hyperparameter_configs))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix")
    main(parser.parse_args())
