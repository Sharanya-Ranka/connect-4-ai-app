import torch
import numpy as np
from GameImplementation.game_state import MCTSGameState, GameState
from Agent.policy_and_value_model import (
    PolicyAndValueTrainer,
    PolicyAndValueFunction,
)
from config import debugObj


class DeepNNAndMCTSAgent:
    """
    Represents the "AlphaZero" like agent
    Consists of :
    Deep Neural Network: Evaluating states to provide estimated state value and policy (action) probabilities (proportional to how good the action is)
    An MCTS System: Monte Carlo Tree Search uses the policy of the NN as a 'bias' to inform its search, and then further refines the "goodness" values of actions.

    This NN + MCTS system is used to train the next iteration of the NN,
    this loop leads to the NN giving better estimates, and MCTS being better informed, so its search is in turn more effective
    """

    UCT_C_COEFF = 1

    def __init__(self, config):
        """
        Initializes the NN used, keeps track of training data generated during self play
        """
        self.config = config
        self.policy_value_function = PolicyAndValueFunction(config)
        self.training_data = []

        self.trainer = self._setUpTrainer()

    def getNetworkOnlyActionProbabilities(self, state):
        """
        Returns the action probabilties estimates from the Neural Network only.
        """
        state_value, action_probabilities = self.policy_value_function.evaluateFunction(
            state
        )

        return action_probabilities

    def getNetworkOnlyStateValue(self, state):
        """
        Returns the state value estimates from the Neural Network only.
        """
        state_value, action_probabilities = self.policy_value_function.evaluateFunction(
            state
        )

        return state_value

    def getNetworkOnlyStateValueAndActionProbabilities(self, state):
        """
        Returns the state value  and action probability estimates from the Neural Network only.
        """
        state_value, action_probabilities = self.policy_value_function.evaluateFunction(
            state
        )

        # if debugObj.requireNetworkActualOp():
        #     print(f"Network Only output")
        #     print(
        #         f"State:\n{state}\nState value={state_value}\nAction Probabilities={action_probabilities}\n",
        #         flush=True,
        #     )

        return state_value, action_probabilities

    def clearTrainingData(self):
        self.training_data = []
        # print(f"Cleared training data")

    def saveToTrainingData(self, state, value, action_probs):
        """
        Save the state, refined state_value (outcome of actual play) and refined action probabilities to be used to train the NN further
        """
        self.training_data.append((state, value, action_probs))

    def getMCTSEmpiricalStateValueAndActionProbabilties(self, state, action_bias):
        """
        Returns the action probabilties estimates from the NN + MCTS system. MCTS uses action_bias (estimates from the NN only)
        to inform its search.
        Generates a Tree each time this is called, starting from the state it is given
        Conducts playouts (selection + expansion + simulation + backpropagation) NUM_PLAYOUTS times
        to accumulate 'refined' action probabilities and state values, and returns them
        """
        root_state = MCTSGameState.createMCTSState(state)
        root_state.prior = action_bias
        # breakpoint()

        for playout_ind in range(self.config["NUM_PLAYOUTS"]):
            leaf_state = self._MCTSSelection(root_state)
            self._MCTSExpansion(leaf_state)
            # result = self._MCTSSimulation(leaf_state)
            self._MCTSBackpropagation(leaf_state, leaf_state.v)
            debugObj.updateSim()

        # Calculate empirical probabilities using uct scores
        q_vals = root_state.q
        illegal_moves = [
            ind for ind, child in enumerate(root_state.children) if child == None
        ]
        q_vals[illegal_moves] = -np.inf
        final_empirical_probabilities = np.exp(q_vals) / np.sum(np.exp(q_vals))
        # TODO : Empirical probabilities should be dependent on number of visits
        # if any([child == None for child in root_state.children]):
        #     breakpoint()

        return final_empirical_probabilities

    def _MCTSSelection(self, root_state: MCTSGameState) -> MCTSGameState:
        """
        Performs the selection step in MCTS.
        Until you get to a leaf, choose an action based on its 'goodness' score
        Goodness score depends on the NN bias, and outcomes from previous playouts with an 'uncertainty benefit of doubt'
        """

        def getBiasedUCTScore(state: MCTSGameState):
            move_uct_scores = state.q + DeepNNAndMCTSAgent.UCT_C_COEFF * state.prior / (
                1 + state.visits
            )
            illegal_indices = [
                ind for ind, child in enumerate(state.children) if child == None
            ]
            move_uct_scores[illegal_indices] = np.nan

            return move_uct_scores

        state = root_state

        while state.is_leaf != True and state.isTerminal() != True:
            # scores = getBiasedUCTScore(state) * (
            #     -1 if state.next_player == GameState.RED else 1
            # )
            scores = getBiasedUCTScore(state)
            best_action = np.nanargmax(np.array(scores, dtype=np.float32))

            state = state.children[best_action]

        return state

    def _MCTSExpansion(self, state: MCTSGameState):
        """
        Performs the expansion step in MCTS.
        We are at a leaf state, and need to add its children to the tree.
        Children are initialized with the bias provided by the NN.
        Note that in this game (s, a) implies a unique s' TODO complete
        """
        if state.isTerminal() == False:
            children_created = state.createChildrenStates()
            assert children_created == True

            for child in state.children:
                if child != None:
                    state_value, action_probabilities = (
                        self.getNetworkOnlyStateValueAndActionProbabilities(child.state)
                    )
                    child.prior = action_probabilities
                    child.v = state_value

    # def _MCTSSimulation(self, state: MCTSGameState) -> int:
    #     """
    #     Performs the simulation step in MCTS.
    #     Randomly chooses next actions (uninformed) until a terminal state is reached
    #     Returns the winner in the simulation
    #     """
    #     temp_state = state.state
    #     while temp_state.isTerminal() == False:
    #         available_moves = temp_state.possible_next_moves
    #         random_move = np.random.choice(available_moves)
    #         temp_state = temp_state.applyMove(random_move)

    #     return temp_state.getWinner()

    def _MCTSBackpropagation(self, leaf_state: MCTSGameState, result: float):
        state = leaf_state.parent
        last_move = leaf_state.last_move
        while state != None:
            state.visits[last_move] += 1
            state.w[last_move] += result * (
                -1 if state.next_player == leaf_state.next_player else 1
            )

            # if result == GameState.RED:
            #     state.w[last_move] -= 1
            # elif result == GameState.YELLOW:
            #     state.w[last_move] += 1

            # This happens implicitly
            # if result == GameState.NOONE:
            #     state.w += 0

            state.q[last_move] = state.w[last_move] / state.visits[last_move]

            last_move = state.last_move
            state = state.parent

    def getActionWithInfo(self, state: GameState) -> dict:
        """
        Performs the backpropagation step in MCTS.
        Goes up the current branch, updating every state in the tree based on the outcome
        """
        state_value, action_bias = self.getNetworkOnlyStateValueAndActionProbabilities(
            state
        )
        empirical_action_probs = self.getMCTSEmpiricalStateValueAndActionProbabilties(
            state, action_bias
        )
        # if debugObj.requireMCTSActionBias():
        #     print(f"MCTS output")
        #     print(
        #         f"State:\n{state}\nEmpirical Action Probabilities={empirical_action_probs}\n",
        #         flush=True,
        #     )
        action = np.random.choice(state.cols, p=empirical_action_probs)
        # breakpoint()
        # print(f"Empirical action probs={empirical_action_probs}")
        action_info = dict(action=action, empirical_action_probs=empirical_action_probs)
        return action_info

    def _setUpTrainer(self):
        """
        Setting up the trainer, which will handle training the NN each iteration
        """
        # trainer_config = dict(
        #     LEARNING_RATE=self.config['LEARNING_RATE'],

        # )

        # breakpoint()
        trainer = PolicyAndValueTrainer(self.config)

        return trainer

    def trainNetwork(self):
        """
        Run the trainer, providing the model and accumulated self-play data.
        """
        self.trainer.runTrainPipeline(
            self.policy_value_function.pv_network, self.training_data
        )
        self.policy_value_function.updateModelIter()
