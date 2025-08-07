import numpy as np

from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
from GameImplementation.game_state import GameState
from config import debugObj


class SelfPlayOrchestrator:
    def __init__(self, config):
        self.config = config

    def initializeAgent(self):
        self.agent = DeepNNAndMCTSAgent(self.config)

    def selfPlayPipeline(self):
        all_games_data = []
        for game_num in range(self.config["NUM_GAMES"]):
            all_games_data.append(self.playAGame())

        return all_games_data

    def playAGame(self):
        state = GameState()
        current_game_data = []
        while not state.isTerminal():
            action_info = self.agent.getActionWithInfo(state)
            current_game_data.append([state, -1, action_info["empirical_action_probs"]])

            action = action_info["action"]
            state = state.applyMove(action)

        for i in range(len(current_game_data)):
            inter_state = current_game_data[i]

            state_value = (
                0
                if state.getWinner() == GameState.NOONE
                else -1 if inter_state.next_player == state.getWinner() else 1
            )

            current_game_data[i][1] = state_value

            # if debugObj.iteration == 0 and i == 0:
            #     print(f"First state={inter_state}\n{state_value}")

        return current_game_data


class TrainingOrchestrator:
    def __init__(self, config):
        self.config = config

    def trainingPipeline(self):
        pass


class SelfPlayAndTrainingOrchestrator:
    def __init__(self, config):
        self.config = config
        self.agent: DeepNNAndMCTSAgent = config["AGENT"]
        self.model_iterations: int = config["ITERATIONS"]
        self.games_per_iteration: int = config["GAMES_PER_ITERATION"]

    def overallPipeline(self):
        debugObj.updateIteration(setZero=True)

        for iteration in range(self.model_iterations):
            self.performIteration()
            debugObj.updateIteration()

    def performIteration(self):
        plys_in_games = []
        num_playouts = np.arange(100, self.games_per_iteration * 100 + 1, 100)
        for game_num in range(self.games_per_iteration):
            # num_plys = self._playAGame()
            num_plys = self._playAGameWithSetPlayouts(num_playouts[game_num])
            print(
                f"Game {game_num} Num playouts {num_playouts[game_num]} Num plys {num_plys}"
            )

            plys_in_games.append(num_plys)
            debugObj.updateGameInIteration()

        print(f"Iteration {debugObj.iteration} : Average plys {np.mean(plys_in_games)}")

        self._trainNNModel()

    def _playAGameWithSetPlayouts(self, n_playouts=10):
        self.agent.config["NUM_PLAYOUTS"] = n_playouts
        return self._playAGame()

    def _playAGame(self):
        state = GameState()
        current_game_training_data = []
        while not state.isTerminal():
            action_info = self.agent.getActionWithInfo(state)
            current_game_training_data.append(
                (state, action_info["empirical_action_probs"])
            )

            action = action_info["action"]
            state = state.applyMove(action)
            debugObj.updateTurn()

        for i, (inter_state, action_probs) in enumerate(current_game_training_data):
            state_value = (
                0
                if state.getWinner() == GameState.NOONE
                else -1 if inter_state.next_player == state.getWinner() else 1
            )

            # if debugObj.iteration == 0 and i == 0:
            #     print(f"First state={inter_state}\n{state_value}")

            self.agent.saveToTrainingData(inter_state, state_value, action_probs)

        return len(current_game_training_data)

    def _trainNNModel(self):
        self.agent.trainNetwork()
        self.agent.clearTrainingData()
