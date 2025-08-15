import cProfile
import pstats  # To process and display the results
import time
import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from GameImplementation import game_play
from Agent.train_through_self_play import SelfPlayAndTrainingOrchestrator
from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
from config import getSelfPlayFullConfig
from Experiments import model_checks


def cleanUp():
    cleanup_dir = os.path.join("ModelCheckpoints", "debug_model")

    for filename in os.listdir(cleanup_dir):
        file_path = os.path.join(cleanup_dir, filename)
        if os.path.isfile(file_path):  # Check if it's a file (not a subdirectory)
            os.remove(file_path)
            print(f"File '{file_path}' deleted successfully.")


def runExperiment():
    self_play_config = getSelfPlayFullConfig()
    spto = SelfPlayAndTrainingOrchestrator(self_play_config)

    # Profile the main function
    # profiler = cProfile.Profile()
    # profiler.enable()
    spto.overallPipeline()
    # profiler.disable()


def checkModel(model_weights_source):
    model_checks.main(model_weights_source)


if __name__ == "__main__":
    # cleanUp()
    runExperiment()

    # model_weights_source = "ModelCheckpoints/debug_model/iteration_90.pth"
    # checkModel(model_weights_source)


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
