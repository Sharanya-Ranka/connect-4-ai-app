# Global configs
NUM_INITIAL_CHANNELS = 4
NUM_ROWS = 6
NUM_COLS = 7

# Global config (Dict format)
GLOBAL_CONFIG = dict(
    NUM_INITIAL_CHANNELS=NUM_INITIAL_CHANNELS,
    NUM_ROWS=NUM_ROWS,
    NUM_COLS=NUM_COLS,
)


N_MULTIPROCESS_GAME_RUNNERS = 5
# Self play config
SELF_PLAY_CONFIG = dict(
    USE_MULTIPROCESSING=False,
    N_MULTIPROCESS_GAME_RUNNERS=N_MULTIPROCESS_GAME_RUNNERS,
    NUM_ITERATIONS=120,
    # START_FROM_ITERATION=37,
    NUM_DATAPOINTS_PER_GAME=10,
    NUM_LEGACY_ITERATIONS_DATA=5,
    GAMES_PER_ITERATION=40 * N_MULTIPROCESS_GAME_RUNNERS,
    INITIAL_TEMPERATURE=5,
    TRIGGER_PLY=10,
    FINAL_TEMPERATURE=0.1,
    **GLOBAL_CONFIG,
)

# Agent config
AGENT_CONFIG = dict(
    UCT_C_COEFF=2,
    NUM_PLAYOUTS=60,
    USE_BATCHED_INFERENCE=True,
    INFERENCE_MIN_BATCH_SIZE=16,
    **GLOBAL_CONFIG,
)

# Model config
MODEL_CONFIG = dict(
    NUM_CNN_FILTERS=64,
    KERNEL_SIZE=3,
    NUM_RESIDUAL_BLOCKS=9,
    DROPOUT_RATE=0.2,
    POLICY_HEAD_FILTERS=64,
    VALUE_HEAD_FILTERS=32,
    USE_GPU=True,
    **GLOBAL_CONFIG,
)

# Training config
TRAINING_CONFIG = dict(
    TEST_SIZE=0.2,
    LEARNING_RATE=0.002,
    EPOCHS=50,
    BATCH_SIZE=32,
    USE_GPU=MODEL_CONFIG["USE_GPU"],
    BASE_PATH="ModelCheckpoints/debug_model",
)

TEST_CONFIG = dict(
    TEST="BatchedInference",
    # Test specifics
    BATCH_SIZE=32,
    TEST_CASE_SET="RANDOM_TEST_CASES",
    MODEL_WEIGHTS_SOURCE="ModelCheckpoints/debug_model/iteration_0.pth",
)


def getAgentFullConfig():
    agent_config = dict(
        GLOBAL_CONFIG=GLOBAL_CONFIG,
        MODEL_CONFIG=MODEL_CONFIG,
        TRAINING_CONFIG=TRAINING_CONFIG,
        AGENT_CONFIG=AGENT_CONFIG,
    )

    return agent_config


def getSelfPlayFullConfig():
    # from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent

    AGENT_FULL_CONFIG = getAgentFullConfig()

    self_play_config = dict(
        **AGENT_FULL_CONFIG,
        SELF_PLAY_CONFIG=SELF_PLAY_CONFIG,
    )

    return self_play_config


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
