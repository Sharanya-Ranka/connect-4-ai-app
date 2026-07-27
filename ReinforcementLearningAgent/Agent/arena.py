import torch
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import reduce
import itertools


import numpy as np

from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent

from GameImplementation.game_state import GameState
from utilities import PositionProvider


class PlayOffOrchestrator:
    def __init__(self, config):
        self.config = config
        self.initializeAgents()

    def initializeAgents(self):
        # Config should consist of atleast the model config and the agent config
        self.player1 = DeepNNAndMCTSAgent(self.config["PLAYER1"])
        self.player2 = DeepNNAndMCTSAgent(self.config["PLAYER2"])

    def playOffPipeline(self):
        player1_score = 0
        player2_score = 0

        for position_num, position in enumerate(self.config["POSITIONS"]):
            # To properly test the agents let both of them play from player1's perspective
            winner_gm1 = self.playAGameFromPosition(
                position, self.player1, self.player2
            )
            winner_gm2 = self.playAGameFromPosition(
                position, self.player2, self.player1
            )

            if winner_gm1 == GameState.RED:
                player1_score += 1
            elif winner_gm1 == GameState.YELLOW:
                player2_score += 1
            else:
                player1_score += 0.5
                player2_score += 0.5

            if winner_gm2 == GameState.RED:
                player2_score += 1
            elif winner_gm2 == GameState.YELLOW:
                player1_score += 1
            else:
                player1_score += 0.5
                player2_score += 0.5

        return (player1_score, player2_score)

    def playAGameFromPosition(self, position, player1, player2):
        state: GameState = position

        while not state.isTerminal():
            if state.next_player == 1:
                action_info = player1.getActionWithInfo(state)
            else:
                action_info = player2.getActionWithInfo(state)

            action = self.chooseBestAction(action_info["empirical_action_probs"])
            state = state.applyMove(action)

        return state.getWinner()

    def chooseBestAction(self, empirical_action_probs):
        best_action = np.argmax(empirical_action_probs)

        return best_action


def playOffRunnerFunction(config):
    sp = PlayOffOrchestrator(config=config)
    return sp.playOffPipeline()


class ArenaOrchestrator:
    def __init__(self, config):
        self.config = config
        self.model_config = config["MODEL_CONFIG"]
        self.agent_config = config["AGENT_CONFIG"]

    def overallPipeline(self):
        positions = PositionProvider.generateStartingPositions(
            self.config["BEGIN_POSITION_DEPTH"], self.config["NUM_GAMES"] // 2
        )

        player_model_iterations = self.config["ITERATIONS_COMPARE"]
        pairings_iterations = list(
            itertools.product(player_model_iterations[:2], player_model_iterations[2:])
        )
        # Successive pairing (k with k+2)
        # list(
        #     zip(player_model_iterations[:-2], player_model_iterations[2:])
        # )

        # All combinations
        # itertools.combinations(
        #     self.config["ITERATIONS_COMPARE"], 2
        # )

        for pl1, pl2 in pairings_iterations:
            playoff_data = self.playOff(pl1, pl2, positions)
            print(f"Playoff player {pl1} vs player {pl2}")
            print(f"Num games={self.config['NUM_GAMES']} WinStats={playoff_data}")

    def getPlayOffConfig(self, player1_iter, player2_iter):
        pl1_model_config = self.model_config.copy()
        pl1_model_config["MODEL_WEIGHTS_SOURCE"] = self.getModelPathForIteration(
            player1_iter
        )

        pl2_model_config = self.model_config.copy()
        pl2_model_config["MODEL_WEIGHTS_SOURCE"] = self.getModelPathForIteration(
            player2_iter
        )

        playoff_config = dict(
            PLAYER1=dict(
                AGENT_CONFIG=self.agent_config.copy(),
                MODEL_CONFIG=pl1_model_config,
            ),
            PLAYER2=dict(
                AGENT_CONFIG=self.agent_config.copy(),
                MODEL_CONFIG=pl2_model_config,
            ),
        )

        return playoff_config

    def getModelPathForIteration(self, iteration=0):
        return os.path.join(self.config["BASE_PATH"], f"iteration_{iteration}.pth")

    def playOff(self, player1_iter, player2_iter, positions):
        playoff_config = self.getPlayOffConfig(player1_iter, player2_iter)
        all_playoff_data = [0, 0]
        if self.config.get("USE_MULTIPROCESSING", False) == False:
            playoff_config["POSITIONS"] = positions
            # No multiprocessing
            sp = PlayOffOrchestrator(config=playoff_config)
            # breakpoint()
            process_playoff_data = sp.playOffPipeline()
            all_playoff_data[0] += process_playoff_data[0]
            all_playoff_data[1] += process_playoff_data[1]
        else:
            # Use multiprocessing
            max_workers = self.config["N_MULTIPROCESS_GAME_RUNNERS"]

            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = set()
                positions_per_worker = int(np.ceil(len(positions) / max_workers))
                for worker_ind in range(max_workers):
                    cur_playoff_config = playoff_config.copy()
                    start_pos = worker_ind * positions_per_worker
                    end_pos = start_pos + positions_per_worker
                    # print(start_pos, end_pos)
                    cur_playoff_config["POSITIONS"] = positions[start_pos:end_pos]
                    futures.add(
                        executor.submit(playOffRunnerFunction, cur_playoff_config)
                    )

                for future in as_completed(futures):
                    process_playoff_data = future.result()
                    all_playoff_data[0] += process_playoff_data[0]
                    all_playoff_data[1] += process_playoff_data[1]

        return all_playoff_data
