import React from "react";

export default function GameBoardTile({
  parity,
  in_winning_run,
  tile_opacity,
  move_num,
}) {
  const tile_colour =
    parity === 0 ? "transparent" : parity === 1 ? "yellow" : "red";
  const highlight_type = "highlight-" + tile_opacity;
  const winning_run = in_winning_run ? "winning_run" : "";

  const blue_container = "radial-gradient(transparent 48%, blue 50%)",
    yellow_tile = "radial-gradient(yellow 48%, transparent 50%)",
    red_tile = "radial-gradient(red 48%, transparent 50%)",
    translucent =
      "radial-gradient(rgba(255, 255, 255, 0.35) 48%, transparent 50%)",
    black_dot = "radial-gradient(black 20%, transparent 22%)";

  const final_background =
    blue_container +
    (tile_opacity === "partial" ? `,${translucent}` : "") +
    (in_winning_run ? `,${black_dot}` : "") +
    (parity === 0 ? "" : parity === 1 ? `,${yellow_tile}` : `,${red_tile}`);

  return (
    <div
      className={`tile`} // ${tile_colour}${winning_run} ${highlight_type}`}
      style={{
        background: final_background,
        color: in_winning_run ? "white" : "black",
      }}
    >
      <span>{`${move_num >= 0 ? move_num : ""}`}</span>
    </div>
  );
}
