class GameState {
  constructor(max_rows, max_columns, all_moves = null) {
    this.all_moves = all_moves || [];
    this.max_rows = max_rows;
    this.max_columns = max_columns;
  }

  lastMovePlayedBy() {
    return this.all_moves.length % 2 === 0 ? 2 : 1;
  }

  getLastMove() {
    return this.all_moves[this.all_moves.length - 1];
  }

  getId() {
    return JSON.stringify(this.all_moves.map((el) => el[1]));
  }

  getInfoFromId(id) {}

  getNextMoveState(column) {
    if (
      column === null ||
      column >= this.max_columns ||
      this.isGameOver() !== null
    ) {
      return null;
    }
    const row = Math.max(
      ...this.all_moves
        .filter((move) => move[1] === column)
        .map((move) => move[0]),
    );

    if (row + 1 < this.max_rows) {
      // Do a shallow copy. We do not expect to change already-occured moves
      const new_moves = [...this.all_moves];
      const new_row = row === -Infinity ? 0 : row + 1;
      new_moves.push([new_row, column]);
      return new GameState(this.max_rows, this.max_columns, new_moves);
    } else {
      return null;
    }
  }
  getPreviousMoveState() {
    const new_moves = this.all_moves.slice(0, -1);

    return new GameState(this.max_rows, this.max_columns, new_moves);
  }

  getChildIds() {
    const children_ids = this.getChildStates().map((state) => state.getId());

    return children_ids;
  }

  getChildStates() {
    const children = [];
    for (let col = 0; col < this.max_columns; col++) {
      const child = this.getNextMoveState(col);
      if (child != null) {
        children.push(child);
      }
    }

    return children;
  }

  getParentId() {
    const parent = this.getParentState();
    const parent_id = parent === null ? null : parent.getId();

    return parent_id;
  }

  getParentState() {
    const parent = this.getPreviousMoveState();

    return parent;
  }

  isGameOver() {
    const player1_moves = this.all_moves.filter((mov, ind) => ind % 2 === 0);
    const player2_moves = this.all_moves.filter((mov, ind) => ind % 2 === 1);

    const player1_runs = [
      this.check4RunVertical(player1_moves),
      this.check4RunHorizontal(player1_moves),
      this.check4RunLeftDiagonal(player1_moves),
      this.check4RunRightDiagonal(player1_moves),
    ];

    const player2_runs = [
      this.check4RunVertical(player2_moves),
      this.check4RunHorizontal(player2_moves),
      this.check4RunLeftDiagonal(player2_moves),
      this.check4RunRightDiagonal(player2_moves),
    ];

    const player1_max_run_length = Math.max(
      ...player1_runs.map((run) => run.length),
    );
    const player2_max_run_length = Math.max(
      ...player2_runs.map((run) => run.length),
    );

    if (player1_max_run_length >= 4) {
      return {
        winner: 1,
        runs: player1_runs.filter(
          (run) => run.length === player1_max_run_length,
        ),
      };
    } else if (player2_max_run_length >= 4) {
      return {
        winner: 2,
        runs: player2_runs.filter(
          (run) => run.length === player2_max_run_length,
        ),
      };
    } else if (this.all_moves.length === this.max_columns * this.max_rows) {
      return { winner: null, runs: [] };
    } else {
      return null;
    }
    // if
  }

  check4RunVertical(moves) {
    function compareFunc(a, b) {
      if (a[1] !== b[1]) {
        return a[1] - b[1];
      } else {
        return a[0] - b[0];
      }
    }
    const sorted_moves = moves.sort(compareFunc);

    let current_run = [sorted_moves[0]],
      max_run = [];
    for (let i = 1; i < sorted_moves.length; i++) {
      if (
        sorted_moves[i][1] === sorted_moves[i - 1][1] &&
        sorted_moves[i][0] === sorted_moves[i - 1][0] + 1
      ) {
        current_run.push(sorted_moves[i]);
      } else {
        max_run = current_run.length > max_run.length ? current_run : max_run;
        current_run = [sorted_moves[i]];
      }
    }
    max_run = current_run.length > max_run.length ? current_run : max_run;

    return max_run;
  }

