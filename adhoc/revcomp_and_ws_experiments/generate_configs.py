import avutils.util as util
import avutils.file_processing as fp

other_data_loaders = {
    "train": {
        "class": "hdf5_data_loader.MultimodalBatchDataLoader",
        "kwargs": {
            "batch_size": 100,
            "path_to_hdf5": "train_data.hdf5",
            "num_to_load_for_eval": 1000,
            "bundle_x_and_y_in_generator": False,
            "strip_enclosing_dictionary": True
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
                   "max_epochs": 80, 
                   "epochs_to_wait": 80,
                   "running_mean_over_epochs": 1
                } 
            },
            "class_weight": {"0":1, "1":5}
        }
    }

def get_model_creator(stride, nb_filter, revcomp,
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

    return {
        "class": "flexible_keras.FlexibleKerasSequential",
        "kwargs": {
            "layers_config": [
                {
                    "class": conv_class, 
                    "kwargs": {
                        "input_shape": [1000,4],
                        "nb_filter": nb_filter,
                        "filter_length": 15,
                    }
                },
                {
                    "class": batchnorm_class,
                    "kwargs": {}
                },
                {
                    "class": "keras.layers.core.Activation", 
                    "kwargs": {"activation": "relu"}
                },
                {
                    "class": conv_class, 
                    "kwargs": {
                        "nb_filter": nb_filter,
                        "filter_length": 14,
                    }
                },
                {
                    "class": batchnorm_class,
                    "kwargs": {}
                },
                {
                    "class": "keras.layers.core.Activation", 
                    "kwargs": {"activation": "relu"}
                },
                {
                    "class": conv_class, 
                    "kwargs": {"nb_filter": nb_filter,
                               "filter_length": 14,
                              }
                },
                {
                    "class": batchnorm_class,
                    "kwargs": {}
                },
                {
                    "class": "keras.layers.core.Activation", 
                    "kwargs": {"activation": "relu"}
                },
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

def get_hyperparameter_configs(prefix, stride,
                               nb_filter, revcomp,
                               ws,
                               symws,
                               ircws, seed):
    message = (prefix
               +" rc-"+('t' if revcomp else 'f')
               +"_nbf-"+str(nb_filter)
               +"_ws-"+('t' if ws else 'f')
               +("_symws-"+('t' if symws else 'f')
                 +"_ircws-"+('t' if ircws else 'f')
                 if ws else "")
               +"_str-"+str(stride)
               +" seed-"+str(seed))
    return {
        "message": message,
        "other_data_loaders": other_data_loaders,
        "model_creator": get_model_creator(stride=stride,
                            nb_filter=nb_filter,
                            revcomp=revcomp, ws=ws,
                            symws=symws,
                            ircws=ircws),
        "model_trainer": get_model_trainer(seed=seed)   
    }

def main(args):
    stride=20
    possible_settings = [
        {"nb_filter": 16, "revcomp":False, "ws":False, "symws":False, "ircws":False}, #norev
        {"nb_filter": 16, "revcomp":False, "ws":True, "symws":True, "ircws":False}, #norev, sym
        {"nb_filter": 16, "revcomp":True, "ws":True, "symws":False, "ircws":True}, #rev, irc
        {"nb_filter": 16, "revcomp":True, "ws":True, "symws":True, "ircws":True}, #rev, sym, irc
        {"nb_filter": 32, "revcomp":False, "ws":False, "symws":False, "ircws":False}, #norev
        {"nb_filter": 32, "revcomp":True, "ws":True, "symws":False, "ircws":True}, #rev, irc
        {"nb_filter": 8, "revcomp":False, "ws":False, "symws":False, "ircws":False}, #norev
        {"nb_filter": 8, "revcomp":True, "ws":True, "symws":False, "ircws":True}, #rev, irc
    ]
    hyperparameter_configs_0to4 = []
    hyperparameter_configs_5to9 = []
    for seed in range(0,5):
        for settings in possible_settings: 
            hyperparameter_configs_0to4.append(
                get_hyperparameter_configs(prefix=args.prefix,
                 stride=stride, seed=seed, **settings))
            hyperparameter_configs_5to9.append(
                get_hyperparameter_configs(prefix=args.prefix,
                 stride=stride, seed=seed+5, **settings))
            
    fp.write_to_file("seed0-4_hyperparameter_configs.yaml",
                     util.format_as_json(hyperparameter_configs_0to4))
    fp.write_to_file("seed5-9_hyperparameter_configs.yaml",
                     util.format_as_json(hyperparameter_configs_5to9))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prefix")
    main(parser.parse_args())
