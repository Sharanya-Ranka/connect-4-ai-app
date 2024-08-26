const MCTS_UCT_PLAYER = "MCTS_UCT_PLAYER";
const MCTS_UCT_MONITOR_PLAYER = "MCTS_UCT_MONITOR_PLAYER";
const HUMAN_PLAYER = "HUMAN_PLAYER";
// const DEFAULT_GAME_CONFIG = {
//   num_rows: 6,
//   num_cols: 7,
//   player1: { type: MCTS_UCT_PLAYER, strength: 1000 },
//   player2: { type: HUMAN_PLAYER },
//   is_game_active: false,
// };

const MAX_ROWS = 10;
const MAX_COLUMNS = 10;

const DEFAULT_PLAYER_CONFIGS = {
  [HUMAN_PLAYER]: { type: HUMAN_PLAYER },
  [MCTS_UCT_PLAYER]: { type: MCTS_UCT_PLAYER, strength: 1000 },
  [MCTS_UCT_MONITOR_PLAYER]: { type: MCTS_UCT_MONITOR_PLAYER, strength: 2000 },
};
const DEFAULT_GAME_CONFIG = {
  num_rows: 6,
  num_cols: 7,
  player1: { type: HUMAN_PLAYER },
  // player1: { type: MCTS_UCT_PLAYER, strength: 1000 },
  player2: { type: MCTS_UCT_PLAYER, strength: 1000 },
  monitor: { type: MCTS_UCT_MONITOR_PLAYER, strength: 2000 },
};

const DEFAULT_GAME_STATE = {
  num_rows: DEFAULT_GAME_CONFIG.num_rows,
  num_cols: DEFAULT_GAME_CONFIG.num_cols,
  all_moves: [],
  active_player_ind: 1,
  paused: false,
  is_game_active: false,
  ui_state: {
    column_clicked: null,
    column_hover: null,
    highlight_state: null,
  },
};

const MCTS_AGENT_STRENGTHS = [50, 100, 500, 1000, 2000, 5000];
// const

export {
  MCTS_UCT_PLAYER,
  HUMAN_PLAYER,
  MCTS_UCT_MONITOR_PLAYER,
  DEFAULT_PLAYER_CONFIGS,
  DEFAULT_GAME_CONFIG,
  DEFAULT_GAME_STATE,
  MCTS_AGENT_STRENGTHS,
  MAX_ROWS,
  MAX_COLUMNS,
};
