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


def get_model_creator(nlayers, stride, nb_filter, revcomp,
                      ws,
                      symws,
                      ircws):
    if (symws):
        assert ws
    if (ircws):
        assert ws
    if revcomp:
        conv_class =  "keras.layers.convolutional.RevCompConv1D"
        batchnorm_class = "keras.layers.normalization.RevCompConv1DBatchNorm"
    else:
        conv_class =  "keras.layers.convolutional.Convolution1D"
        batchnorm_class = "keras.layers.normalization.BatchNormalization"

    if (ws):
        if (symws==False and ircws==False):
            weightsum_init = "fanintimesfanout"
        elif (symws==True and ircws==True):
            weightsum_init = "fanintimesfanouttimesfour"
        elif (symws==True or ircws==True):
            weightsum_init = "fanintimesfanouttimestwo"

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
            "layers_config": conv_block+[
                {
                    "class": "keras.layers.convolutional.MaxPooling1D", 
                    "kwargs": {"pool_length": 40, "stride": stride}
                },
                ({
                    "class": "keras.layers.convolutional.WeightedSum1D",
                    "kwargs": {"symmetric": symws,
                               "input_is_revcomp_conv": ircws,
                               "init": weightsum_init,
                               "bias": False
                               }
                 }
                 if ws else 
                 {
                     "class": "keras.layers.core.Flatten", 
                     "kwargs": {}
                 }),
                {
                    "class": "keras.layers.core.Dense", 
                    "kwargs": {"output_dim": 1,
                               "trainable": (False if ws else True),
                               "init": ("one" if ws else "glorot_uniform")}
                },
                {
                    "class": "keras.layers.core.Activation", 
                    "kwargs": {"activation": "sigmoid"}
                }
            ],
            "optimizer_config": {
                "class": "keras.optimizers.Adam",
                "kwargs": {"lr": 0.001}
            },
            "loss": "binary_crossentropy" 
        } 
    }


def get_hyperparameter_configs(prefix, nlayers, stride,
                               nb_filter, revcomp,
                               ws,
                               symws,
                               ircws, seed, pos_weight,
                               train_file_prefix=""):
    message = (prefix
               +("-"+train_file_prefix if (len(train_file_prefix) > 0) else "")
               +" nlay-"+str(nlayers)
               +"_rc-"+('t' if revcomp else 'f')
               +"_nbf-"+str(nb_filter)
               +"_ws-"+('t' if ws else 'f')
               +("_symws-"+('t' if symws else 'f')
                 +"_ircws-"+('t' if ircws else 'f')
                 if ws else "")
               +"_str-"+str(stride)
               +" seed-"+str(seed))
    return {
        "message": message,
        "other_data_loaders": get_other_data_loaders(train_file_prefix=train_file_prefix),
        "model_creator": get_model_creator(nlayers=nlayers, stride=stride,
                            nb_filter=nb_filter,
                            revcomp=revcomp, ws=ws,
                            symws=symws,
                            ircws=ircws),
        "model_trainer": get_model_trainer(seed=seed, pos_weight=pos_weight)   
    }


