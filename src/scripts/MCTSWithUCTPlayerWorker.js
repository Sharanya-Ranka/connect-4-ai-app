// class GameState {
//   constructor(all_moves = null) {
//     this.all_moves = all_moves || [];
//     this.max_rows = 6;
//     this.max_columns = 7;
//   }

//   lastMovePlayedBy() {
//     return this.all_moves.length % 2 === 0 ? 2 : 1;
//   }

//   getLastMove() {
//     return this.all_moves[this.all_moves.length - 1][1];
//   }

//   getId() {
//     return JSON.stringify(this.all_moves.map((el) => el[1]));
//   }

//   getInfoFromId(id) {}

//   getNextMoveState(column) {
//     if (column >= this.max_columns || this.isGameOver() !== null) {
//       return null;
//     }
//     const row = Math.max(
//       ...this.all_moves
//         .filter((move) => move[1] === column)
//         .map((move) => move[0]),
//     );

//     if (row + 1 < this.max_rows) {
//       // Do a shallow copy. We do not expect to change already-occured moves
//       const new_moves = [...this.all_moves];
//       const new_row = row === -Infinity ? 0 : row + 1;
//       new_moves.push([new_row, column]);
//       return new GameState(new_moves);
//     } else {
//       return null;
//     }
//   }
//   getPreviousMoveState() {
//     const new_moves = this.all_moves.slice(0, -1);

//     return new GameState(new_moves);
//   }

//   getChildIds() {
//     const children_ids = this.getChildStates().map((state) => state.getId());

//     return children_ids;
//   }

//   getChildStates() {
//     const children = [];
//     for (let col = 0; col < this.max_columns; col++) {
//       const child = this.getNextMoveState(col);
//       if (child !== null) {
//         children.push(child);
//       }
//     }

//     return children;
//   }

//   getParentId() {
//     const parent = this.getParentState();
//     const parent_id = parent === null ? null : parent.getId();

//     return parent_id;
//   }

//   getParentState() {
//     const parent = this.getPreviousMoveState();

//     return parent;
//   }

//   isGameOver() {
//     const player1_moves = this.all_moves.filter((mov, ind) => ind % 2 === 0);
//     const player2_moves = this.all_moves.filter((mov, ind) => ind % 2 === 1);

//     const player1_runs = [
//       this.check4RunVertical(player1_moves),
//       this.check4RunHorizontal(player1_moves),
//       this.check4RunLeftDiagonal(player1_moves),
//       this.check4RunRightDiagonal(player1_moves),
//     ];

//     const player2_runs = [
//       this.check4RunVertical(player2_moves),
//       this.check4RunHorizontal(player2_moves),
//       this.check4RunLeftDiagonal(player2_moves),
//       this.check4RunRightDiagonal(player2_moves),
//     ];

//     const player1_max_run_length = Math.max(
//       ...player1_runs.map((run) => run.length),
//     );
//     const player2_max_run_length = Math.max(
//       ...player2_runs.map((run) => run.length),
//     );

//     if (player1_max_run_length >= 4) {
//       return {
//         winner: 1,
//         runs: player1_runs.filter(
//           (run) => run.length === player1_max_run_length,
//         ),
//       };
//     } else if (player2_max_run_length >= 4) {
//       return {
//         winner: 2,
//         runs: player2_runs.filter(
//           (run) => run.length === player2_max_run_length,
//         ),
//       };
//     } else if (this.all_moves.length === this.max_columns * this.max_rows) {
//       return { winner: null, runs: null };
//     } else {
//       return null;
//     }
//     // if
//   }

//   check4RunVertical(moves) {
//     function compareFunc(a, b) {
//       if (a[1] !== b[1]) {
//         return a[1] - b[1];
//       } else {
//         return a[0] - b[0];
//       }
//     }
//     const sorted_moves = moves.sort(compareFunc);

//     let current_run = [sorted_moves[0]],
//       max_run = [];
//     for (let i = 1; i < sorted_moves.length; i++) {
//       if (
//         sorted_moves[i][1] === sorted_moves[i - 1][1] &&
//         sorted_moves[i][0] === sorted_moves[i - 1][0] + 1
//       ) {
//         current_run.push(sorted_moves[i]);
//       } else {
//         max_run = current_run.length > max_run.length ? current_run : max_run;
//         current_run = [sorted_moves[i]];
//       }
//     }
//     max_run = current_run.length > max_run.length ? current_run : max_run;

//     return max_run;
//   }

//   check4RunHorizontal(moves) {
//     function compareFunc(a, b) {
//       if (a[0] !== b[0]) {
//         return a[0] - b[0];
//       } else {
//         return a[1] - b[1];
//       }
//     }
//     const sorted_moves = moves.sort(compareFunc);

