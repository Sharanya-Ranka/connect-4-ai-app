import torch
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import reduce
import cProfile
import pstats  # To process and display the results


import numpy as np

from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
from Agent.policy_and_value_model import loadModel, saveModel, createNewModel
from Agent.policy_and_value_model import PolicyAndValueTrainer

from GameImplementation.game_state import GameState
from config import debugObj


class SelfPlayOrchestrator:
    def __init__(self, config):
        self.config = config
        self.sp_config = config["SELF_PLAY_CONFIG"]

        self.initializeAgent()

    def initializeAgent(self):
        # Config should consist of atleast the model config and the agent config
        self.agent = DeepNNAndMCTSAgent(self.config)
        # Required to prevent different agents from performing the exact same set of simulations
        seed = os.getpid()
        np.random.seed(seed)

    def selfPlayPipeline(self):
        # print(f"Started pipeline")
        all_games_data = []
        for game_num in range(self.sp_config["NUM_GAMES"]):
            all_games_data.append(self.playAGame())
            # if game_num % 20 == 0:
            #     print(f"Completed game {game_num}")
            #     print(f"Agent cache size={len(self.agent.state_cache)}")
            # print(f"{all_games_data[-1][-1][0]}")
            # breakpoint()
            # profiler = cProfile.Profile()
            # profiler.enable()
            # all_games_data.append(self.playAGame())
            # profiler.disable()
            # print(f"Completed game {game_num}")
            # # Print the statistics
            # stats = pstats.Stats(profiler).sort_stats("tottime")  # Sort by cumulative time
            # stats.print_stats(50)  # Print top 50 functions

        return all_games_data

    def playAGame(self):
        state = GameState()
        current_game_data = []
        current_ply = 0
        while not state.isTerminal():
            # print(f"This state=\n{state}")
            action_info = self.agent.getActionWithInfo(state)
            # print(f"Got action info")
            current_game_data.append([state, 1, action_info["empirical_action_probs"]])

            action = self.chooseTemperatureBasedAction(
                action_info["empirical_action_probs"], ply=current_ply
            )
            state = state.applyMove(action)
            current_ply += 1

        # current_game_data.append([state, -1, action_info["empirical_action_probs"]])
        # breakpoint()

        gamma = 1

        for i in range(len(current_game_data)):
            inter_state = current_game_data[i][0]

            state_value = (
                0
                if state.getWinner() == GameState.NOONE
                else -1 if inter_state.next_player == state.getWinner() else 1
            ) * np.power(gamma, len(current_game_data) - (i + 1))

            current_game_data[i][1] = state_value

            # if debugObj.iteration == 0 and i == 0:
            #     print(f"First state={inter_state}\n{state_value}")

        # breakpoint()

        return current_game_data

    def chooseTemperatureBasedAction(self, empirical_action_probs, ply=0):
        # Empirical action probs are of the form N_i/sum_j N_j
        # Temperature based is N_i^(1/t) / sum_j N_j^(1/t)
        acting_temperature = (
            self.sp_config["FINAL_TEMPERATURE"]
            if ply >= self.sp_config["TRIGGER_PLY"]
            else self.sp_config["INITIAL_TEMPERATURE"]
        )
        # print(f"Temp for ply={ply} = {acting_temperature}")

        max_prob = np.max(empirical_action_probs)
        temperature_based_units = np.power(
            empirical_action_probs / max_prob, 1 / acting_temperature
        )
        temperature_based_probs = temperature_based_units / np.sum(
            temperature_based_units
        )

        action = np.random.choice(self.sp_config["NUM_COLS"], p=temperature_based_probs)

        return action


def selfPlayRunnerFunction(config):
    sp = SelfPlayOrchestrator(config=config)
    return sp.selfPlayPipeline()


class TrainingOrchestrator:
    def __init__(self, config):
        self.config = config
        self.model_config = config["MODEL_CONFIG"]

    def trainingPipeline(self):
        model = loadModel(self.model_config)
        tr = PolicyAndValueTrainer(self.config)
        tr.runTrainPipeline(model, self.config["DATA"])
        saveModel(
            dict(
                MODEL=model,
                SAVE_PATH=self.config["MODEL_SAVE_FULLPATH"],
            )
        )

    def setUp(self):
        model = createNewModel(self.model_config)
        saveModel(
            dict(
                MODEL=model,
                SAVE_PATH=self.config["MODEL_SAVE_FULLPATH"],
            )
        )


