import { GameState } from "./GameState";

function getGameStateObjectFromGameStateDescription(game_state_description) {
  const { num_rows, num_cols, all_moves } = game_state_description;
  const game_state = new GameState(num_rows, num_cols, all_moves);
  return game_state;
}

function getGameStateDescriptionFromGameStateObject(game_state_obj) {
  const game_state_description = {
    num_rows: game_state_obj.max_rows,
    num_cols: game_state_obj.max_columns,
    all_moves: game_state_obj.all_moves,
  };

  return game_state_description;
}

export {
  getGameStateDescriptionFromGameStateObject,
  getGameStateObjectFromGameStateDescription,
};
