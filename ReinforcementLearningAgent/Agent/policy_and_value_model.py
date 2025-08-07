import torch
import numpy as np
from functools import lru_cache

from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

from GameImplementation.game_state import GameState
from Agent.policy_and_value_nn import ConvolutionalPAndVNetwork
from config import UNIQUE_TOKENS, NUM_ROWS, NUM_COLS, debugObj


def preprocessState(state: GameState):
    nn_state = np.zeros((UNIQUE_TOKENS, NUM_ROWS, NUM_COLS))
    row_inds, col_inds = np.indices((NUM_ROWS, NUM_COLS))
    nn_state[state.state, row_inds, col_inds] = 1
    torch_state = torch.tensor(nn_state, dtype=torch.float32)
    # breakpoint()
    return torch_state


class PolicyAndValueFunction:
    def __init__(self, config):
        self.config = config
        self.pv_network = self._getPolicyAndValueNetwork()
        self.cache = {}
        self.model_iter = 0

    def updateModelIter(self):
        self.model_iter += 1

    def evaluateFunction(self, state: GameState):
        if (self.model_iter, state) not in self.cache:
            self.cache[(self.model_iter, state)] = self._evaluateFunction(state)

        return self.cache[(self.model_iter, state)]

    def _evaluateFunction(self, state: GameState):
        processed_state = preprocessState(state)
        # Add batch dimension
        processed_state = processed_state.unsqueeze(dim=0)
        with torch.no_grad():
            state_value, action_logits = self.pv_network(processed_state)
            action_probabilities = torch.softmax(action_logits, dim=-1)
        # breakpoint()
        # Remove batch dimension
        state_value = state_value.squeeze(dim=0)
        action_probabilities = action_probabilities.squeeze(dim=0)

        return state_value.numpy(), action_probabilities.numpy()

    def _getPolicyAndValueNetwork(self):
        if self.config["MODEL_WEIGHTS_SOURCE"] == None:
            return ConvolutionalPAndVNetwork(self.config)


class SelfPlayDataset(Dataset):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.raw_data = self.config["DATASET"]
        self.processed_data = self._processDataset(self.raw_data)

    def __len__(self):
        return len(self.raw_data)

    def __getitem__(self, index):
        state, state_val, action_probs = self.processed_data[index]

        state_t = torch.tensor(state, dtype=torch.float32)
        state_val_t = torch.tensor(state_val, dtype=torch.float32)
        action_probs_t = torch.tensor(action_probs, dtype=torch.float32)
        # breakpoint()

        return state_t, state_val_t, action_probs_t

    def _processDataset(self, raw_dataset):
        processed_dataset = []
        for state, state_val, action_probs in raw_dataset:
            processed_dataset.append((preprocessState(state), state_val, action_probs))

        # breakpoint()

        return processed_dataset