  check4RunHorizontal(moves) {
    function compareFunc(a, b) {
      if (a[0] !== b[0]) {
        return a[0] - b[0];
      } else {
        return a[1] - b[1];
      }
    }
    const sorted_moves = moves.sort(compareFunc);

    let current_run = [sorted_moves[0]],
      max_run = [];
    for (let i = 1; i < sorted_moves.length; i++) {
      if (
        sorted_moves[i][0] === sorted_moves[i - 1][0] &&
        sorted_moves[i][1] === sorted_moves[i - 1][1] + 1
      ) {
        current_run.push(sorted_moves[i]);
      } else {
        max_run = current_run.length > max_run.length ? current_run : max_run;
        current_run = [sorted_moves[i]];
      }
    }
    max_run = current_run.length > max_run.length ? current_run : max_run;

    return max_run;
  }

  // Top left to bottom right
  check4RunLeftDiagonal(moves) {
    function compareFunc(a, b) {
      if (a[0] + a[1] !== b[0] + b[1]) {
        return a[0] + a[1] - (b[0] + b[1]);
      } else {
        return a[0] - b[0];
      }
    }
    const sorted_moves = moves.sort(compareFunc);

    let current_run = [sorted_moves[0]],
      max_run = [];
    for (let i = 1; i < sorted_moves.length; i++) {
      if (
        sorted_moves[i][0] + sorted_moves[i][1] ===
          sorted_moves[i - 1][0] + sorted_moves[i - 1][1] &&
        sorted_moves[i][0] === sorted_moves[i - 1][0] + 1
      ) {
        current_run.push(sorted_moves[i]);
      } else {
        max_run = current_run.length > max_run.length ? current_run : max_run;
        current_run = [sorted_moves[i]];
      }
    }
    max_run = current_run.length > max_run.length ? current_run : max_run;

    return max_run;
  }

  check4RunRightDiagonal(moves) {
    function compareFunc(a, b) {
      if (a[0] - a[1] !== b[0] - b[1]) {
        return a[0] - a[1] - (b[0] - b[1]);
      } else {
        return a[0] - b[0];
      }
    }
    const sorted_moves = moves.sort(compareFunc);

    let current_run = [sorted_moves[0]],
      max_run = [];
    for (let i = 1; i < sorted_moves.length; i++) {
      if (
        sorted_moves[i][0] - sorted_moves[i][1] ===
          sorted_moves[i - 1][0] - sorted_moves[i - 1][1] &&
        sorted_moves[i][0] === sorted_moves[i - 1][0] + 1
      ) {
        current_run.push(sorted_moves[i]);
      } else {
        max_run = current_run.length > max_run.length ? current_run : max_run;
        current_run = [sorted_moves[i]];
      }
    }
    max_run = current_run.length > max_run.length ? current_run : max_run;

    return max_run;
  }
}
export { GameState };

// moves = [1, 0, 2, 0, 3, 0, 4, 0];
// moves = [3, 3, 2, 1, 5, 4, 2, 2, 3, 3, 1, 0, 5, 5, 1, 1];
// // Game that ends with player1 winning 5 horizontal after 31 plies
// moves = [
//   1, 3, 2, 3, 3, 2, 4, 0, 1, 1, 2, 1, 4, 2, 4, 4, 3, 4, 3, 3, 2, 0, 1, 1, 2, 6,
//   5, 6, 6, 5, 5,
// ];

// // Game that ends in player 1 winning (horizontal 4) at ply 37
// moves = [
//   2, 3, 3, 2, 3, 3, 2, 6, 5, 2, 5, 5, 6, 5, 5, 0, 5, 6, 6, 0, 1, 0, 0, 3, 3, 2,
//   2, 0, 0, 1, 1, 6, 4, 1, 1, 4, 1,
// ];

// // Player 2 wins, horizontal 4 ply 24
// moves = [
//   2, 5, 5, 1, 6, 2, 1, 2, 5, 2, 2, 5, 0, 0, 0, 1, 3, 3, 1, 3, 5, 4, 4, 4,
// ];

// // Draw
// moves = [
//   2, 2, 3, 4, 3, 3, 2, 1, 2, 3, 2, 3, 1, 4, 0, 5, 0, 0, 5, 1, 1, 1, 5, 5, 0, 0,
//   5, 4, 4, 4, 3, 2, 1, 0, 5, 4, 6, 6, 6, 6, 6, 6,
// ];

// let gs = new GameState();

// for (let i = 0; i < moves.length; i++) {
//   //   console.log(i);
//   gs = gs.getNextMoveState(moves[i]);
// }
// console.log(gs);
// console.dir(gs.isGameOver(), { depth: null });
// console.dir();
// // console.log(gs.getChildStates()[0]);
// // console.log(gs.getId());
// // console.log(gs.getNextMoveState(1).getId());
