import time
import torch

from Agent.policy_and_value_model import PolicyAndValueFunction
from config import MODEL_CONFIG, AGENT_CONFIG, TEST_CONFIG
from Experiments.test_cases import (
    DEFAULT_TEST_CASES,
    RANDOM_TEST_CASES,
    getRandomTestCases,
)
from GameImplementation.game_state import GameState
from Agent.deepnn_and_mcts_agent import DeepNNAndMCTSAgent
import functools
import itertools
import numpy as np


def getStateValuePerspective(state):
    next_player = state.next_player_str
    this_player = "RED" if next_player == "YELLOW" else "YELLOW"

    return this_player


class ModelTesting:
    def __init__(self, config):
        self.config = config
        self.test_config = config  # ["TEST_CONFIG"]

    def performTest(self):
        if self.test_config["TEST"] == "Accuracy":
            self.testAccuracySetUp()
            self.testAccuracy()
        elif self.test_config["TEST"] == "Compilation":
            self.testCompilationSetUp()
            self.testCompilation()
        elif self.test_config["TEST"] == "BatchedInference":
            self.testBatchedInferenceSetUp()
            self.testBatchedInference()
        elif self.test_config["TEST"] == "BatchedInferenceAccuracy":
            self.testBatchedInferenceAccuracy()

    def testAccuracySetUp(self):
        model_config = MODEL_CONFIG.copy()
        agent_config = AGENT_CONFIG.copy()

        model_config.update(
            dict(MODEL_WEIGHTS_SOURCE=self.test_config["MODEL_WEIGHTS_SOURCE"])
        )

        config = dict(MODEL_CONFIG=model_config, AGENT_CONFIG=agent_config)
        self.agent = DeepNNAndMCTSAgent(config)

    def getTestCases(self):
        if self.test_config["TEST_CASE_SET"] == "DEFAULT_TEST_CASES":
            return DEFAULT_TEST_CASES
        elif self.test_config["TEST_CASE_SET"] == "RANDOM_TEST_CASES":
            return getRandomTestCases(20)

    def testAccuracy(self):
        test_cases = self.getTestCases()

        for test_case in test_cases:
            self.runAccuracySingleTestCase(test_case=test_case)

    def runAccuracySingleTestCase(self, test_case):
        print(f"Test Case={test_case['DESCRIPTION']}")

        game_state: GameState = test_case["GAME_STATE"]
        print(f"{game_state}")

        state_value, action_probabilities = (
            self.agent.getNetworkOnlyStateValueAndActionProbabilities(game_state)
        )
        if not game_state.isTerminal():
            action_info = self.agent.getActionWithInfo(game_state)
        else:
            action_info = {"empirical_action_probs": []}

        sv_perspective = getStateValuePerspective(game_state)
        action_probabilities_str = [f"{prob:.3f}" for prob in action_probabilities]
        action_probs_full_agent_str = [
            f"{prob:.3f}" for prob in action_info["empirical_action_probs"]
        ]
        action_probs_diff_str = [
            f"{prob:.3f}"
            for prob in action_info["empirical_action_probs"] - action_probabilities
        ]

        print(
            f"(Network only) state value = {state_value:.3f} (Perspective={sv_perspective})"
        )
        print(f"(Network only) action probabilities\t = {action_probabilities_str}")
        print(f"(Full agent) action probabilities\t = {action_probs_full_agent_str}")
        print(f"(Differences) action probabilities\t = {action_probs_diff_str}")
        print()

    def testCompilationSetUp(self):
        model_config = MODEL_CONFIG.copy()
        # agent_config = AGENT_CONFIG.copy()

        model_config.update(
            dict(MODEL_WEIGHTS_SOURCE=self.test_config["MODEL_WEIGHTS_SOURCE"])
        )

        config = model_config
        self.model_fn = PolicyAndValueFunction(config)
        self.model_fn_compiled = PolicyAndValueFunction(config)

    def testCompilation(self):
        nn_model = self.model_fn_compiled.pv_network

        compilation_start = time.time()
        nn_model_compiled = torch.compile(nn_model)
        compilation_end = time.time()

        self.model_fn_compiled.pv_network = nn_model_compiled
        print(f"Compilation time = {compilation_end-compilation_start:.4f}")

        unc_first, unc_rest = self.timeModelOnTestCases(self.model_fn)
        c_first, c_rest = self.timeModelOnTestCases(self.model_fn_compiled)

        print(
            f"Num test cases= 1 + {len(self.getTestCases()) - 1}\nUncompiled time={unc_first:.4f} {unc_rest:.4f}\nCompiled time={c_first:.4f} {c_rest:.4f}"
        )
        print()

    def timeModelOnTestCases(self, model_fn: PolicyAndValueFunction):
        test_cases = self.getTestCases() * 500
        print(len(test_cases))

        # Timing model_fn
        test_cases_starttime = time.time()
        for i, test_case in enumerate(test_cases):
            game_state: GameState = test_case["GAME_STATE"]
            retval = model_fn._evaluateFunction(game_state)

            if i == 0:
                first_testcase_endtime = time.time()

        test_cases_endtime = time.time()

        return (
            first_testcase_endtime - test_cases_starttime,
            test_cases_endtime - first_testcase_endtime,
        )

    def testBatchedInferenceSetUp(self):
        model_config = MODEL_CONFIG.copy()
        # agent_config = AGENT_CONFIG.copy()

        model_config.update(
            dict(MODEL_WEIGHTS_SOURCE=self.test_config["MODEL_WEIGHTS_SOURCE"])
        )

        config = model_config
        self.model_fn = PolicyAndValueFunction(config)

    def testBatchedInferenceAccuracy(self):
        test_cases = self.getTestCases()

        model_config = MODEL_CONFIG.copy()
        agent_config = AGENT_CONFIG.copy()

        model_config.update(
            dict(MODEL_WEIGHTS_SOURCE=self.test_config["MODEL_WEIGHTS_SOURCE"])
        )
        batch_sizes_to_compare = self.test_config["INFERENCE_BATCH_SIZES_TO_COMPARE"]
        predictions = {}

        for batch_size in batch_sizes_to_compare:
            print(f"On batch size={batch_size}")
            this_agent_config = agent_config.copy()
            this_agent_config["INFERENCE_MIN_BATCH_SIZE"] = batch_size
            config = dict(MODEL_CONFIG=model_config, AGENT_CONFIG=this_agent_config)
            agent = DeepNNAndMCTSAgent(config)

            this_agent_predictions = []

            for tc in test_cases:
                game_state = tc["GAME_STATE"]
                action_info = agent.getActionWithInfo(game_state)
                empirical_probs = action_info["empirical_action_probs"]
                this_agent_predictions.append(list(empirical_probs))

            # breakpoint()

            predictions[batch_size] = np.array(
                functools.reduce(lambda x, y: x + y, this_agent_predictions, [])
            )

        batch_combinatons = itertools.combinations(batch_sizes_to_compare, 2)

        def compareProbabilities(p1: np.ndarray, p2: np.ndarray):
            diff = np.abs(p1 - p2)
            hist, _ = np.histogram(diff, bins=[0, 0.01, 0.05, 0.10, 0.50, 1])
            hist = hist / hist.sum()
            # breakpoint()

            return (np.min(diff), np.max(diff), np.mean(diff), hist)

        for bs1, bs2 in batch_combinatons:
            print(f"Comparing inference batch sizes {bs1} and {bs2}")
            minp, maxp, meanp, hist = compareProbabilities(
                predictions[bs1], predictions[bs2]
            )

            hist_str = f"(0-1%){hist[0]:.2f} (1-5%){hist[1]:.2f} (5-10%){hist[2]:.2f} (10-50%){hist[3]:.2f} (50-100%){hist[4]:.2f}"
            print(f"Min diff={minp:.3f} Max diff={maxp:.3f} Mean diff={meanp:.3f}")
            print(f"Histogram={hist_str}")
            print()

    def testBatchedInference(self):
        batch_size = self.config.get("BATCH_SIZE", 16)
        test_cases = self.getTestCases()
        print(
            f"Testing batching with size={batch_size} Num of test cases={len(test_cases)}"
        )

        # Test batched inference speed
        batched_starttime = time.time()
        for batch_start_ind in range(0, len(test_cases), batch_size):
            game_states = [
                test_cases[i]["GAME_STATE"]
                for i in range(
                    batch_start_ind, min(batch_start_ind + batch_size, len(test_cases))
                )
            ]
            retval = self.model_fn._evaluateFunctionBatched(game_states)
        batched_endtime = time.time()
        batched_duration = batched_endtime - batched_starttime
        # Print the batched execution results, including total and average time
        print(
            f"Batched execution total = {batched_duration:.4f}s | Average = {batched_duration / len(test_cases):.6f}s"
        )

        # Test individual inference speed
        individual_starttime = time.time()
        for i, test_case in enumerate(test_cases):
            game_state: GameState = test_case["GAME_STATE"]
            retval = self.model_fn._evaluateFunction(game_state)
        individual_endtime = time.time()
        individual_duration = individual_endtime - individual_starttime
        # Print the individual execution results, including total and average time
        print(
            f"Individual execution total = {individual_duration:.4f}s | Average = {individual_duration / len(test_cases):.6f}s"
        )

    # def testGPUExec


def main(model_weights_source):
    # "ModelCheckpoints/testrun1/iteration_100.pth"
    # "ModelCheckpoints/debug_model/iteration_30.pth"
    model_fn = createModelFunction(MODEL_CONFIG, model_weights_source)
    testModel(model_fn=model_fn, test_cases=TEST_CASES)


if __name__ == "__main__":
    main()