//     let current_run = [sorted_moves[0]],
//       max_run = [];
//     for (let i = 1; i < sorted_moves.length; i++) {
//       if (
//         sorted_moves[i][0] === sorted_moves[i - 1][0] &&
//         sorted_moves[i][1] === sorted_moves[i - 1][1] + 1
//       ) {
//         current_run.push(sorted_moves[i]);
//       } else {
//         max_run = current_run.length > max_run.length ? current_run : max_run;
//         current_run = [sorted_moves[i]];
//       }
//     }
//     max_run = current_run.length > max_run.length ? current_run : max_run;

//     return max_run;
//   }

//   // Top left to bottom right
//   check4RunLeftDiagonal(moves) {
//     function compareFunc(a, b) {
//       if (a[0] + a[1] !== b[0] + b[1]) {
//         return a[0] + a[1] - b[0] + b[1];
//       } else {
//         return a[0] - b[0];
//       }
//     }
//     const sorted_moves = moves.sort(compareFunc);

//     let current_run = [sorted_moves[0]],
//       max_run = [];
//     for (let i = 1; i < sorted_moves.length; i++) {
//       if (
//         sorted_moves[i][0] + sorted_moves[i][1] ===
//           sorted_moves[i - 1][0] + sorted_moves[i - 1][1] &&
//         sorted_moves[i][0] === sorted_moves[i - 1][0] + 1
//       ) {
//         current_run.push(sorted_moves[i]);
//       } else {
//         max_run = current_run.length > max_run.length ? current_run : max_run;
//         current_run = [sorted_moves[i]];
//       }
//     }
//     max_run = current_run.length > max_run.length ? current_run : max_run;

//     return max_run;
//   }

//   check4RunRightDiagonal(moves) {
//     function compareFunc(a, b) {
//       if (a[0] - a[1] !== b[0] - b[1]) {
//         return a[0] - a[1] - (b[0] - b[1]);
//       } else {
//         return a[0] - b[0];
//       }
//     }
//     const sorted_moves = moves.sort(compareFunc);

//     let current_run = [sorted_moves[0]],
//       max_run = [];
//     for (let i = 1; i < sorted_moves.length; i++) {
//       if (
//         sorted_moves[i][0] - sorted_moves[i][1] ===
//           sorted_moves[i - 1][0] - sorted_moves[i - 1][1] &&
//         sorted_moves[i][0] === sorted_moves[i - 1][0] + 1
//       ) {
//         current_run.push(sorted_moves[i]);
//       } else {
//         max_run = current_run.length > max_run.length ? current_run : max_run;
//         current_run = [sorted_moves[i]];
//       }
//     }
//     max_run = current_run.length > max_run.length ? current_run : max_run;

//     return max_run;
//   }
// }

import { GameState } from "./GameState";

function randomChoice(arr) {
  return arr[Math.floor(arr.length * Math.random())];
}

function roundNDecimals(num, n) {
  return Math.round(num * Math.pow(10, n)) / Math.pow(10, n);
}

class GameStateMCTSWithUCT extends GameState {
  constructor(max_rows, max_columns, all_moves = null) {
    super(max_rows, max_columns, all_moves);
    this.wins = 0;
    this.plays = 0;
  }

  getNextMoveState(column) {
    const next_move_game_state = super.getNextMoveState(column);
    if (next_move_game_state !== null) {
      return new GameStateMCTSWithUCT(
        this.max_rows,
        this.max_columns,
        next_move_game_state.all_moves,
      );
    } else {
      return null;
    }
  }

  getPreviousMoveState() {
    const prev_move_state = super.getPreviousMoveState();

    return new GameStateMCTSWithUCT(
      this.max_rows,
      this.max_columns,
      prev_move_state.all_moves,
    );
  }
}

class MCTSWithUCTPlayerWorker {
  constructor(num_playouts, player_num) {
    this.states_known = new Map();
    this.current_state = null;
    this.uct_c_coeff = 2;
    this.num_playouts = num_playouts;
    this.num_playouts_per_chunk = 100;
    this.num_playouts_performed = 0;
    this.player_num = player_num;
  }