class PolicyAndValueTrainer:
    def __init__(self, config):
        self.config = config
        self.mse_loss_criterion = torch.nn.MSELoss()
        self.ce_loss_criterion = torch.nn.CrossEntropyLoss()

        self.debug_mse_loss_criterion = torch.nn.MSELoss(reduction="none")
        self.debug_ce_loss_criterion = torch.nn.CrossEntropyLoss(reduction="none")

    def runTrainPipeline(self, model, data):
        print(f"Beginning training\nNumber of datapoints={len(data)}")
        self.loadData(data)
        # breakpoint()
        self.setUpModel(model)
        self.train()
        # breakpoint()

    def loadData(self, data):
        total_indices = np.arange(len(data))
        train_indices, test_indices = train_test_split(
            total_indices, test_size=self.config["TEST_SIZE"]
        )
        # breakpoint()

        train_data = [dp for i, dp in enumerate(data) if i in train_indices]
        test_data = [dp for i, dp in enumerate(data) if i in test_indices]
        train_config = dict(DATASET=train_data)
        test_config = dict(DATASET=test_data)

        self.train_dataset = SelfPlayDataset(train_config)
        self.test_dataset = SelfPlayDataset(test_config)

        self.train_dataloader = DataLoader(
            self.train_dataset, batch_size=self.config["BATCH_SIZE"], shuffle=False
        )
        self.test_dataloader = DataLoader(
            self.test_dataset, batch_size=self.config["BATCH_SIZE"]
        )

    def setUpModel(self, model):
        self.model = model
        self.optimizer = torch.optim.Adam(
            model.parameters(), lr=self.config["LEARNING_RATE"]
        )

    def _calculateLoss(self, true, pred):
        mse_loss = self.mse_loss_criterion(pred[0], true[0])
        ce_loss = self.ce_loss_criterion(pred[1], true[1])
        total_loss = mse_loss + ce_loss
        # total_loss = mse_loss
        # breakpoint()
        return total_loss

    def _calculateDebugLoss(self, true, pred):
        mse_loss = self.mse_loss_criterion(pred[0], true[0])
        ce_loss = self.ce_loss_criterion(pred[1], true[1])
        total_loss = mse_loss + ce_loss
        # total_loss = mse_loss

        if (
            debugObj.iteration == 2
            and (debugObj.epoch == 14 or debugObj.epoch == 0)
            and debugObj.batch == 1
        ):
            pass
            # debug_mse_loss = self.debug_mse_loss_criterion(pred[0], true[0])
            # debug_ce_loss = self.debug_ce_loss_criterion(pred[1], true[1])
            # print(f"Epoch={debugObj.epoch}")
            # print(f"True={true}\nPred={pred}")
            # print(f"Debug MSE loss={debug_mse_loss}\nDebug CE loss={debug_ce_loss}\n")
        # breakpoint()
        return mse_loss, ce_loss

    def train(self):
        debugObj.updateEpoch(setZero=True)

        train_mse_losses = []
        train_ce_losses = []
        eval_mse_losses = []
        eval_ce_losses = []

        for epoch in range(self.config["EPOCHS"]):
            # print(f"Epoch: {epoch}")
            train_mse_loss, train_ce_loss = self.trainEpoch()
            eval_mse_loss, eval_ce_loss = self.evalEpoch()

            train_mse_losses.append(train_mse_loss)
            train_ce_losses.append(train_ce_loss)
            eval_mse_losses.append(eval_mse_loss)
            eval_ce_losses.append(eval_ce_loss)

            debugObj.updateEpoch()

        print(
            f"Train mse loss={train_mse_losses[-1]:.5f} Train ce loss={train_ce_losses[-1]:.5f} Eval mse loss={eval_mse_losses[-1]:.5f} Eval ce loss={eval_ce_losses[-1]:.5f}"
        )

        # breakpoint()

    def trainEpoch(self):
        batches_mse_loss = 0
        batches_ce_loss = 0

        num_batches = 0

        self.model.train()

        debugObj.updateBatch(setZero=True)
        for state, target_state_val, target_policy in self.train_dataloader:
            pred_state_val, pred_policy = self.model(state)
            mse_loss, ce_loss = self._calculateDebugLoss(
                (target_state_val, target_policy), (pred_state_val, pred_policy)
            )

            loss = mse_loss + ce_loss
            # loss = mse_loss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            batches_mse_loss += mse_loss.item()
            batches_ce_loss += ce_loss.item()

            num_batches += 1
            debugObj.updateBatch()

        # print(f"TrainLoss={batches_loss/num_batches:.5f}")
        return float(batches_mse_loss / num_batches), float(
            batches_ce_loss / num_batches
        )

    def evalEpoch(self):
        batches_mse_loss = 0
        batches_ce_loss = 0
        num_batches = 0

        self.model.eval()

        for state, target_state_val, target_policy in self.test_dataloader:
            pred_state_val, pred_policy = self.model(state)
            mse_loss, ce_loss = self._calculateDebugLoss(
                (target_state_val, target_policy), (pred_state_val, pred_policy)
            )

            batches_mse_loss += mse_loss.item()
            batches_ce_loss += ce_loss.item()
            num_batches += 1

        # print(f"EvalLoss={batches_loss/num_batches:.5f}")
        return float(batches_mse_loss / num_batches), float(
            batches_ce_loss / num_batches
        )
