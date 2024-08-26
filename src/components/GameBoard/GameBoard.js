import GameBoardTile from "./GameBoardTile";
import "../../styles/GameBoardStyles/GameBoard.css";
import { getGameStateObjectFromGameStateDescription } from "../../scripts/utilities";

export default function GameBoard({ game_state, setGameState }) {
  // console.log("GameBoard: GameState", game_state);

  function handleGameBoardClick(col) {
    setGameState((prev_state) => ({
      ...prev_state,
      ui_state: { ...prev_state.ui_state, column_clicked: col },
    }));
  }

  function handleColumnMouseEnter(col) {
    setGameState((prev_state) => ({
      ...prev_state,
      ui_state: { ...prev_state.ui_state, column_hover: col },
    }));
  }

  function handleColumnMouseLeave() {
    setGameState((prev_state) => ({
      ...prev_state,
      ui_state: { ...prev_state.ui_state, column_hover: null },
    }));
  }
  const game_state_obj = getGameStateObjectFromGameStateDescription(game_state);
  // console.log(game_state);
  let hover_show_tile = null,
    hover_parity = 0;
  if (game_state.ui_state.column_hover !== null) {
    const next_state_obj = game_state_obj.getNextMoveState(
      game_state.ui_state.column_hover,
    );

    if (next_state_obj !== null) {
      const highlighted_move = next_state_obj.getLastMove();
      hover_show_tile = highlighted_move;
      hover_parity = next_state_obj.lastMovePlayedBy();
      // console.log("Hover", hover_show_tile, hover_parity);
    }
  }

  function getValueForTile(row_ind, col_ind) {
    // Provides the tile configuration info for each tile given its position in the game board.
    // This ultimately decides the way each tile will look
    let parity = 0,
      in_winning_run = false,
      tile_opacity = "full",
      move_num = -1;

    if (
      hover_show_tile !== null &&
      hover_show_tile[0] == row_ind &&
      hover_show_tile[1] == col_ind
    ) {
      tile_opacity = "partial";
      parity = hover_parity;
    }
    // console.log("Game State", game_state);
    game_state.all_moves.forEach(([row, col], move_ind) => {
      if (row === row_ind && col === col_ind) {
        parity = move_ind % 2 === 0 ? 1 : 2;
        move_num = move_ind + 1;
      }
    });

    // if (game_state.ui_state.highlight_state !== null) {
    //   game_state.ui_state.highlight_state.all_moves.forEach(
    //     ([row, col], move_ind) => {
    //       if (row === row_ind && col === col_ind) {
    //         tile_opacity = "partial";
    //         parity = move_ind % 2 === 0 ? 1 : 2;
    //       }
    //     },
    //   );
    // }

    if (game_state_obj.isGameOver() !== null) {
      const runs = game_state_obj.isGameOver().runs;
      runs.forEach((run) =>
        run.forEach(([row, col]) => {
          if (row === row_ind && col === col_ind) {
            in_winning_run = true;
          }
        }),
      );
    }

    // Colour : Red/Yellow depending on the player who played the move
    // In_winning_run  : Black inner markings to highlight the winning 'run' of 4/more tokens
    // Move_num : Keep track of the order of moves
    return {
      parity: parity,
      in_winning_run: in_winning_run,
      tile_opacity: tile_opacity,
      move_num: move_num,
    };
  }
  // Just creates a grid of JSX elements representing individual tiles. Uses all state to determine how each tile should look
  const tile_grid_jsx = Array.from({ length: game_state.num_rows }).map(
    (_, row_ind) =>
      Array.from({ length: game_state.num_cols }).map((_, col_ind) => (
        <GameBoardTile {...getValueForTile(row_ind, col_ind)} />
      )),
  );

  // Creates columns from the grid defined before. We have specific behaviour for columns hence want to define it this way
  const game_board_columns_jsx = Array.from({
    length: game_state.num_cols,
  }).map((_, col_ind) => (
    <div
      className="game-board-column"
      onClick={() => handleGameBoardClick(col_ind)}
      onMouseEnter={() => handleColumnMouseEnter(col_ind)}
      onMouseLeave={() => handleColumnMouseLeave()}
    >
      {Array.from({ length: game_state.num_rows }).map(
        (_, row_ind) => tile_grid_jsx[row_ind][col_ind],
      )}
    </div>
  ));

  // Renders the game board. It is a series of columns that contain tiles within them
  return <div className="game-board">{game_board_columns_jsx}</div>;
}
