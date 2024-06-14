const MCTS_UCT_PLAYER = "MCTS_UCT_PLAYER";
const HUMAN_PLAYER = "HUMAN_PLAYER";
const DEFAULT_GAME_CONFIG = {
  num_rows: 6,
  num_cols: 7,
  player1: { type: MCTS_UCT_PLAYER, strength: 5000 },
  player2: { type: HUMAN_PLAYER },
  is_game_active: false,
};
// const

export { MCTS_UCT_PLAYER, HUMAN_PLAYER, DEFAULT_GAME_CONFIG };
