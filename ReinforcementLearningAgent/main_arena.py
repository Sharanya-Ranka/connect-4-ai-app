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

    model_config = SAVE_CONFIG["MODEL_CONFIG"]
    model = loadModel(model_config)
    dummy_input = preprocessState(GameState()).unsqueeze(dim=0)
    print(f"Dummy input shape={dummy_input.shape}")

    ModelSaver.saveONNXModel(model, dummy_input, SAVE_CONFIG["SAVE_FILEPATH"])


if __name__ == "__main__":
    print(f"Running Arena Pipeline")
    runArenaPipeline()
