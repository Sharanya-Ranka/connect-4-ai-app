from GameImplementation.game_state import GameState
import numpy as np


def getGameState(game_state_list):
    game_state = np.array(game_state_list, dtype=np.int8)
    move_count = np.count_nonzero(game_state)

    return GameState(state=game_state, move_count=move_count)


TEST_CASES = [
    dict(
        DESCRIPTION="Beginning of Game",
        GAME_STATE=getGameState(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
            ]
        ),
    ),
    dict(
        DESCRIPTION="Early Game: Red is almost winning",
        GAME_STATE=getGameState(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 2, 0],
                [0, 0, 0, 0, 0, 2, 0],
                [0, 1, 1, 1, 0, 2, 0],
            ]
        ),
    ),
    dict(
        DESCRIPTION="Early Game: Yellow is almost winning",
        GAME_STATE=getGameState(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 2],
                [0, 1, 1, 0, 0, 0, 2],
                [0, 1, 1, 0, 0, 0, 2],
            ]
        ),
    ),
    # dict(
    #     DESCRIPTION="Late Game: Red is almost winning",
    #     GAME_STATE=getGameState(
    #         [
    #             [0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 2, 2, 1],
    #             [1, 2, 1, 1, 2, 1, 2],
    #             [2, 1, 2, 2, 1, 2, 1],
    #             [1, 2, 1, 1, 2, 1, 2],
    #         ]
    #     ),
    # ),
    # dict(
    #     DESCRIPTION="Late Game: Yellow is almost winning",
    #     GAME_STATE=getGameState(
    #         [
    #             [0, 0, 0, 0, 0, 0, 0],
    #             [0, 0, 0, 0, 0, 0, 0],
    #             [1, 0, 0, 0, 2, 2, 1],
    #             [1, 2, 1, 1, 2, 1, 2],
    #             [2, 1, 2, 2, 1, 2, 1],
    #             [1, 2, 1, 1, 2, 1, 2],
    #         ]
    #     ),
    # ),
    dict(
        DESCRIPTION="Draw",
        GAME_STATE=getGameState(
            [
                [2, 1, 1, 2, 1, 2, 2],
                [1, 2, 2, 2, 1, 1, 2],
                [2, 1, 1, 2, 2, 2, 1],
                [1, 2, 2, 1, 1, 1, 2],
                [2, 1, 1, 1, 2, 1, 1],
                [1, 1, 2, 2, 1, 2, 2],
            ]
        ),
    ),
]
