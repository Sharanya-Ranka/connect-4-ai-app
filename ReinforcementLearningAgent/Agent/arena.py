import torch
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import reduce
import itertools
import copy


import numpy as np
import re

from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
from Experiments.test_players import UniformPriorMCTSAgent, RandomAgent

from GameImplementation.game_state import GameState
from utilities import PositionProvider


class PlayOffOrchestrator:
    def __init__(self, config):
        self.config = config
        self.initializeAgents()

    def _agentFactory(self, agent_config):
        # breakpoint()
        if agent_config["AGENT_TYPE"] == "DEEPNN_AND_MCTS_AGENT":
            return DeepNNAndMCTSAgent(agent_config)
        elif agent_config["AGENT_TYPE"] == "UNIFORM_PRIOR_MCTS_AGENT":
            return UniformPriorMCTSAgent(agent_config)
        elif agent_config["AGENT_TYPE"] == "RANDOM_AGENT":
            return RandomAgent(agent_config)

    def initializeAgents(self):
        # Config should consist of atleast the model config and the agent config
        self.player1 = self._agentFactory(self.config["PLAYER1"])
        self.player2 = self._agentFactory(self.config["PLAYER2"])
        # breakpoint()

    def printGame(self, game_progression, player1_id, player2_id, player_won):
        win_player_id = player1_id if player_won == GameState.RED else player2_id
        win_player_colour = "RED" if player_won == GameState.RED else "YELLOW"
        print(f"New game: {player1_id} vs {player2_id}")
        print(f"{win_player_id} ({win_player_colour}) Wins")
        for state, action_info in game_progression:
            print(state)
            action_probs = " ".join(
                map(lambda x: f"{x:.2f}", action_info["empirical_action_probs"])
            )
            print(action_probs)

        print(f"Game ends\n")

    def playOffPipeline(self):
        player1_wins = 0
        player2_wins = 0
        draws = 0
        player1_wins_printed = 0
        player2_wins_printed = 0
        WINS_TO_PRINT = 1
        print_games = self.config.get("PRINT_GAMES", False)

        # breakpoint()

        player1_id = self.config["PLAYER1"]["NAME"]
        player2_id = self.config["PLAYER2"]["NAME"]

        # player1_id = re.search(r"(iteration_\d+)\.pth", player1_id).group(1)
        # player2_id = re.search(r"(iteration_\d+)\.pth", player2_id).group(1)

        for position_num, position in enumerate(self.config["POSITIONS"]):
            # To properly test the agents let both of them play from player1's perspective
            winner_gm1, gm1_prog = self.playAGameFromPosition(
                position, self.player1, self.player2
            )
            winner_gm2, gm2_prog = self.playAGameFromPosition(
                position, self.player2, self.player1
            )

            if winner_gm1 == GameState.RED:
                player1_wins += 1
                if print_games and player1_wins_printed < WINS_TO_PRINT:
                    player1_wins_printed += 1
                    self.printGame(gm1_prog, player1_id, player2_id, GameState.RED)
            elif winner_gm1 == GameState.YELLOW:
                player2_wins += 1
                if print_games and player2_wins_printed < WINS_TO_PRINT:
                    player2_wins_printed += 1
                    self.printGame(gm1_prog, player1_id, player2_id, GameState.YELLOW)
            else:
                draws += 1

            if winner_gm2 == GameState.RED:
                player2_wins += 1
                if print_games and player2_wins_printed < WINS_TO_PRINT:
                    player2_wins_printed += 1
                    self.printGame(gm2_prog, player2_id, player1_id, GameState.RED)
            elif winner_gm2 == GameState.YELLOW:
                player1_wins += 1
                if print_games and player1_wins_printed < WINS_TO_PRINT:
                    player1_wins_printed += 1
                    self.printGame(gm2_prog, player2_id, player1_id, GameState.YELLOW)
            else:
                draws += 1

        return (player1_wins, draws, player2_wins)

    def playAGameFromPosition(self, position, player1, player2):
        state: GameState = position
        game_progression = []

        while not state.isTerminal():
            if state.next_player == 1:
                action_info = player1.getActionWithInfo(state)
            else:
                action_info = player2.getActionWithInfo(state)

            action_mask = np.array(state.possible_moves_mask, dtype=np.bool)
            action = self.chooseBestAction(
                action_info["empirical_action_probs"], action_mask
            )
            game_progression.append((state, action_info))
            # breakpoint()
            state = state.applyMove(action)

        return state.getWinner(), game_progression

    def chooseBestAction(self, empirical_action_probs, action_mask):
        empirical_action_probs[~action_mask] = -float("inf")
        best_action = np.argmax(empirical_action_probs)

        return best_action


def playOffRunnerFunction(config):
    sp = PlayOffOrchestrator(config=config)
    return sp.playOffPipeline()


