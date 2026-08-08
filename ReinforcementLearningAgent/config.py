# Global configs
NUM_INITIAL_CHANNELS = 2
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
    # Do you want to use multi-processing in the self-play data collection phase?
    USE_MULTIPROCESSING=True,
    # How many processes to use to play games
    N_MULTIPROCESS_GAME_RUNNERS=N_MULTIPROCESS_GAME_RUNNERS,
    # How many iterations to perform (1 iteration = 1 collection step + 1 update step)
    NUM_ITERATIONS=100,
    # Start from some iteration (the model checkpoint at the end of the previous iteration must exist)
    # Do not provide this if you want to start from scratch
    # START_FROM_ITERATION=45,
    # How many (state, mcts_enhanced_action_priors, game_outcome). Too many datapoints will make all datapoints highly dependant. Too few will leave little training data
    NUM_DATAPOINTS_PER_GAME=5,
    # Data from how many previous iterations must be stored in the replay buffer? Ideally 1, but this leaves too little training data
    NUM_LEGACY_ITERATIONS_DATA=4,
    # Number of games to play per iteration. If multiple processes are being used, this will be divided among the processes
    GAMES_PER_ITERATION=5 * N_MULTIPROCESS_GAME_RUNNERS,
    # Actions are sampled from the provided distribution over actions modified by the temperature. Larger temperature pushes distributions towards uniform distribution (greater exploration), and smaller temperatures push it towards a point mass distribution (greater exploitation).
    # Temperature switches from initial to final based on the trigger ply (which move within a game)
    INITIAL_TEMPERATURE=2,
    TRIGGER_PLY=6,
    FINAL_TEMPERATURE=0.5,
    **GLOBAL_CONFIG,
)

# Agent config
AGENT_CONFIG = dict(
    # Coefficient for the uncertainty based prior. Increasing this value increases model prior based exploration bonus (a term that has a high value if very few vists have occured from that state, or if the model thinks it is a good action to take.)
    UCT_C_COEFF=0.5,
    # Number of MCTS playouts for each move in the game
    NUM_PLAYOUTS=1000,
    # Inference is usually performed for each request, but this can be quite slow and not utilize the GPU effectively. Batched inference queues the inference request and registers a "virtual loss" which is reversed when the INFERENCE_MIN_BATCH_SIZE is reached and the results are available
    USE_BATCHED_INFERENCE=True,
    INFERENCE_MIN_BATCH_SIZE=16,
    **GLOBAL_CONFIG,
)

# Model config ConvolutionalPAndV
MODEL_CONFIG = dict(
    NUM_CNN_FILTERS=64,
    KERNEL_SIZE=3,
    NUM_RESIDUAL_BLOCKS=5,
    DROPOUT_RATE=0.2,
    POLICY_HEAD_FILTERS=8,
    VALUE_HEAD_FILTERS=8,
    USE_GPU=False,
    **GLOBAL_CONFIG,
)


# # Model config Convolutional4PAndV
# MODEL_CONFIG = dict(
#     NUM_CNN_FILTERS=16,
#     KERNEL_SIZE=3,
#     DROPOUT_RATE=0.2,
#     POLICY_HEAD_FILTERS=8,
#     VALUE_HEAD_FILTERS=8,
#     USE_GPU=False,
#     **GLOBAL_CONFIG,
# )

# Training config
TRAINING_CONFIG = dict(
    # Howlarge should the test
    TEST_SIZE=0.1,
    # Learning rate for the training phase
    LEARNING_RATE=0.01,
    DECREASE_LR_EVERY_K_ITERATIONS=20,
    EPOCHS=5,
    BATCH_SIZE=32,
    USE_GPU=False,
    BASE_PATH="ModelCheckpoints/debug_model",
)


RANDOM_PLAYER_BASE_CONFIG = dict(
    NAME="random",
    AGENT_TYPE="RANDOM_AGENT",
)

DEEPNN_MCTS_BASE_CONFIG = dict(
    NAME="deepnn_mcts_bs32",
    AGENT_TYPE="DEEPNN_AND_MCTS_AGENT",
    AGENT_CONFIG=dict(
        # Coefficient for the uncertainty based prior. Increasing this value increases model prior based exploration bonus (a term that has a high value if very few vists have occured from that state, or if the model thinks it is a good action to take.)
        UCT_C_COEFF=2,
        # Number of MCTS playouts for each move in the game
        NUM_PLAYOUTS=1000,
        # Inference is usually performed for each request, but this can be quite slow and not utilize the GPU effectively. Batched inference queues the inference request and registers a "virtual loss" which is reversed when the INFERENCE_MIN_BATCH_SIZE is reached and the results are available
        USE_BATCHED_INFERENCE=True,
        INFERENCE_MIN_BATCH_SIZE=32,
        **GLOBAL_CONFIG,
    ),
    MODEL_CONFIG=MODEL_CONFIG,
    BASE_PATH=TRAINING_CONFIG["BASE_PATH"],
)


