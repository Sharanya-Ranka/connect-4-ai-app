from GameImplementation.game_state import GameState
import numpy as np
import torch


class PositionProvider:
    @staticmethod
    def generateStartingPositions(at_depth=5, num_positions=5):
        """
        We can generate positions in various ways.
        1) Perform random moves until you get to depth k and add the set. Do this until you get n states
        2) Generate all posible positions at depth k and choose n from them

        We use the first method, since the number of states explodes quickly
        """
        set_of_states = set()

        while len(set_of_states) < num_positions:
            state = GameState()
            current_depth = 0
            while not state.isTerminal() and current_depth < at_depth:
                valid_actions = state.possible_next_moves
                chosen_action = np.random.choice(valid_actions)

                state = state.applyMove(chosen_action)
                current_depth += 1

            set_of_states.add(state)

        return list(set_of_states)


class ModelSaver:
    @staticmethod
    def saveONNXModel(model, dummy_input, save_filepath):
        torch.onnx.export(
            model, 
            dummy_input, 
            save_filepath, 
            export_params=True, 
            opset_version=11, 
            do_constant_folding=True
        )

        
