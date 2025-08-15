from Agent.policy_and_value_model import PolicyAndValueFunction
from config import MODEL_CONFIG
from Experiments.test_cases import TEST_CASES
from GameImplementation.game_state import GameState


def getStateValuePerspective(state):
    next_player = state.next_player_str
    this_player = "RED" if next_player == "YELLOW" else "YELLOW"

    return this_player


def testModelOnTestCase(model_fn: PolicyAndValueFunction, test_case):
    print(f"Test Case={test_case['DESCRIPTION']}")

    game_state: GameState = test_case["GAME_STATE"]
    print(f"{game_state}")

    state_value, action_probabilities = model_fn.evaluateFunction(game_state)

    sv_perspective = getStateValuePerspective(game_state)
    action_probabilities_str = [f"{prob:.3f}" for prob in action_probabilities]

    print(f"Predicted state value = {state_value} (Perspective={sv_perspective})")
    print(f"Predicted action probabilities = {action_probabilities_str}")
    print()


def testModel(model_fn=None, test_cases=None):
    print(
        f"Testing model with weights source={model_fn.config['MODEL_WEIGHTS_SOURCE']}"
    )

    for test_case in test_cases:
        testModelOnTestCase(model_fn, test_case)


def createModelFunction(config, weights_source):
    full_config = MODEL_CONFIG.copy()
    full_config.update(dict(MODEL_WEIGHTS_SOURCE=weights_source))
    pv_fn = PolicyAndValueFunction(full_config)

    return pv_fn


def main(model_weights_source):
    # "ModelCheckpoints/testrun1/iteration_100.pth"
    # "ModelCheckpoints/debug_model/iteration_30.pth"
    model_fn = createModelFunction(
        MODEL_CONFIG, model_weights_source
    )
    testModel(model_fn=model_fn, test_cases=TEST_CASES)


if __name__ == "__main__":
    main()
