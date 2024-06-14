import TreeVisualizerNode from "./TreeVisualizerNode";
import React from "react";
import "../../styles/TreeVisualizerStyles/TreeVisualizer.css";

export default function TreeVisualizer({ tree }) {
  const [choices, setChoices] = React.useState([
    { level: 0, choice: tree.root_key },
  ]);
  function handleNodeClicked(new_choice) {
    setChoices((prev_choices) => [
      ...prev_choices.filter((choice) => choice.level < new_choice.level),
      new_choice,
    ]);
  }
  const levels_data = choices.map((choice) =>
    tree
      .getNode(choice.choice)
      .children.map((choice_child) => tree.getNode(choice_child)),
  );
  //   console.log(choices);

  const levels_jsx = levels_data.map((level, level_ind) => (
    <div className="tree-vis-level">
      {level.map((node) => (
        <TreeVisualizerNode
          id={node.key}
          value={node.value}
          level={level_ind + 1}
          isclicked={choices.map((choice) => choice.choice).includes(node.key)}
          handleClick={handleNodeClicked}
        />
      ))}
    </div>
  ));
  return (
    <div className="tree-visualizer">
      <div className="tree-vis">{levels_jsx}</div>
    </div>
  );
}
