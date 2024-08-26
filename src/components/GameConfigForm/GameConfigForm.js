import "../../styles/GameConfigFormStyles/GameConfigForm.css";
import { GameState } from "../../scripts/GameState";
import {
  MCTS_UCT_PLAYER,
  HUMAN_PLAYER,
  MCTS_UCT_MONITOR_PLAYER,
  MCTS_AGENT_STRENGTHS,
  MAX_ROWS,
  MAX_COLUMNS,
  DEFAULT_GAME_STATE,
  DEFAULT_PLAYER_CONFIGS,
} from "../../scripts/constants";
import React from "react";
import {
  HumanPlayer,
  MCTSWithUCTPlayer,
  MCTSWithUCTMonitorPlayer,
} from "../../scripts/Player";

export default function GameConfigForm({
  game_config,
  game_state,
  setGameConfig,
  setPlayers,
  setGameState,
}) {
  // console.log("GameConfigForm: GameState", game_state);
  // Form change handlers
  function handleGameBoardChange(event) {
    const { name, value } = event.target;
    const prev_game_board = {
      num_rows: game_config.num_rows,
      num_cols: game_config.num_cols,
    };
    const new_game_board = { ...prev_game_board, [name]: value };
    // console.log(name, value);
    setGameConfig((prev_state) => ({ ...prev_state, ...new_game_board }));
    setGameState((prev_state) => ({ ...prev_state, ...new_game_board }));
  }

  function handlePlayerChange(player_num, event) {
    const { name, value } = event.target;
    // console.log(name, value);
    const player_config =
      player_num === 0
        ? game_config.monitor
        : player_num === 1
          ? game_config.player1
          : game_config.player2;

    const player_name =
      player_num === 0 ? "monitor" : player_num === 1 ? "player1" : "player2";

    const new_player_config = { ...player_config, [name]: value };
    // console.log("New player config", new_player_config);
    setGameConfig((prev_state) => ({
      ...prev_state,
      [player_name]: new_player_config,
    }));
  }

  function handlePlayerChangeType(player_num, event) {
    const { name, value } = event.target;
    const default_config = DEFAULT_PLAYER_CONFIGS[value];

    const player_name =
      player_num === 0 ? "monitor" : player_num === 1 ? "player1" : "player2";

    // console.log("New player config", default_config);
    setGameConfig((prev_state) => ({
      ...prev_state,
      [player_name]: default_config,
    }));
  }

  function handlePlayerChangeStrength(player_num, event) {
    const { name, value } = event.target;
    const strength = parseInt(value);
    const player_name =
      player_num === 0 ? "monitor" : player_num === 1 ? "player1" : "player2";

    const player_config = game_config[player_name];
    const new_player_config = { ...player_config, [name]: strength };
    // console.log("New player config", new_player_config);

    setGameConfig((prev_state) => ({
      ...prev_state,
      [player_name]: new_player_config,
    }));
  }

  function handlePlayResetClicked(event) {
    // console.log("Button clicked");
    const upd_is_game_active = !game_state.is_game_active;
    setGameState((prev_state) => ({
      ...prev_state,
      is_game_active: upd_is_game_active,
    }));

    if (upd_is_game_active) {
      performPlaySetup();
    } else {
      performReset();
    }
  }

  function handlePausedClicked(event) {
    setGameState((prev_state) => ({
      ...prev_state,
      paused: !prev_state.paused,
    }));
  }

  function getPlayer(player_config, player_num) {
    if (player_config.type === HUMAN_PLAYER) {
      return new HumanPlayer(player_num);
    } else if (player_config.type === MCTS_UCT_PLAYER) {
      const player_info = {
        player_num: player_num,
        num_playouts: player_config.strength,
      };
      return new MCTSWithUCTPlayer(player_info);
    } else if (player_config.type === MCTS_UCT_MONITOR_PLAYER) {
      const player_info = {
        player_num: player_num,
        num_playouts: player_config.strength,
      };
      return new MCTSWithUCTMonitorPlayer(player_info);
    }
  }

  function performPlaySetup() {
    const players = {
      monitor: getPlayer(
        {
          type: MCTS_UCT_MONITOR_PLAYER,
          strength: game_config.monitor.strength,
        },
        0,
      ),
      player1: getPlayer(game_config.player1, 1),
      player2: getPlayer(game_config.player2, 2),
    };
    // console.log("Setting players", players);
    // console.log("Setting active player index", 0);
    setPlayers(players);
    setGameState((prev_state) => ({ ...prev_state, active_player_ind: 1 }));
  }

  function performReset() {
    const players = { monitor: null, player1: null, player2: null };
    setPlayers(players);
    setGameState((prev_state) => ({
      ...DEFAULT_GAME_STATE,
      num_rows: game_config.num_rows,
      num_cols: game_config.num_cols,
      is_game_active: false,
    }));
    // setActivePlayerInd(-1);
  }

  const row_options = Array.from(
    Array.from({ length: MAX_ROWS + 1 }).map((_, ind) =>
      ind >= 4 ? <option value={ind}>{ind}</option> : "",
    ),
  );

  const column_options = Array.from(
    Array.from({ length: MAX_COLUMNS + 1 }).map((_, ind) =>
      ind >= 4 ? <option value={ind}>{ind}</option> : "",
    ),
  );

  const player_options = (
    <>
      <option value={MCTS_UCT_PLAYER}>{MCTS_UCT_PLAYER}</option>
      <option value={HUMAN_PLAYER}>{HUMAN_PLAYER}</option>
    </>
  );

  const monitor_option = (
    <>
      <option value={MCTS_UCT_PLAYER}>{MCTS_UCT_PLAYER}</option>
    </>
  );

  const strength_options = MCTS_AGENT_STRENGTHS.map((val) => (
    <option value={val}>{val}</option>
  ));

  return (
    <div className="game-config-form">
      <b>Game Board</b>
      <div className="game-config-rows">
        {/* Num rows*/}
        <label for="num_rows">Rows</label>
        <select
          id="num_rows"
          name="num_rows"
          onChange={handleGameBoardChange}
          value={game_config.num_rows}
          disabled={game_state.is_game_active}
        >
          {row_options}
        </select>
      </div>
      <div className="game-config-columns">
        <label for="num_cols">Columns</label>
        <select
          id="num_cols"
          name="num_cols"
          onChange={handleGameBoardChange}
          value={game_config.num_cols}
          disabled={game_state.is_game_active}
        >
          {column_options}
        </select>
      </div>
      <hr />
      <b>Players</b>
      {/* Player types */}
      <div className="game-config-player1">
        Player1
        <br />
        {/* <label for="player1">Player 1: Type</label> */}
        <select
          id="player1"
          name="type"
          onChange={(event) => handlePlayerChangeType(1, event)}
          value={game_config.player1.type}
          disabled={game_state.is_game_active}
        >
          {player_options}
        </select>
        {game_config.player1.type === MCTS_UCT_PLAYER ? (
          <>
            <label className="strength-label" for="player1_strength">
              Strength
            </label>
            <select
              id="player1_strength"
              name="strength"
              onChange={(event) => handlePlayerChangeStrength(1, event)}
              value={game_config.player1.strength}
              disabled={game_state.is_game_active}
            >
              {strength_options}
            </select>
          </>
        ) : (
          ""
        )}
      </div>
      <div className="game-config-player2">
        Player2
        <br />
        {/* <label for="player2">Player 2</label> */}
        <select
          id="player2"
          name="type"
          onChange={(event) => handlePlayerChangeType(2, event)}
          value={game_config.player2.type}
          disabled={game_state.is_game_active}
        >
          {player_options}
        </select>
        {game_config.player2.type === MCTS_UCT_PLAYER ? (
          <>
            <label className="strength-label" for="player2_strength">
              Strength
            </label>
            <select
              id="player2_strength"
              name="strength"
              onChange={(event) => handlePlayerChangeStrength(2, event)}
              value={game_config.player2.strength}
              disabled={game_state.is_game_active}
            >
              {strength_options}
            </select>
          </>
        ) : (
          ""
        )}
      </div>
      <div className="game-config-monitor">
        Monitor (Calculates win chance)
        <br />
        {/* <label for="player2">Player 2</label> */}
        <select
          id="monitor"
          name="type"
          // onChange={(event) => handlePlayerChange(2, event)}
          value={game_config.monitor.type}
          disabled={game_state.is_game_active}
        >
          {monitor_option}
        </select>
        <>
          <label className="strength-label" for="monitor_strength">
            Strength
          </label>
          <select
            id="monitor_strength"
            name="strength"
            onChange={(event) => handlePlayerChangeStrength(0, event)}
            value={game_config.monitor.strength}
            disabled={game_state.is_game_active}
          >
            {strength_options}
          </select>
        </>
      </div>
      <hr />
      <div>
        <button onClick={handlePlayResetClicked}>
          {game_state.is_game_active ? "Reset" : "Play"}
        </button>
      </div>
      <div>
        <button onClick={handlePausedClicked}>
          {game_state.paused ? "Resume" : "Pause"}
        </button>
      </div>
    </div>
  );
}
