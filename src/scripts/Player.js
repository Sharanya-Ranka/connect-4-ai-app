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

  _getMoveUpdate() {
    return { move: this.column_clicked };
  }

  async getMoveUpdate(current_state, resolveCallback) {
    const update = this._getMoveUpdate();
    if (resolveCallback) {
      if (update.move === null) {
        setTimeout(() => {
          this.getMoveUpdate(current_state, resolveCallback);
        }, 500);
      } else {
        return resolveCallback(update);
      }
    } else {
      return new Promise((resolve) => {
        this.getMoveUpdate(current_state, resolve);
      });
    }
    // this.communicateMoveCallback(this.player_number, this.column_clicked);
  }

  communicateColumnClicked(column) {
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
    this.player_number = player_info.player_number;
    this.worker = new MCTSWithUCTPlayerWorker(player_info.num_playouts);
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

export { HumanPlayer, RandomValidMovePlayer, MCTSWithUCTPlayer };
