import GameBoard from "./GameBoard";
import { GameState } from "../../scripts/GameState";
import { Tree } from "../../scripts/GameTree";

import {
  HumanPlayer,
  MCTSWithUCTPlayer,
  RandomValidMovePlayer,
} from "../../scripts/Player";
import React from "react";
import TreeVisualizer from "../TreeVisualization/TreeVisualizer";

export default function GameCreator({
  game_config,
  game_state,
  players,
  active_player_ind,
  setGameState,
  setActivePlayerInd,
}) {
  // State: Tree
  // const [tree, changeTree] = React.useState(null);

  // Commit move communicated by the player. This is called only from the effect below (which queries the players for moves)
  // Changes state of the game-board and active player index on committing the move
  function commitMove(player_number, move) {
    const new_game_state = game_state.getNextMoveState(move);
    setGameState((prev_game_state) => new_game_state);
    // console.log(`Will change active player from ${active_player_ind}`);
    setActivePlayerInd((player_ind) => {
      // console.log("Setting new active player: Original", player_ind);
      // console.log("Setting new active player: New", 1 - player_ind);
      return 1 - player_number;
    });
  }
  //  Check if the move provided by the player is Valid. Only then shall we commit the move
  function isValidMove(player_ind, move) {
    return move != null && game_state.getNextMoveState(move) != null
      ? true
      : false;
  }

  // Runs each time the active player is changed. Requests for a valid move from the player periodically
  React.useEffect(() => {
    // console.log(`Setting player ${active_player_ind} as active`);

    async function requestPlayerForMoveUpdate() {
      players[active_player_ind].setActive();
      // console.log(`Getting move from player ${active_player_ind}`);
      // console.log("Current game state", game_state);
      const update = await players[active_player_ind].getMoveUpdate(game_state);
      const move = update.move;
      if (isValidMove(active_player_ind, move)) {
        // console.log(`Committing move from player ${active_player_ind}`);
        commitMove(active_player_ind, move);

        if (update.estimated_evaluations_tree_data != null) {
          // console.log(update.estimated_evaluations_tree_data);
          // changeTree(
          //   new Tree(
          //     update.estimated_evaluations_tree_data.node_data,
          //     update.estimated_evaluations_tree_data.parent_data,
          //     update.estimated_evaluations_tree_data.root_key,
          //   ),
          // );
        }
      } else {
        console.log(
          `Setting timeout to get move from player ${active_player_ind}`,
        );

        setTimeout(requestPlayerForMoveUpdate, 500);
      }
    }
    if (players.length == 2 && !game_state.isGameOver()) {
      requestPlayerForMoveUpdate();
    }
  }, [active_player_ind]);

  // Communicates board clicks to players who communicate their moves through clicks (Human players)
  function handleGameBoardClick(column) {
    // console.log("Column clicked", column);
    if (
      players.length == 2 &&
      players[active_player_ind].communicatesMoveThroughClick()
    ) {
      players[active_player_ind].communicateColumnClicked(column);
    }
  }

  return (
    <div className="game-board-main">
      <GameBoard
        game_state={game_state}
        handleGameBoardClick={handleGameBoardClick}
      />
      {/* {tree === null ? "" : <TreeVisualizer tree={tree} />} */}
    </div>
  );
}
