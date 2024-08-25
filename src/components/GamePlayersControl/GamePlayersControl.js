import React from "react";
import {
  getGameStateDescriptionFromGameStateObject,
  getGameStateObjectFromGameStateDescription,
} from "../../scripts/utilities";

export default function GamePlayersControl({
  game_state,
  players,
  setGameState,
  setWinChance,
}) {
  // console.log("GamePlayersControl: GameState", game_state);
  // Commit move communicated by the player. This is called only from the effect below (which queries the players for moves)
  // Changes state of the game-board and active player index on committing the move
  const game_state_obj = getGameStateObjectFromGameStateDescription(game_state);

  function commitMove(player_number, move) {
    // const game_state = game_state.getNextMoveState(move);
    // console.log("Org state:", game_state_obj);
    const next_game_state_obj = game_state_obj.getNextMoveState(move);

    var next_game_state_slice =
      getGameStateDescriptionFromGameStateObject(next_game_state_obj);
    next_game_state_slice.active_player_ind = 3 - game_state.active_player_ind;
    // console.log("Committing move");
    setGameState((prev_game_state) => ({
      ...prev_game_state,
      ...next_game_state_slice,
    }));
    // console.log(`Will change active player from ${active_player_ind}`);
  }
  //  Check if the move provided by the player is Valid. Only then shall we commit the move
  function isValidMove(player_ind, move) {
    return move != null && game_state_obj.getNextMoveState(move) !== null
      ? true
      : false;
  }

  // Runs each time the active player is changed. Requests for a valid move from the player periodically
  React.useEffect(() => {
    async function playerMoveWorkflow() {
      // console.log(`Setting player ${active_player_ind} as active`);
      async function requestMonitorForMoveUpdate() {
        const monitor = players.monitor;
        if (monitor === null) {
          return;
        }

        setWinChance((prev_state) => ({
          ...prev_state,
          calculation_ongoing: true,
        }));
        const monitor_player_update =
          await monitor.getMoveUpdate(game_state_obj);

        setWinChance({
          player_ind: 3 - game_state.active_player_ind,
          win_chance: monitor_player_update.win_chance,
          calculation_ongoing: false,
        });
      }
      async function requestPlayerForMoveUpdate() {
        // console.log(`Getting move from player ${game_state.active_player_ind}`);
        // console.log("Current game state", game_state);
        const active_player =
          game_state.active_player_ind === 1
            ? players.player1
            : players.player2;

        const update = await active_player.getMoveUpdate(game_state_obj);
        const move = update.move;
        // console.log("Move is", move);
        if (isValidMove(game_state.active_player_ind, move)) {
          if (effect_is_active) {
            // console.log(
            //   `Committing move from player ${game_state.active_player_ind}`,
            // );
            commitMove(game_state.active_player_ind, move);
          }
        } else {
          setTimeout(requestPlayerForMoveUpdate, 500);
        }
      }

      function canProceed1() {
        return game_state.is_game_active;
      }
      function canProceed2() {
        return !game_state_obj.isGameOver() && game_state.paused === false;
      }
      // console.log("CanProceed", canProceed1(), canProceed2());
      if (canProceed1()) {
        await requestMonitorForMoveUpdate();
        if (canProceed2()) {
          await requestPlayerForMoveUpdate();
        }
      }
    }
    // console.log("GamePlayersControl: Triggering workflow");
    let effect_is_active = true;
    playerMoveWorkflow();

    return () => {
      console.log("Cleanup useEffect");
      effect_is_active = false;
    };
  }, [
    game_state.is_game_active,
    game_state.active_player_ind,
    game_state.paused,
  ]);

  // Communicates board clicks to players who communicate their moves through clicks (Human players)
  React.useEffect(() => {
    // console.log("In column clicked");
    function canProceed() {
      return game_state.is_game_active;
    }

    const active_player =
      game_state.active_player_ind === 1 ? players.player1 : players.player2;
    if (
      game_state.ui_state.column_clicked !== null &&
      canProceed() &&
      active_player.communicatesMoveThroughClick()
    ) {
      // console.log("Column clicked", game_state.ui_state.column_clicked);
      active_player.communicateColumnClicked(
        game_state.ui_state.column_clicked,
      );
    }
    setGameState((prev_state) => ({
      ...prev_state,
      ui_state: { ...prev_state.ui_state, column_clicked: null },
    }));
  }, [game_state.ui_state.column_clicked]);

  return <></>;
}
