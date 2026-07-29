from GameImplementation.game_state import GameState
import numpy as np
from typing import List
import random


def getGameState(game_state_list):
    game_state = np.array(game_state_list, dtype=np.int8)
    move_count = np.count_nonzero(game_state)

    return GameState(state=game_state, move_count=move_count)


DEFAULT_TEST_CASES = [
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
    dict(
        DESCRIPTION="Middle Game: Yellow is almost winning",
        GAME_STATE=getGameState(
            [
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 1, 1, 1, 0],
                [0, 0, 0, 2, 2, 2, 0],
                [2, 0, 2, 2, 1, 1, 0],
                [2, 1, 1, 2, 1, 1, 2],
            ]
        ),
    ),
    dict(
        DESCRIPTION="Late Game: Yellow is almost winning",
        GAME_STATE=getGameState(
            [
                [1, 0, 2, 1, 0, 2, 1],
                [2, 0, 1, 2, 0, 1, 2],
                [2, 0, 2, 2, 0, 1, 1],
                [1, 0, 2, 2, 0, 1, 2],
                [2, 1, 1, 1, 0, 2, 1],
                [1, 2, 1, 2, 1, 1, 2],
            ]
        ),
    ),
    dict(
        DESCRIPTION="Late Game: Red is almost winning",
        GAME_STATE=getGameState(
            [
                [1, 0, 2, 1, 0, 2, 1],
                [2, 0, 1, 2, 0, 1, 2],
                [2, 0, 2, 2, 0, 1, 1],
                [1, 0, 2, 2, 0, 1, 2],
                [2, 1, 1, 1, 2, 2, 1],
                [1, 2, 1, 2, 1, 1, 2],
            ]
        ),
    ),
    dict(
        DESCRIPTION="Draw",
        GAME_STATE=getGameState(
            [
                [2, 0, 1, 2, 1, 2, 0],
                [1, 2, 2, 2, 1, 1, 2],
                [2, 1, 1, 2, 2, 2, 1],
                [1, 2, 2, 1, 1, 1, 2],
                [2, 1, 1, 1, 2, 1, 1],
                [1, 1, 2, 2, 1, 2, 2],
            ]
        ),
    ),
]

RANDOM_TEST_CASES = [
    dict(
        DESCRIPTION=f"Random TC {i}",
        GAME_STATE=getGameState(np.random.randint(0, 3, (6, 7))),
    )
    for i in range(1000)
]


def getRandomTestCases(count: int, from_pool: int | None = None) -> List[GameState]:
    if from_pool == None:
        from_pool = 10 * count

    pool_states = set()
    pool_states.add(GameState())

    while len(pool_states) < from_pool:
        temp = GameState()
        while not temp.isTerminal() and len(pool_states) < from_pool:
            temp = temp.applyMove(random.choice(temp.possible_next_moves))
            if not temp.isTerminal():
                pool_states.add(temp)

    # breakpoint()
    chosen_states = np.random.choice(list(pool_states), count, replace=False)
    print(f"Created random test cases")
    return [
        dict(
            DESCRIPTION=f"Random TC {i}",
            GAME_STATE=game_state,
        )
        for i, game_state in enumerate(chosen_states)
    ]
