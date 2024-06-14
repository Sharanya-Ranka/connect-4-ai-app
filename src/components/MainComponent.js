import GameCreator from "./GameBoard/GameCreator";
import GameConfigForm from "./GameConfigForm/GameConfigForm";
import { GameState } from "../scripts/GameState";
import {
  MCTS_UCT_PLAYER,
  HUMAN_PLAYER,
  DEFAULT_GAME_CONFIG,
} from "../scripts/constants";

import React from "react";

export default function MainComponent() {
  // State: Form
  const [game_config, setGameConfig] = React.useState(DEFAULT_GAME_CONFIG);

  // State: GameBoard
  const [game_state, setGameState] = React.useState(
    new GameState(game_config.num_rows, game_config.num_cols),
  );

  // State: Players
  const [players, setPlayers] = React.useState([]);

  // State: Active Player Index. Used to keep track of the active player
  const [active_player_ind, setActivePlayerInd] = React.useState(-1);

  // State: GameState estimations

  React.useEffect(() => {}, [game_config.is_game_active]);

  return (
    <>
      <GameConfigForm
        game_config={game_config}
        setGameConfig={setGameConfig}
        setPlayers={setPlayers}
        setGameState={setGameState}
        setActivePlayerInd={setActivePlayerInd}
      />
      <GameCreator
        game_config={game_config}
        game_state={game_state}
        players={players}
        active_player_ind={active_player_ind}
        setGameState={setGameState}
        setActivePlayerInd={setActivePlayerInd}
      />
    </>
  );
}
