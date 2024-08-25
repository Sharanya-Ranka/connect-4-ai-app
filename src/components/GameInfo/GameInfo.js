import "../../styles/GameInfo/GameInfo.css";

export default function GameInfo() {
  return (
    <div className="gameinfo">
      <h2>Play Connect4 against a Monte-Carlo Tree Search Agent!</h2>
      <h3>
        Connect 4 tokens vertically, horizontally or diagonally before your
        opponent to win
      </h3>
      <p>Use the selectors below to configure a game, and hit play!</p>
      <p>Explanation on the MCTS Agents coming soon!</p>
    </div>
  );
}