def main(args):
    stride=20
    possible_settings = [
        #{"nlayers":3, "nb_filter": 16, "revcomp":False,
        # "ws":False, "symws":False, "ircws":False}, #norev
        #{"nb_filter": 16, "revcomp":True, "ws":True, "symws":False, "ircws":True}, #rev, irc
        #{"nb_filter": 32, "revcomp":False, "ws":False, "symws":False, "ircws":False}, #norev
        #{"nb_filter": 32, "revcomp":True, "ws":True, "symws":False, "ircws":True}, #rev, irc
        #{"nb_filter": 8, "revcomp":False, "ws":False, "symws":False, "ircws":False}, #norev
        #{"nb_filter": 8, "revcomp":True, "ws":True, "symws":False, "ircws":True}, #rev, irc
        #{"nb_filter": 16, "revcomp":False, "ws":False,
        # "symws":False, "ircws":False, "train_file_prefix":"10pc/"}, #norev
        #{"nb_filter": 16, "revcomp":True, "ws":True,
        # "symws":False, "ircws":True, "train_file_prefix":"10pc/"}, #rev, irc
        #150 width 41 in first layer is roughly the equivalent of 32,15-32,14-32,14; 32*(15*4 + 14*32 + 14*32 + 48)/(41*4 + 48) = 151.55
        #{"nlayers": 1, "nb_filter": 150, "revcomp":False, "ws":False, 
        # "symws":False, "ircws":False, "train_file_prefix": "10pc/"}, #norev
        #{"nlayers": 1, "nb_filter": 75, "revcomp":False, "ws":False, 
        # "symws":False, "ircws":False, "train_file_prefix": "10pc/"}, #norev
        #{"nlayers": 1,"nb_filter": 75, "revcomp":True, "ws":True, 
        # "symws":False, "ircws":True, "train_file_prefix":"10pc/"}, #rev, irc
        #36 width 21 in first two layers is roughly the equivalent of 32,15-32,14-32,14; ((21*4 + 48)x + 21*x^2) = 32*(15*4 + 14*32 + 14*32 + 48) <- put in wolfram alpha
        #{"nlayers": 2, "nb_filter": 36, "revcomp":False, "ws":False, 
        # "symws":False, "ircws":False, "train_file_prefix": "10pc/"}, #norev
        #{"nlayers": 2,"nb_filter": 18, "revcomp":True, "ws":True, 
        # "symws":False, "ircws":True, "train_file_prefix":"10pc/"}, #rev, irc
        #{"nlayers": 2,"nb_filter": 32, "revcomp":False, "ws":False,
        # "symws":False, "ircws":False, "train_file_prefix":"10pc/"}, #norev

        {"nlayers": 3,"nb_filter": 16, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"10pc/"}, #norev
        {"nlayers": 3,"nb_filter": 16, "revcomp":True, "ws":True,
         "symws":False, "ircws":True, "train_file_prefix":"10pc/"}, #rev, irc
        {"nlayers": 3,"nb_filter": 32, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"10pc/"}, #norev

        {"nlayers": 3,"nb_filter": 16, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"20pc/"}, #norev
        {"nlayers": 3,"nb_filter": 16, "revcomp":True, "ws":True,
         "symws":False, "ircws":True, "train_file_prefix":"20pc/"}, #rev, irc
        {"nlayers": 3,"nb_filter": 32, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"20pc/"}, #norev

        {"nlayers": 3,"nb_filter": 16, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"40pc/"}, #norev
        {"nlayers": 3,"nb_filter": 16, "revcomp":True, "ws":True,
         "symws":False, "ircws":True, "train_file_prefix":"40pc/"}, #rev, irc
        {"nlayers": 3,"nb_filter": 32, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"40pc/"}, #norev

        {"nlayers": 3,"nb_filter": 16, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"60pc/"}, #norev
        {"nlayers": 3,"nb_filter": 16, "revcomp":True, "ws":True,
         "symws":False, "ircws":True, "train_file_prefix":"60pc/"}, #rev, irc
        {"nlayers": 3,"nb_filter": 32, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"60pc/"}, #norev

        {"nlayers": 3,"nb_filter": 16, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"80pc/"}, #norev
        {"nlayers": 3,"nb_filter": 16, "revcomp":True, "ws":True,
         "symws":False, "ircws":True, "train_file_prefix":"80pc/"}, #rev, irc
        {"nlayers": 3,"nb_filter": 32, "revcomp":False, "ws":False,
         "symws":False, "ircws":False, "train_file_prefix":"80pc/"}, #norev

        # "symws":False, "ircws":False, "train_file_prefix":"80pc/"}, #norev
        #{"nlayers": 1, "nb_filter": 150, "revcomp":False, "ws":False, 
        # "symws":False, "ircws":False, "train_file_prefix": "10pc/"}, #norev

        #{"nlayers": 1, "nb_filter": 25, "revcomp":False, "ws":False, 
        # "symws":False, "ircws":False, "train_file_prefix": "10pc/"}, #norev
        #{"nlayers": 1, "nb_filter": 25, "revcomp":True, "ws":True, 
        # "symws":False, "ircws":True, "train_file_prefix": "10pc/"}, #rev
        #{"nlayers": 1, "nb_filter": 50, "revcomp":False, "ws":False, 
        # "symws":False, "ircws":False, "train_file_prefix": "10pc/"}, #norev
        #{"nlayers": 1, "nb_filter": 50, "revcomp":True, "ws":True, 
        # "symws":False, "ircws":True, "train_file_prefix": "10pc/"}, #rev
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
