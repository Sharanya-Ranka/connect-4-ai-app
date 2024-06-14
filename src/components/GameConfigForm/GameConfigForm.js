import "../../styles/GameConfigFormStyles/GameConfigForm.css";
import { GameState } from "../../scripts/GameState";
import { MCTS_UCT_PLAYER, HUMAN_PLAYER } from "../../scripts/constants";
import React from "react";
import { HumanPlayer, MCTSWithUCTPlayer } from "../../scripts/Player";

export default function GameConfigForm({
  game_config,
  setGameConfig,
  setPlayers,
  setGameState,
  setActivePlayerInd,
}) {
  // Form change handlers
  function handleGameBoardChange(event) {
    const { name, value } = event.target;
    const prev_game_board = {
      num_rows: game_config.num_rows,
      num_cols: game_config.num_cols,
    };
    const new_game_board = { ...prev_game_board, [name]: value };
    console.log(name, value);
    setGameConfig((prev_state) => ({ ...prev_state, ...new_game_board }));

    setGameState(
      (prev_state) =>
        new GameState(new_game_board.num_rows, new_game_board.num_cols),
    );
  }

  function handlePlayerChange(player_num, event) {
    const { name, value } = event.target;
    console.log(name, value);
    const player_config =
      player_num === 1 ? game_config.player1 : game_config.player2;
    const new_player_config = { ...player_config, [name]: value };
    setGameConfig((prev_state) => ({
      ...prev_state,
      [player_num === 1 ? "player1" : "player2"]: new_player_config,
    }));
  }

  function handlePlayResetClicked(event) {
    console.log("Button clicked");
    setGameConfig((prev_state) => ({
      ...prev_state,
      is_game_active: !prev_state.is_game_active,
    }));
  }

  React.useEffect(() => {
    if (game_config.is_game_active) {
      performPlaySetup();
    } else {
      performReset();
    }
  }, [game_config.is_game_active]);

  function getPlayer(player_config) {
    if (player_config.type == HUMAN_PLAYER) {
      return new HumanPlayer(1);
    } else {
      const player_info = {
        player_num: 1,
        num_playouts: player_config.strength,
      };
      return new MCTSWithUCTPlayer(player_info);
    }
  }

  function performPlaySetup() {
    const players = [
      getPlayer(game_config.player1),
      getPlayer(game_config.player2),
    ];

    console.log("Setting players", players);
    console.log("Setting active player index", 0);

    setPlayers(players);
    setActivePlayerInd(0);
  }

  function performReset() {
    const players = [];
    setPlayers(players);
    setGameState(new GameState(game_config.num_rows, game_config.num_cols));
    setActivePlayerInd(-1);
  }

  const max_rows = 10,
    max_columns = 10;

  const mcts_agent_strengths = [50, 100, 500, 1000, 2000, 5000];

  const row_options = Array.from(
    Array.from({ length: max_rows + 1 }).map((_, ind) =>
      ind >= 4 ? <option value={ind}>{ind}</option> : "",
    ),
  );

  const column_options = Array.from(
    Array.from({ length: max_columns + 1 }).map((_, ind) =>
      ind >= 4 ? <option value={ind}>{ind}</option> : "",
    ),
  );

  const player_options = (
    <>
      <option value={MCTS_UCT_PLAYER}>{MCTS_UCT_PLAYER}</option>
      <option value={HUMAN_PLAYER}>{HUMAN_PLAYER}</option>
    </>
  );

  const strength_options = mcts_agent_strengths.map((val) => (
    <option value={val}>{val}</option>
  ));

  return (
    <div className="game-config-form">
      <div className="game-config-rows">
        {/* Num rows*/}
        <label for="num_rows">Number of rows</label>
        <select
          id="num_rows"
          name="num_rows"
          onChange={handleGameBoardChange}
          value={game_config.num_rows}
          disabled={game_config.is_game_active}
        >
          {row_options}
        </select>
      </div>
      <div className="game-config-columns">
        <label for="num_cols">Number of columns</label>
        <select
          id="num_cols"
          name="num_cols"
          onChange={handleGameBoardChange}
          value={game_config.num_cols}
          disabled={game_config.is_game_active}
        >
          {column_options}
        </select>
      </div>
      {/* Player types */}
      <div className="game-config-player1">
        <label for="player1">Player 1: Type</label>
        <select
          id="player1"
          name="type"
          onChange={(event) => handlePlayerChange(1, event)}
          value={game_config.player1.type}
          disabled={game_config.is_game_active}
        >
          {player_options}
        </select>
        {game_config.player1.type === MCTS_UCT_PLAYER ? (
          <>
            <label for="player1_strength">Player 1: Strength</label>
            <select
              id="player1_strength"
              name="strength"
              onChange={(event) => handlePlayerChange(1, event)}
              value={game_config.player1.strength}
              disabled={game_config.is_game_active}
            >
              {strength_options}
            </select>
          </>
        ) : (
          ""
        )}
      </div>
      <div className="game-config-player2">
        <label for="player2">Player 2</label>
        <select
          id="player2"
          name="type"
          onChange={(event) => handlePlayerChange(2, event)}
          value={game_config.player2.type}
          disabled={game_config.is_game_active}
        >
          {player_options}
        </select>
        {game_config.player2.type === MCTS_UCT_PLAYER ? (
          <>
            <label for="player2_strength">Player 2: Strength</label>
            <select
              id="player2_strength"
              name="strength"
              onChange={(event) => handlePlayerChange(2, event)}
              value={game_config.player2.strength}
              disabled={game_config.is_game_active}
            >
              {strength_options}
            </select>
          </>
        ) : (
          ""
        )}
      </div>
      <div>
        <button onClick={handlePlayResetClicked}>
          {game_config.is_game_active ? "Reset" : "Play"}
        </button>
      </div>
    </div>
  );
}
