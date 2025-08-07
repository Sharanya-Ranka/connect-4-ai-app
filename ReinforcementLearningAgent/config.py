UNIQUE_TOKENS = 3
NUM_ROWS = 6
NUM_COLS = 7

NUM_PLAYOUTS = 500
NUM_ITERATIONS = 2
GAMES_PER_ITERATION = 10

TEST_SIZE = 0.2
LEARNING_RATE = 0.01
EPOCHS = 2
HIDDEN_DIM = 100
BATCH_SIZE = 16

NUM_CNN_FILTERS = 32
KERNEL_SIZE = 3
NUM_RESIDUAL_BLOCKS = 5
DROPOUT_RATE = 0.3
POLICY_HEAD_FILTERS = 16
VALUE_HEAD_FILTERS = 16


def getModelConfig():
    model_config = dict(
        NUM_CNN_FILTERS=NUM_CNN_FILTERS,
        KERNEL_SIZE=KERNEL_SIZE,
        NUM_RESIDUAL_BLOCKS=NUM_RESIDUAL_BLOCKS,
        DROPOUT_RATE=DROPOUT_RATE,
        POLICY_HEAD_FILTERS=POLICY_HEAD_FILTERS,
        VALUE_HEAD_FILTERS=VALUE_HEAD_FILTERS,
    )
    return model_config


def getAgentConfig():
    debug_agent_config = dict(
        UCT_C_COEFF=1,  # Hardcoded in DeepNNAndMCTSAgent
        NUM_PLAYOUTS=NUM_PLAYOUTS,  # Needs to be defined in the config passed to DeepNNAndMCTSAgent
        MODEL_WEIGHTS_SOURCE=None,  # Needs to be defined in the config passed to PolicyAndValueFunction
        NUM_ROWS=NUM_ROWS,  # Needs to be defined in the config passed to PolicyAndValueNetwork
        NUM_COLS=NUM_COLS,  # Needs to be defined in the config passed to PolicyAndValueNetwork
        UNIQUE_TOKENS=UNIQUE_TOKENS,  # Needs to be defined in the config passed to PolicyAndValueNetwork
        HIDDEN_DIM=HIDDEN_DIM,  # Needs to be defined in the config passed to PolicyAndValueNetwork
        DATASET=None,  # Needs to be defined in the config passed to SelfPlayDataset
        LEARNING_RATE=LEARNING_RATE,  # Needs to be defined in the config passed to PolicyAndValueTrainer
        BATCH_SIZE=BATCH_SIZE,
        EPOCHS=EPOCHS,  # Needs to be defined in the config passed to PolicyAndValueTrainer
        TEST_SIZE=TEST_SIZE,
        **getModelConfig(),
    )

    return debug_agent_config


def getSelfPlayConfig():
    from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent

    debug_agent_config = getAgentConfig()

    debug_config = dict(
        AGENT=DeepNNAndMCTSAgent(debug_agent_config),  # Placeholder, as it's an object
        ITERATIONS=NUM_ITERATIONS,  # This is `model_iterations`, needs to be defined in the config passed to SelfPlayTrainingOrchestrator
        GAMES_PER_ITERATION=GAMES_PER_ITERATION,  # Needs to be defined in the config passed to SelfPlayTrainingOrchestrator
    )

    return debug_config


class DebugManager:
    def __init__(self, config):
        self.config = config
        self.iteration = 0
        self.game_in_iteration = 0
        self.turn = 0
        self.sim = 0

        self.epoch = 0
        self.batch = 0

        self.debug_this_iteration = False
        self.debug_this_game = False
        self.debug_this_turn = False

        self.require_network_actual_op = False
        self.require_network_action_bias = False
        self.require_mcts_action_bias = False
        # self.require_

    def updateIteration(self, setZero=False):
        if setZero:
            self.iteration = 0
        else:
            self.iteration += 1

        self.debug_this_iteration = True
        # if self.iteration == 0 or self.iteration == 3:
        #     self.debug_this_iteration = True
        # else:
        #     self.debug_this_iteration = False

        self.updateGameInIteration(setZero=True)

    def updateGameInIteration(self, setZero=False):
        if setZero:
            self.game_in_iteration = 0
        else:
            self.game_in_iteration += 1

        if (self.game_in_iteration == 0) and self.debug_this_iteration:
            self.debug_this_game = True
        else:
            self.debug_this_game = False

        self.updateTurn(setZero=True)

    def updateTurn(self, setZero=False):
        if setZero:
            self.turn = 0
        else:
            self.turn += 1

        if (self.turn == 0 or self.turn == 17) and self.debug_this_game:
            self.debug_this_turn = True
        else:
            self.debug_this_turn = False

        self.updateSim(setZero=True)

    def updateSim(self, setZero=False):
        if setZero:
            self.sim = 0
        else:
            self.sim += 1

        # print(f"SetSim={self.sim} {self.debug_this_turn}")

        if (self.sim == 0 or self.sim == 95) and self.debug_this_turn:
            # print(
            #     f"Iteration: {self.iteration}, Game: {self.game_in_iteration}, Turn: {self.turn}, Sim: {self.sim}"
            # )
            self.require_network_actual_op = True
            self.require_mcts_action_bias = True

    def updateEpoch(self, setZero=False):
        if setZero:
            self.epoch = 0
        else:
            self.epoch += 1

    def updateBatch(self, setZero=False):
        if setZero:
            self.batch = 0
        else:
            self.batch += 1

    def requireNetworkActualOp(self):
        if self.require_network_actual_op:
            self.require_network_actual_op = False
            return True
        else:
            return False

    def requireNetworkActionBias(self):
        pass

    def requireMCTSActionBias(self):
        if self.require_mcts_action_bias:
            self.require_mcts_action_bias = False
            return True
        else:
            return False


debugObj = DebugManager({})
