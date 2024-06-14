import { Tree, getGameTreeData } from "../../scripts/GameTree";
import TreeVisualizer from "./TreeVisualizer";

export default function TreeVisualizerMain() {
  const game_tree_data = getGameTreeData(5, 7);
  //   console.log(game_tree_data);
  //   const tree = new Tree(
  //     [
  //       { key: 1, value: 1 },
  //       { key: 2, value: 2 },
  //       { key: 3, value: 3 },
  //       { key: 4, value: 4 },
  //       { key: 5, value: 5 },
  //       { key: 6, value: 6 },
  //       { key: 7, value: 7 },
  //       { key: 8, value: 8 },
  //     ],
  //     [
  //       [3, 1],
  //       [2, 1],
  //       [4, 3],
  //       [5, 3],
  //       [6, 2],
  //       [7, 2],
  //       [8, 4],
  //     ],
  //     1,
  //   );

  const tree = new Tree(
    game_tree_data.node_data,
    game_tree_data.parents_data,
    game_tree_data.root_key,
  );
  return (
    <div className="game-tree-main">
      <TreeVisualizer tree={tree} />
    </div>
  );
}