DEEPNN_MCTS_BASE_CONFIG2 = dict(
    NAME="deepnn_mcts_bs1",
    AGENT_TYPE="DEEPNN_AND_MCTS_AGENT",
    AGENT_CONFIG=dict(
        # Coefficient for the uncertainty based prior. Increasing this value increases model prior based exploration bonus (a term that has a high value if very few vists have occured from that state, or if the model thinks it is a good action to take.)
        UCT_C_COEFF=2,
        # Number of MCTS playouts for each move in the game
        NUM_PLAYOUTS=1000,
        # Inference is usually performed for each request, but this can be quite slow and not utilize the GPU effectively. Batched inference queues the inference request and registers a "virtual loss" which is reversed when the INFERENCE_MIN_BATCH_SIZE is reached and the results are available
        USE_BATCHED_INFERENCE=True,
        INFERENCE_MIN_BATCH_SIZE=1,
        **GLOBAL_CONFIG,
    ),
    MODEL_CONFIG=MODEL_CONFIG,
    BASE_PATH=TRAINING_CONFIG["BASE_PATH"],
)

UNIFORM_PRIOR_BASE_CONFIG = dict(
    NAME="uniform_prior_mcts",
    AGENT_TYPE="UNIFORM_PRIOR_MCTS_AGENT",
    AGENT_CONFIG=dict(
        # Coefficient for the uncertainty based prior. Increasing this value increases model prior based exploration bonus (a term that has a high value if very few vists have occured from that state, or if the model thinks it is a good action to take.)
        UCT_C_COEFF=2,
        # Number of MCTS playouts for each move in the game
        NUM_PLAYOUTS=1000,
        # Inference is usually performed for each request, but this can be quite slow and not utilize the GPU effectively. Batched inference queues the inference request and registers a "virtual loss" which is reversed when the INFERENCE_MIN_BATCH_SIZE is reached and the results are available
        USE_BATCHED_INFERENCE=True,
        INFERENCE_MIN_BATCH_SIZE=4,
        **GLOBAL_CONFIG,
    ),
    MODEL_CONFIG=MODEL_CONFIG,
    BASE_PATH=TRAINING_CONFIG["BASE_PATH"],
)


ARENA_CONFIG = dict(
    PRINT_GAMES=False,
    NUM_GAMES=50,
    BEGIN_POSITION_DEPTH=3,
    USE_MULTIPROCESSING=True,
    N_MULTIPROCESS_GAME_RUNNERS=N_MULTIPROCESS_GAME_RUNNERS,
    PLAYER1_BASE_CONFIG=DEEPNN_MCTS_BASE_CONFIG,
    PLAYER1_VARIANTS=dict(ITERATIONS=[5]),
    PLAYER2_BASE_CONFIG=DEEPNN_MCTS_BASE_CONFIG2,
    PLAYER2_VARIANTS=dict(ITERATIONS=[1]),
)

TEST_CONFIG = dict(
    TEST="Accuracy",
    # Test specifics
    # INFERENCE_BATCH_SIZES_TO_COMPARE=[1, 8, 32],
    TEST_CASE_SET="DEFAULT_TEST_CASES",
    MODEL_WEIGHTS_SOURCE="ModelCheckpoints/debug_model/iteration_25.pth",
)

SAVE_CONFIG = dict(
    SAVE_FILEPATH="SavedModels/model.onnx",
    MODEL_CONFIG={
        **MODEL_CONFIG,
        "USE_GPU": False,
        "MODEL_WEIGHTS_SOURCE": "ModelCheckpoints/debug_model/iteration_33.pth",
    },
)

SELF_PLAY_AND_TRAINING_PIPELINE = "SelfPlayAndTrainingPipeline"
MODEL_VERIFICATION_PIPELINE = "ModelVerificationPipeline"
ARENA_PIPELINE = "ArenaPipeline"
ONNX_SAVE_PIPELINE = "ONNXSavePipeline"

PIPELINE = MODEL_VERIFICATION_PIPELINE
# ARENA_PIPELINE
# SELF_PLAY_AND_TRAINING_PIPELINE
# MODEL_VERIFICATION_PIPELINE


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
