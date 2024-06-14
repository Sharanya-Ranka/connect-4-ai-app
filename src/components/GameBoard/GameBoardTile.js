import React from "react";

export default function GameBoardTile(props) {
  const [status, changeStatus] = React.useState("");
  const tile_colour =
    props.colour === 0 ? "transparent" : props.colour === 1 ? "yellow" : "red";
  const winning_run = props.in_winning_run ? "-winning_run" : "";
  const move_num = props.move_num;

  function handleMouseEnter() {
    changeStatus("tile-highlighted");
  }

  function handleMouseLeave() {
    changeStatus("");
  }

  return (
    <div
      className={`tile tile-${tile_colour}${winning_run} ${status}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {move_num}
    </div>
  );
}
