import cProfile
import pstats  # To process and display the results
import time
import os
import torch.multiprocessing as mp

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

mp.set_start_method("spawn", force=True)

from GameImplementation import game_play
from Agent.train_through_self_play import SelfPlayAndTrainingOrchestrator
from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
from config import (
    PIPELINE,
    MODEL_VERIFICATION_PIPELINE,
    SELF_PLAY_AND_TRAINING_PIPELINE,
    ARENA_PIPELINE,
ONNX_SAVE_PIPELINE,
)
from config import getSelfPlayFullConfig


def cleanUp():
    cleanup_dir = os.path.join("ModelCheckpoints", "debug_model")

    for filename in os.listdir(cleanup_dir):
        file_path = os.path.join(cleanup_dir, filename)
        if os.path.isfile(file_path):  # Check if it's a file (not a subdirectory)
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")


def runSelfPlayAndTrainingPipeline():
    self_play_config = getSelfPlayFullConfig()
    spto = SelfPlayAndTrainingOrchestrator(self_play_config)

    # Profile the main function
    # profiler = cProfile.Profile()
    # profiler.enable()
    spto.overallPipeline()
    # profiler.disable()


def runModelVerificationPipeline():
    from Experiments import model_checks
    from config import TEST_CONFIG

    mt = model_checks.ModelTesting(TEST_CONFIG)
    mt.performTest()


def runArenaPipeline():
    from Agent import arena
    from config import ARENA_CONFIG

    arena_runner = arena.ArenaOrchestrator(ARENA_CONFIG)
    arena_runner.overallPipeline()

def runONNXModelSavePipeline():
    from config import SAVE_CONFIG
    from utilities import ModelSaver
    from GameImplementation.game_state import GameState
    from Agent.policy_and_value_model import loadModel, preprocessState

    model_config = SAVE_CONFIG['MODEL_CONFIG']
    model = loadModel(model_config)
    dummy_input = preprocessState(GameState()).unsqueeze(dim=0)
    print(f"Dummy input shape={dummy_input.shape}")
    
    ModelSaver.saveONNXModel(model, dummy_input, SAVE_CONFIG['SAVE_FILEPATH'])
    
    


if __name__ == "__main__":
    if PIPELINE == SELF_PLAY_AND_TRAINING_PIPELINE:
        print(f"Running Self Play and Training Pipeline")
        runSelfPlayAndTrainingPipeline()
    elif PIPELINE == MODEL_VERIFICATION_PIPELINE:
        print(f"Running Model Verification Pipeline")
        runModelVerificationPipeline()
    elif PIPELINE == ARENA_PIPELINE:
        print(f"Running Arena Pipeline")
        runArenaPipeline()
    elif PIPELINE == ONNX_SAVE_PIPELINE:
        print(f"Running ONNX Model Save Pipeline")
        runONNXModelSavePipeline()
    else:
        print(f"No valid pipeline selected. Exiting")


# Print the statistics
# stats = pstats.Stats(profiler).sort_stats("tottime")  # Sort by cumulative time
# stats.print_stats(50)  # Print top 50 functions

# from GameImplementation import game_play
# from Agent.train_through_self_play import SelfPlayTrainingOrchestrator
# from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
# from config import getSelfPlayConfig

# self_play_config = getSelfPlayConfig()
# spto = SelfPlayTrainingOrchestrator(self_play_config)
# spto.selfPlayTrainingPipeline()
