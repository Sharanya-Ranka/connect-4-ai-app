import cProfile
import pstats  # To process and display the results
import time

from GameImplementation import game_play
from Agent.train_through_self_play import SelfPlayTrainingOrchestrator
from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
from config import getSelfPlayConfig

self_play_config = getSelfPlayConfig()
spto = SelfPlayTrainingOrchestrator(self_play_config)


# Profile the main function
# profiler = cProfile.Profile()
# profiler.enable()
spto.selfPlayTrainingPipeline()
# profiler.disable()

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