  async getCurrentStateWinChance(current_state) {
    // console.log("getCurrentStateWinChance : Current state", current_state);
    this.updateCurrentState(current_state);
    this.num_playouts_performed = 0;
    await this.performPlayouts();
    const win_chance = this.getUCTScoreForState(this.current_state, 0);
    // console.log("Win chance for move chosen=", win_chance * 100);

    return {
      win_chance: win_chance,
    };
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async getMoveAsync(current_state) {
    // await this.sleep(2 * 1000);
    this.forgetUnrequiredStates();
    this.updateCurrentState(current_state);
    // console.log("getMoveAsync : Current state", current_state);
    // const win_chance = this.getUCTScoreForState(this.current_state, 0);
    // console.log("Win chance for move chosen=", win_chance * 100);
    this.num_playouts_performed = 0;
    await this.performPlayouts();
    const target_state = this.chooseBestChild(this.current_state, 0);
    // this.getChildStatistics(this.current_state);

    // console.log("Number of states known", this.states_known.size);
    return {
      move: target_state.getLastMove()[1],
      // estimated_evaluations_tree_data: estimated_evaluations_tree_data,
      win_chance: this.getUCTScoreForState(target_state, 0),
    };
  }

  async performPlayouts(resolveCallback) {
    // console.log("Scheduling new playout chunk for", this.num_playouts);
    const final_playouts_when_chunk_ends = Math.min(
      this.num_playouts,
      this.num_playouts_performed + this.num_playouts_per_chunk,
    );
    while (this.num_playouts_performed < final_playouts_when_chunk_ends) {
      this.allMCTSSteps();
      this.num_playouts_performed += 1;
      // console.log("Number of playouts performed", this.num_playouts_performed);
    }

    if (this.num_playouts_performed < this.num_playouts) {
      if (resolveCallback) {
        // console.log("Case1");
        setTimeout(() => this.performPlayouts(resolveCallback), 0);
      } else {
        // console.log("Case2");
        return new Promise((resolve) => this.performPlayouts(resolve));
      }
    } else {
      if (resolveCallback) {
        // console.log("Case3");
        resolveCallback();
      } else {
        return;
      }
    }
  }

  forgetUnrequiredStates() {
    this.states_known.clear();
  }

  getMove(current_state) {
    this.updateCurrentState(current_state);
    for (let sim = 0; sim < this.num_playouts; sim++) {
      this.allMCTSSteps();
      // console.log("Number of known states", this.states_known.size);
    }
    const target_state = this.chooseBestChild(this.current_state, 0);
    // this.updateCurrentState(target_state);
    // const estimated_evaluations_tree_data = this.getEstimatedEvaluationsTree();

    return {
      move: target_state.getLastMove()[1],
      // estimated_evaluations_tree_data: estimated_evaluations_tree_data,
    };
  }

  getChildStatistics(state) {
    // Retrieve the children of the current state from this.states_known.
    // We will choose the best child (as currently estimated using UCT scores)
    const children = this.getChildKnownStates(state);

    const all_child_plays = children.map((child_state) => child_state.plays);
    const all_child_wins = children.map((child_state) => child_state.wins);

    // Get the best UCT scores out of all the children
    const all_child_scores = children.map((child_state) =>
      this.getUCTScoreForState(child_state, 0),
    );
    // console.log(this.player_num);
    // console.log(all_child_wins);
    // console.log(all_child_plays);
    // console.log(all_child_scores.map((num) => roundNDecimals(num, 2)));
    // console.log();
  }

  getEstimatedEvaluationsTree() {
    // console.log("In estimated evaluations tree");
    // console.log("Current state", this.current_state);
    // console.log()
    const depth = 4;
    let key = 0;
    const nodes = [
        {
          key: key,
          value: this.getUCTScoreForState(this.current_state, 0),
        },
      ],
      parents = [],
      parent_key_and_states = this.getChildKnownStates(this.current_state).map(
        (state) => [0, state],
      );

    key += 1;
    // console.log(JSON.stringify(parent_key_and_states));

    while (
      parent_key_and_states.length > 0 &&
      parent_key_and_states[0][1].all_moves.length -
        this.current_state.all_moves.length <=
        depth
    ) {
      const [parent_key, state] = parent_key_and_states.shift();
      nodes.push({
        key: key,
        value: this.getUCTScoreForState(state, 0),
      });
      parents.push([key, parent_key]);
      this.getChildKnownStates(state).forEach((child_state) => {
        // console.log(JSON.stringify(child_state));
        parent_key_and_states.push([key, child_state]);
      });
      key += 1;
    }

    return { node_data: nodes, parent_data: parents, root_key: 0 };
  }

  updateCurrentState(state) {
    if (!this.states_known.has(state.getId())) {
      // console.log("updateCurrentState : State not known, creating new state");
      const new_game_state = new GameStateMCTSWithUCT(
        state.max_rows,
        state.max_columns,
        state.all_moves,
      );
      this.states_known.set(new_game_state.getId(), new_game_state);
      this.current_state = new_game_state;
    } else {
      this.current_state = this.states_known.get(state.getId());
    }
  }

  getParentKnownState(state) {
    const parent_id = state.getParentId();
    const parent_known_state =
      parent_id === null ? null : this.states_known.get(parent_id);

    return parent_known_state;
  }

  getChildKnownStates(state) {
    const child_known_states = [];
    state.getChildIds().forEach((child_id) => {
      const child_state = this.states_known.get(child_id);
      if (child_state) {
        child_known_states.push(child_state);
      }
    });

    return child_known_states;
  }

  getUCTScoreForState(state, uct_c_coeff) {
    if (state.plays === 0) {
      return Number.POSITIVE_INFINITY;
    } else {
      // Should never come here if parent is not null
      const exploitation_factor = state.wins / state.plays;
      const parent = this.getParentKnownState(state);
      const exploration_factor =
        uct_c_coeff * Math.sqrt(Math.log(parent.plays) / state.plays);

      // console.log("mcts_state; getUCTScore:", exploitation_factor + exploration_factor)
      return exploitation_factor + exploration_factor;
    }
  }
  allMCTSSteps() {
    const leaf_state = this.selectionStep();
    const chosen_child = this.expansionStep(leaf_state);
    const game_decision = this.simulationStep(chosen_child);
    this.backpropagationStep(chosen_child, game_decision);
  }

  selectionStep() {
    // Set up. We should continue the selection step until we reach a "leaf" Node.
    // i.e. a node/state whose children are not yet known or do not exist (game over)
    let selection_state = this.current_state;
    let test_child_id = selection_state.getChildIds()[0];
    let is_not_leaf =
      test_child_id !== undefined && this.states_known.has(test_child_id);

    while (is_not_leaf) {
      selection_state = this.chooseBestChild(selection_state, this.uct_c_coeff);

      // Get information about whether this new state is a leaf of not
      test_child_id = selection_state.getChildIds()[0];
      is_not_leaf =
        test_child_id !== undefined && this.states_known.has(test_child_id);
    }

    const leaf_state = selection_state;

    return leaf_state;
  }

  chooseBestChild(state, uct_c_coeff) {
    // Retrieve the children of the current state from this.states_known.
    // We will choose the best child (as currently estimated using UCT scores)
    const children = this.getChildKnownStates(state);

    // Get the best UCT scores out of all the children
    const all_child_scores = children.map((child_state) =>
      this.getUCTScoreForState(child_state, uct_c_coeff),
    );
    // if (uct_c_coeff === 0) {
    //   console.log(all_child_scores);
    // }
    const best_child_score = Math.max(...all_child_scores);

    // Get all best children of the current state
    const best_children = children.filter(
      (child_state) =>
        this.getUCTScoreForState(child_state, uct_c_coeff) === best_child_score,
    );

    // Choose one of the best children. We will go down this route to explore more
    const best_child = randomChoice(best_children);

    return best_child;
  }

  expansionStep(leaf_state) {
    // Expansion consists of adding children of the leaf state (if it exists) to the known states.
    // It is worth exploring these states, since we reached them using the best choices till now
    const children = leaf_state.getChildStates();

    children.forEach((state) => {
      this.states_known.set(state.getId(), state);
    });

    // Choose among the children randomly for the simulation step. This child will be the 'parent' state of the
    // uninformed exploration i.e from hereon, there is only random selection of states
    const chosen_child = randomChoice(children);
    const chosen_state = chosen_child === undefined ? leaf_state : chosen_child;
    return chosen_state;
  }

  simulationStep(state) {
    // Simulate moves till we reach a Game over state
    // Its okay to use non-mcts states here since we will not be needing their uct scores anyway
    // Returns the outcome of the gameover stage (win - for which player  or draw)
    let temp_state = state;
    while (temp_state.isGameOver() === null) {
      const child_states = temp_state.getChildStates();
      temp_state = randomChoice(child_states);
    }

    return temp_state.isGameOver();
  }

  backpropagationStep(last_known_state, game_decision) {
    let backprop_state = last_known_state;
    while (true) {
      const player = backprop_state.lastMovePlayedBy();
      if (game_decision.winner === player) {
        backprop_state.wins += 1;
      } else if (game_decision.winner === null) {
        backprop_state.wins += 0.5;
      }
      backprop_state.plays += 1;

      if (backprop_state === this.current_state) {
        break;
      }

      backprop_state = this.states_known.get(
        backprop_state.getParentState().getId(),
      );
    }
  }
}

export { MCTSWithUCTPlayerWorker };

// // gs = new GameStateMCTSWithUCT();
// // console.log(gs);
// const moves = [
//   2, 3, 3, 2, 3, 3, 2, 6, 5, 2, 5, 5, 6, 5, 5, 0, 5, 6, 6, 0, 1, 0, 0, 3, 3, 2,
//   2, 0, 0, 1, 1, 6, 4, 1, 6,
//   //4, // 1,
// ];
// gs = new GameState();

// // for (let i = 0; i < moves.length; i++) {
// //   //   console.log(i);
// //   gs = gs.getNextMoveState(moves[i]);
// // }

// mcts_player = new MCTSWithUCTPlayerWorker(5000);
// const [state_info, target_state] = mcts_player.getMove(gs);
// console.log("Done");
