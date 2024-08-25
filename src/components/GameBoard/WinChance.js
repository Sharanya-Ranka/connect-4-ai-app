import "../../styles/GameBoardStyles/WinChance.css";

export default function WinChance({ win_chance, game_state }) {
  const player_ind = win_chance.player_ind;
  const win_prob = win_chance.win_chance;
  const player1_win_chance = player_ind === 1 ? win_prob : 1 - win_prob;
  const player2_win_chance = player_ind === 2 ? win_prob : 1 - win_prob;
  const active = game_state.active_player_ind;
  const asof_move_num = game_state.all_moves.length;
  // console.log("Win Chance", player1_win_chance, win_chance);
  return (
    <div className="win-chance">
      <h3>{asof_move_num}</h3>
      <div className="win-stats">
        <div className="table-label">
          <b>Win Chance</b>
        </div>
        {win_chance.calculation_ongoing ? (
          <div className="loader"></div>
        ) : (
          <></>
        )}
        {/* <div className="player-win-chance"> */}
        <div id="player1-name" className={`${active === 1 ? "active" : ""}`}>
          Player 1
        </div>
        <div
          id="player1-win-chance"
          className={`${active === 1 ? "active" : ""}`}
        >
          {Math.round(player1_win_chance * 100)}%{/* </div> */}
        </div>
        {/* <div className="player-win-chance"> */}
        <div id="player2-name" className={`${active === 2 ? "active" : ""}`}>
          Player 2
        </div>
        <div
          id="player2-win-chance"
          className={`${active === 2 ? "active" : ""}`}
        >
          {Math.round(player2_win_chance * 100)}%
        </div>
      </div>
      {/* </div> */}
    </div>
  );
}
