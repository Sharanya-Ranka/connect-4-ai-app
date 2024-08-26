import { MCTSWithUCTPlayerWorker } from "./MCTSWithUCTPlayerWorker";

class HumanPlayer {
  constructor(player_number) {
    this.player_number = player_number;
  }
  communicatesMoveThroughClick() {
    return true;
  }

  setCommunicateMoveCallback(callback) {
    this.communicateMoveCallback = callback;
  }

  setActive() {
    this.column_clicked = null;
  }

  _getMoveUpdate(resolveCallback) {
    // console.log("_getMoveUpdate: column clicked", this.column_clicked);
    if (this.column_clicked === null) {
      setTimeout(() => {
        this._getMoveUpdate(resolveCallback);
      }, 500);
    } else {
      // console.log("Resolving");
      resolveCallback({ move: this.column_clicked });
    }
  }

  async getMoveUpdate(current_state) {
    // console.log("getMoveUpdate: Started");
    this.column_clicked = null;
    return new Promise((resolve) => {
      this._getMoveUpdate(resolve);
    });
  }

  communicateColumnClicked(column) {
    // console.log("communicateColumnClicked:", column);
    this.column_clicked = column;
  }
}

class RandomValidMovePlayer {
  communicatesMoveThroughClick() {
    return false;
  }
}

class MCTSWithUCTPlayer {
  constructor(player_info) {
    // console.log("Creating MCTS player", player_info);
    this.player_number = player_info.player_num;
    this.worker = new MCTSWithUCTPlayerWorker(
      player_info.num_playouts,
      player_info.player_num,
    );
  }
  communicatesMoveThroughClick() {
    return false;
  }

  setActive() {}

  async getMoveUpdate(current_state) {
    const update = await this.worker.getMoveAsync(current_state);
    return update;
  }
}

class MCTSWithUCTMonitorPlayer {
  constructor(player_info) {
    this.player_number = player_info.player_num;
    this.worker = new MCTSWithUCTPlayerWorker(
      player_info.num_playouts,
      player_info.player_number,
    );
  }
  communicatesMoveThroughClick() {
    return false;
  }

  setActive() {}

  async getMoveUpdate(current_state) {
    const update = await this.worker.getCurrentStateWinChance(current_state);
    return update;
  }
}

export {
  HumanPlayer,
  RandomValidMovePlayer,
  MCTSWithUCTPlayer,
  MCTSWithUCTMonitorPlayer,
};
