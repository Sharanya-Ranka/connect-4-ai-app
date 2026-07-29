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
    this.forgetUnrequiredStates(this.current_state);
    this.num_playouts_performed = 0;
    await this.performPlayouts();
    console.log("Monitor current state", this.current_state)
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
    this.updateCurrentState(current_state);
    this.forgetUnrequiredStates(this.current_state);
    // console.log("getMoveAsync : Current state", current_state);
    // const win_chance = this.getUCTScoreForState(this.current_state, 0);
    // console.log("Win chance for move chosen=", win_chance * 100);
    this.num_playouts_performed = 0;
    await this.performPlayouts();
    // console.log("Current state", this.current_state);
    const target_state = this.chooseBestChild(this.current_state, 0);
    // console.log("Target state:", target_state);
    // this.getChildStatistics(this.current_state);

    // console.log("Number of states known", this.states_known.size);
    return {
      move: target_state.getLastMove()[1],
      // estimated_evaluations_tree_data: estimated_evaluations_tree_data,
      win_chance: this.getUCTScoreForState(target_state, 0),
    };
  }

  async performPlayouts(resolveCallback) {
    console.log("Scheduling new playout chunk for", this.num_playouts);
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

  forgetUnrequiredStates(current_state) {
    // Forget states that are not descendants of (or equal to) current state
    let num_deletions = 0;
    for (const [state_id, state] of this.states_known) {
      if (!current_state.isAncestorOf(state)) {
        this.states_known.delete(state_id);
        num_deletions += 1;
      }
    }

    console.log("Deleted %d states", num_deletions);
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
      let exploration_factor = 0;
      if(uct_c_coeff !== 0){
        const parent = this.getParentKnownState(state);
        exploration_factor =
          uct_c_coeff * Math.sqrt(Math.log(parent.plays) / state.plays);
      }

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
    // console.log("Children", children);

    // Get the best UCT scores out of all the children
    const all_child_scores = children.map((child_state) =>
      this.getUCTScoreForState(child_state, uct_c_coeff),
    );
    // console.log("All child scores", all_child_scores);
    // if (uct_c_coeff === 0) {
    //   console.log(all_child_scores);
    // }
    const best_child_score = Math.max(...all_child_scores);
    // console.log("Best child score", best_child_score);

    // Get all best children of the current state
    const best_children = children.filter(
      (child_state) =>
        this.getUCTScoreForState(child_state, uct_c_coeff) === best_child_score,
    );
    // console.log("Best children", best_children);

    // Choose one of the best children. We will go down this route to explore more
    const best_child = randomChoice(best_children);
    // console.log("Best child", best_child);

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
