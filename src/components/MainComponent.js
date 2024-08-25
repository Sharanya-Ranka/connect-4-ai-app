import GameCreator from "./GameBoard/GameCreator";
import GameConfigForm from "./GameConfigForm/GameConfigForm";
import { MCTSWithUCTPlayer } from "../scripts/Player";
import { GameState } from "../scripts/GameState";

import {
  MCTS_UCT_PLAYER,
  HUMAN_PLAYER,
  DEFAULT_GAME_CONFIG,
  DEFAULT_GAME_STATE,
} from "../scripts/constants";

import React from "react";
import GameBoard from "./GameBoard/GameBoard";
import GamePlayersControl from "./GamePlayersControl/GamePlayersControl";
import WinChance from "./GameBoard/WinChance";
import "../styles/MainComponent.css";

// import useSe
export default function MainComponent() {
  // State: Form
  const [game_config, setGameConfig] = React.useState(DEFAULT_GAME_CONFIG);

  // // State: GameState
  // const [game_state, setGameState] = React.useState(
  //   new GameState(game_config.num_rows, game_config.num_cols),
  // );

  const [new_game_state, setNewGameState] = React.useState(DEFAULT_GAME_STATE);

  // // State: GameBoard Extra State
  // const [gameboard_extra_state, setGameBoardExtraState] = React.useState({
  //   column_clicked: null,
  //   column_hover: null,
  //   highlight_state: null,
  // });

  // State: Players
  const [players, setPlayers] = React.useState({
    monitor: null,
    player1: null,
    player2: null,
  });

  // // State: Active Player Index. Used to keep track of the active player
  // const [active_player_ind, setActivePlayerInd] = React.useState(-1);

  // State : Win Chance
  const [win_chance, setWinChance] = React.useState({
    player_ind: -1,
    win_chance: null,
    calculation_ongoing: false,
  });

  return (
    <div className="main-component">
      <GameConfigForm
        game_config={game_config}
        game_state={new_game_state}
        setGameConfig={setGameConfig}
        setPlayers={setPlayers}
        setGameState={setNewGameState}
      />
      <GamePlayersControl
        game_state={new_game_state}
        players={players}
        setGameState={setNewGameState}
        setWinChance={setWinChance}
      />
      <WinChance win_chance={win_chance} game_state={new_game_state} />
      <GameBoard game_state={new_game_state} setGameState={setNewGameState} />
    </div>
  );
}
