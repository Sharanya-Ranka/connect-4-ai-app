export default function TreeVisualizerNode(props) {
  function handleClick() {
    props.handleClick({ level: props.level, choice: props.id });
  }

  return (
    <div
      className={`tree-vis-node level-colour-${
        props.level % 2 === 0 ? "yellow" : "red"
      } ${props.isclicked ? "clicked" : ""}`}
      onClick={handleClick}
    >
      {props.id}:{props.value}
    </div>
  );
}