class SelfPlayAndTrainingOrchestrator:
    def __init__(self, config):
        self.config = config
        self.sp_config = config["SELF_PLAY_CONFIG"]
        self.tr_config = config["TRAINING_CONFIG"]
        self.model_config = config["MODEL_CONFIG"]
        self.agent_config = config["AGENT_CONFIG"]

        self.game_data_store = []

    def overallPipeline(self):
        start_iteration = self.sp_config.get("START_FROM_ITERATION", 1)
        end_iteration = self.sp_config["NUM_ITERATIONS"]
        for iteration in range(start_iteration, end_iteration + 1):
            if iteration == 1:
                self.setUp()

            self.performIteration(iteration=iteration)
            debugObj.updateIteration()

    def setUp(self):
        setup_config = self.getIterationTrainingConfig(iteration=0, game_data=None)
        tr = TrainingOrchestrator(config=setup_config)
        tr.setUp()

    def getModelPathForIteration(self, iteration=0):
        return os.path.join(self.tr_config["BASE_PATH"], f"iteration_{iteration}.pth")

    # def getTemperatureForIteration(self, iteration=0):
    #     initial_temp = self.sp_config["INITIAL_TEMPERATURE"]
    #     temp_factor = self.sp_config["TEMPERATURE_DELTA_FACTOR"]
    #     min_temp = self.sp_config["MIN_TEMPERATURE"]
    #     eff_iteration = iteration % self.sp_config["TEMPERATURE_RESET_ITERATION"]

    #     return max(min_temp, np.power(temp_factor, eff_iteration - 1) * initial_temp)

    def getIterationSelfPlayConfig(self, iteration=0):
        model_config = self.model_config.copy()
        model_config["MODEL_WEIGHTS_SOURCE"] = self.getModelPathForIteration(
            iteration - 1
        )

        self_play_config = dict(
            AGENT_CONFIG=self.agent_config,
            MODEL_CONFIG=model_config,
            SELF_PLAY_CONFIG=dict(
                NUM_COLS=self.sp_config["NUM_COLS"],
                INITIAL_TEMPERATURE=self.sp_config["INITIAL_TEMPERATURE"],
                TRIGGER_PLY=self.sp_config["TRIGGER_PLY"],
                FINAL_TEMPERATURE=self.sp_config["FINAL_TEMPERATURE"],
            ),
        )

        if self.sp_config.get("USE_MULTIPROCESSING", False) == False:
            self_play_config["SELF_PLAY_CONFIG"]["NUM_GAMES"] = self.sp_config[
                "GAMES_PER_ITERATION"
            ]

        else:
            max_workers = self.sp_config["N_MULTIPROCESS_GAME_RUNNERS"]
            self_play_config["SELF_PLAY_CONFIG"]["NUM_GAMES"] = int(
                self.sp_config["GAMES_PER_ITERATION"] / max_workers
            )

        return self_play_config

    def selectRandomStates(self, game_states, num_samples):
        sample = np.random.choice(
            len(game_states), size=min(num_samples, len(game_states)), replace=False
        )

        return list(game_states[ind] for ind in sample)

    def updateGameDataStore(self, cur_iter_game_data):
        num_samples_per_game = self.sp_config.get("NUM_DATAPOINTS_PER_GAME", 5)
        cur_iter_game_samples = [
            self.selectRandomStates(single_game_data, num_samples_per_game)
            for single_game_data in cur_iter_game_data
        ]

        self.game_data_store += cur_iter_game_samples
        max_datapoints = (
            self.sp_config["GAMES_PER_ITERATION"]
            * self.sp_config["NUM_LEGACY_ITERATIONS_DATA"]
        )
        self.game_data_store = self.game_data_store[-max_datapoints:]

    def getIterationTrainingConfig(self, iteration=0, game_data=None):
        model_config = self.model_config.copy()
        model_config["MODEL_WEIGHTS_SOURCE"] = (
            None if iteration < 1 else self.getModelPathForIteration(iteration - 1)
        )

        flattened_game_data = (
            None if game_data is None else reduce(lambda x, y: x + y, game_data, [])
        )

        if (
            iteration > 0
            and iteration % self.tr_config["DECREASE_LR_EVERY_K_ITERATIONS"] == 0
        ):
            new_lr = self.tr_config["LEARNING_RATE"] / 5
            self.tr_config["LEARNING_RATE"] = new_lr
            print(f"Decreasing lr={new_lr} at iteration={iteration}")

        tr_config = dict(
            DATA=flattened_game_data,
            MODEL_CONFIG=model_config,
            TRAINING_CONFIG=self.tr_config,
            MODEL_SAVE_FULLPATH=self.getModelPathForIteration(iteration),
        )
        return tr_config

    def performIteration(self, iteration=0):
        self_play_config = self.getIterationSelfPlayConfig(iteration=iteration)

        if self.sp_config.get("USE_MULTIPROCESSING", False) == False:
            # No multiprocessing
            sp = SelfPlayOrchestrator(config=self_play_config)
            # breakpoint()
            all_game_data = sp.selfPlayPipeline()
        else:
            # Use multiprocessing
            max_workers = self.sp_config["N_MULTIPROCESS_GAME_RUNNERS"]
            all_game_data = []
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(selfPlayRunnerFunction, self_play_config)
                    for worker in range(max_workers)
                }

                for future in as_completed(futures):
                    process_game_data = future.result()
                    all_game_data.extend(process_game_data)

        # print(f"Iteration {debugObj.iteration} : Average plys {np.mean(plys_in_games)}")

        self.updateGameDataStore(all_game_data)

        train_config = self.getIterationTrainingConfig(
            iteration, game_data=self.game_data_store
        )
        # breakpoint()
        tr = TrainingOrchestrator(config=train_config)
        training_results = tr.trainingPipeline()
        self.processTrainingResults(training_results)

    def processTrainingResults(self, training_results):
        pass