class ArenaOrchestrator:
    def __init__(self, config):
        self.config = config

    def overallPipeline(self):
        assert (
            self.config["NUM_GAMES"] % 2 == 0
        ), "Num games must be even (we use 1/2 positions with 2 games per position, with players swapped)"
        positions = PositionProvider.generateStartingPositions(
            self.config["BEGIN_POSITION_DEPTH"], self.config["NUM_GAMES"] // 2
        )

        player1_configs = self._getPlayerConfigs(
            self.config["PLAYER1_BASE_CONFIG"], self.config["PLAYER1_VARIANTS"]
        )
        player2_configs = self._getPlayerConfigs(
            self.config["PLAYER2_BASE_CONFIG"], self.config["PLAYER2_VARIANTS"]
        )
        # breakpoint()

        pairings = itertools.product(player1_configs, player2_configs)

        for pl1, pl2 in pairings:
            playoff_data = self.playOff(pl1, pl2, positions)
            print(f"Playoff player {pl1['NAME']} vs player {pl2['NAME']}")
            print(f"Num games={self.config['NUM_GAMES']} WinStats={playoff_data}")

    def _getPlayerConfigs(self, base_config, variants):
        all_configs = []

        if not variants:
            all_configs.append(copy.deepcopy(base_config))
            return all_configs

        for iteration_variant in variants["ITERATIONS"]:
            config = copy.deepcopy(base_config)
            config["MODEL_CONFIG"]["MODEL_WEIGHTS_SOURCE"] = (
                self.getModelPathForIteration(
                    base_config["BASE_PATH"], iteration_variant
                )
            )
            config["NAME"] = config["NAME"] + f"_iteration{iteration_variant}"

            all_configs.append(config)

        return all_configs

    def getPlayOffConfig(self, player1_config, player2_config):
        playoff_config = dict(
            PRINT_GAMES=self.config["PRINT_GAMES"],
            PLAYER1=player1_config,
            PLAYER2=player2_config,
        )

        return playoff_config

    def getModelPathForIteration(self, base_path, iteration=0):
        return os.path.join(base_path, f"iteration_{iteration}.pth")

    # def playOffMultiProcess(self, pairings, positions):
    #     playoff_configs = [self.getPlayOffConfig(p1_cfg, p2_cfg) for p1_cfg, p2_cfg in pairings]
    #     all_playoff_data = [0, 0, 0]

    #     max_workers = self.config["N_MULTIPROCESS_GAME_RUNNERS"]

    #     with ProcessPoolExecutor(max_workers=max_workers) as executor:
    #         futures = set()
    #         positions_per_worker = int(np.ceil(len(positions) / max_workers))
    #         for worker_ind in range(max_workers):
    #             cur_playoff_config = playoff_config.copy()
    #             start_pos = worker_ind * positions_per_worker
    #             end_pos = start_pos + positions_per_worker
    #             # print(start_pos, end_pos)
    #             cur_playoff_config["POSITIONS"] = positions[start_pos:end_pos]
    #             futures.add(
    #                 executor.submit(playOffRunnerFunction, cur_playoff_config)
    #             )

    #         for future in as_completed(futures):
    #             process_playoff_data = future.result()
    #             all_playoff_data[0] += process_playoff_data[0]
    #             all_playoff_data[1] += process_playoff_data[1]
    #             all_playoff_data[2] += process_playoff_data[2]

    #     return all_playoff_data

    def playOff(self, player1_config, player2_config, positions):
        playoff_config = self.getPlayOffConfig(player1_config, player2_config)
        all_playoff_data = [0, 0, 0]
        if self.config.get("USE_MULTIPROCESSING", False) == False:
            playoff_config["POSITIONS"] = positions
            # No multiprocessing
            sp = PlayOffOrchestrator(config=playoff_config)
            # breakpoint()
            process_playoff_data = sp.playOffPipeline()
            all_playoff_data[0] += process_playoff_data[0]
            all_playoff_data[1] += process_playoff_data[1]
            all_playoff_data[2] += process_playoff_data[2]
        else:
            # Use multiprocessing
            max_workers = self.config["N_MULTIPROCESS_GAME_RUNNERS"]
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                future_to_pos = {}
                # breakpoint()
                for pos in positions:
                    cur_playoff_config = playoff_config.copy()
                    cur_playoff_config["POSITIONS"] = [pos]  # Send single position

                    future = executor.submit(playOffRunnerFunction, cur_playoff_config)
                    future_to_pos[future] = pos

                # 2. Hand over results to downstream aggregation immediately as each finishes
                for future in as_completed(future_to_pos):
                    print(f"Completed a future")
                    process_playoff_data = future.result()

                    # Immediate processing/handover
                    all_playoff_data[0] += process_playoff_data[0]
                    all_playoff_data[1] += process_playoff_data[1]
                    all_playoff_data[2] += process_playoff_data[2]

        return all_playoff_data
