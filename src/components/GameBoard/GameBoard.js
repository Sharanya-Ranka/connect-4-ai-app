import GameBoardTile from "./GameBoardTile";
import "../../styles/GameBoardStyles/GameBoard.css";

export default function GameBoard({ game_state, handleGameBoardClick }) {
  function getValueForTile(row_ind, col_ind) {
    let player = 0,
      in_winning_run = false,
      move_num = 0;
    game_state.all_moves.forEach(([row, col], move_ind) => {
      if (row === row_ind && col === col_ind) {
        player = move_ind % 2 === 0 ? 1 : 2;
        move_num = move_ind;
      }
    });

    if (game_state.isGameOver() != null) {
      const runs = game_state.isGameOver().runs;
      runs.forEach((run) =>
        run.forEach(([row, col]) => {
          if (row === row_ind && col === col_ind) {
            in_winning_run = true;
          }
        }),
      );
    }
    // console.log("GameTile query", [row_ind, col_ind], {
    //   colour: player,
    //   in_winning_run: in_winning_run,
    // });
    return {
      colour: player,
      in_winning_run: in_winning_run,
      move_num: move_num,
    };
  }

  const tile_grid_jsx = Array.from({ length: game_state.max_rows }).map(
    (_, row_ind) =>
      Array.from({ length: game_state.max_columns }).map((_, col_ind) => (
        <GameBoardTile {...getValueForTile(row_ind, col_ind)} />
      )),
  );

  const game_board_columns_jsx = Array.from({
    length: game_state.max_columns,
  }).map((_, col_ind) => (
    <div
      className="game-board-column"
      onClick={() => handleGameBoardClick(col_ind)}
    >
      {Array.from({ length: game_state.max_rows }).map(
        (_, row_ind) => tile_grid_jsx[row_ind][col_ind],
      )}
    </div>
  ));

  return <div className="game-board">{game_board_columns_jsx}</div>;
}
