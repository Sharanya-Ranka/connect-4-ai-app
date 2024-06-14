import GameBoard from "./GameBoard";
import { HumanPlayer, RandomValidMovePlayer } from "../../scripts/Player";

export default function GameBoardMain() {
  let game_board_state = Array.from({ length: 6 }).map((el, ind) =>
    Array.from({ length: 7 }).fill(0),
  );
  game_board_state[0][1] = 1;
  game_board_state[0][2] = 2;
  // console.log(game_board_state);
  // Maintain 2 players, alternate betweeen them when one makes a move
  // Allow a player to make a move
  // Allow the GameBoard to communicate a click
  function onGameBoardClicked(column) {}

  return (
    <div className="game-board-main">
      <GameBoard game_board_state={game_board_state} />
    </div>
  );
}
