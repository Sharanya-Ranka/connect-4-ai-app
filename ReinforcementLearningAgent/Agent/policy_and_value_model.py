import torch
import numpy as np
import os
from functools import lru_cache

from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

from GameImplementation.game_state import GameState
from Agent.policy_and_value_nn import ConvolutionalPAndVNetwork
from config import NUM_INITIAL_CHANNELS, NUM_ROWS, NUM_COLS, debugObj


def createNewModel(config):
    model = ConvolutionalPAndVNetwork(config)
    model.eval()

    if config.get("USE_GPU", False) == True and torch.cuda.is_available():
        device = torch.device("cuda")
        print("GPU is available. Using CUDA device.")
    else:
        device = torch.device("cpu")
        print("GPU is not available. Using CPU device.")

    model = model.to(device)

    return model


def loadModel(config):
    model = ConvolutionalPAndVNetwork(config)
    weights_source = config.get("MODEL_WEIGHTS_SOURCE", None)
    # print(f"Loading model from path={weights_source}")

    if config.get("USE_GPU", False) == True and torch.cuda.is_available():
        device = torch.device("cuda")
        print("GPU is available. Using CUDA device.")
    else:
        device = torch.device("cpu")
        print("GPU is not available. Using CPU device.")

    assert weights_source is not None

    model.load_state_dict(torch.load(weights_source, weights_only=True))
    model.eval()
    model = model.to(device)
    
    
    return model


def saveModel(config):
    model = config["MODEL"]
    save_path = config["SAVE_PATH"]
    save_dir = os.path.dirname(save_path)
    os.makedirs(save_dir, exist_ok=True)

    torch.save(model.state_dict(), save_path)


def preprocessState(state: GameState):
    nn_state = np.zeros((NUM_INITIAL_CHANNELS, NUM_ROWS, NUM_COLS))
    row_inds, col_inds = np.indices((NUM_ROWS, NUM_COLS))
    nn_state[state.state + 1, row_inds, col_inds] = 1
    nn_state[0] = -1 if state.next_player == GameState.RED else 1
    # breakpoint()
    torch_state = torch.tensor(nn_state, dtype=torch.float32)
    # breakpoint()
    return torch_state


class PolicyAndValueFunction:
    def __init__(self, config):
        self.config = config
        self.pv_network = self._getPolicyAndValueNetwork()
        self.cache = {}
        self.model_iter = 0

        if config.get("USE_GPU", False) == True and torch.cuda.is_available():
            device = torch.device("cuda")
            print("GPU is available. Using CUDA device.")
        else:
            device = torch.device("cpu")
        
        self.device = device

    def updateModelIter(self):
        self.model_iter += 1

    def _evaluateFunctionBatched(self, states):
        processed_states = [preprocessState(state) for state in states]
        # Add batch dimension
        processed_states = torch.stack(processed_states, dim=0)
        with torch.no_grad():
            processed_states = processed_states.to(self.device)
            state_value, action_logits = self.pv_network(processed_states)
            action_probabilities = torch.softmax(action_logits, dim=-1)
        # breakpoint()
        # Remove batch dimension
        state_value = state_value.cpu().numpy()
        action_probabilities = action_probabilities.cpu().numpy()

        return state_value, action_probabilities

    def evaluateFunction(self, state: GameState):
        if (self.model_iter, state) not in self.cache:
            self.cache[(self.model_iter, state)] = self._evaluateFunction(state)

        return self.cache[(self.model_iter, state)]

    def _evaluateFunction(self, state: GameState):
        processed_state = preprocessState(state)
        # Add batch dimension
        processed_state = processed_state.unsqueeze(dim=0)
        with torch.no_grad():
            processed_state = processed_state.to(self.device)
            state_value, action_logits = self.pv_network(processed_state)
            action_probabilities = torch.softmax(action_logits, dim=-1)
        # breakpoint()
        # Remove batch dimension
        state_value = state_value.squeeze(dim=0)
        action_probabilities = action_probabilities.squeeze(dim=0)

        return state_value.cpu().numpy(), action_probabilities.cpu().numpy()

    def _getPolicyAndValueNetwork(self):
        return loadModel(self.config)


class SelfPlayDataset(Dataset):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.raw_data = self.config["DATASET"]
        self.processed_data = self._processDataset(self.raw_data)

    def __len__(self):
        return len(self.raw_data)

    def __getitem__(self, index):
        state_t, state_val_t, action_probs_t = self.processed_data[index]
        # breakpoint()

        return state_t, state_val_t, action_probs_t

    def _processDataset(self, raw_dataset):
        processed_dataset = []
        for state, state_val, action_probs in raw_dataset:
            # state_t = torch.tensor(state, dtype=torch.float32)
            state_val_t = torch.tensor(state_val, dtype=torch.float32)
            action_probs_t = torch.tensor(action_probs, dtype=torch.float32)

            processed_dataset.append(
                (preprocessState(state), state_val_t, action_probs_t)
            )

        # breakpoint()

        return processed_dataset


class PolicyAndValueTrainer:
    def __init__(self, config):
        self.config = config
        self.tr_config = config["TRAINING_CONFIG"]

        self.mse_loss_criterion = torch.nn.MSELoss()
        self.ce_loss_criterion = torch.nn.CrossEntropyLoss()

        self.debug_mse_loss_criterion = torch.nn.MSELoss(reduction="none")
        self.debug_ce_loss_criterion = torch.nn.CrossEntropyLoss(reduction="none")

        if config.get("USE_GPU", False) == True and torch.cuda.is_available():
            device = torch.device("cuda")
            print("GPU is available. Using CUDA device.")
        else:
            device = torch.device("cpu")
        
        self.device = device

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
            total_indices, test_size=self.tr_config["TEST_SIZE"]
        )
        # breakpoint()

        train_data = [dp for i, dp in enumerate(data) if i in train_indices]
        test_data = [dp for i, dp in enumerate(data) if i in test_indices]
        train_config = dict(DATASET=train_data)
        test_config = dict(DATASET=test_data)

        self.train_dataset = SelfPlayDataset(train_config)
        self.test_dataset = SelfPlayDataset(test_config)

        self.train_dataloader = DataLoader(
            self.train_dataset, batch_size=self.tr_config["BATCH_SIZE"], shuffle=True
        )
        self.test_dataloader = DataLoader(
            self.test_dataset, batch_size=self.tr_config["BATCH_SIZE"]
        )

    def setUpModel(self, model):
        self.model = model
        self.optimizer = torch.optim.Adam(
            model.parameters(), lr=self.tr_config["LEARNING_RATE"]
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

        # if (
        #     debugObj.iteration == 2
        #     and (debugObj.epoch == 14 or debugObj.epoch == 0)
        #     and debugObj.batch == 1
        # ):
        #     pass
        # debug_mse_loss = self.debug_mse_loss_criterion(pred[0], true[0])
        # debug_ce_loss = self.debug_ce_loss_criterion(pred[1], true[1])
        # print(f"Epoch={debugObj.epoch}")
        # print(f"True={true}\nPred={pred}")
        # print(f"Debug MSE loss={debug_mse_loss}\nDebug CE loss={debug_ce_loss}\n")
        # breakpoint()
        return mse_loss, ce_loss

    def train(self):
        # debugObj.updateEpoch(setZero=True)

        train_mse_losses = []
        train_ce_losses = []
        eval_mse_losses = []
        eval_ce_losses = []

        train_eval_mse_loss, train_eval_ce_loss = self.evalEpoch(self.train_dataloader)
        print(
            f"(Initial) Train mse loss={train_eval_mse_loss:.5f} Train ce loss={train_eval_ce_loss:.5f}"
        )
        
        for epoch in range(self.tr_config["EPOCHS"]):
            print(f"Epoch: {epoch}")

            
            train_mse_loss, train_ce_loss = self.trainEpoch()
            eval_mse_loss, eval_ce_loss = self.evalEpoch(self.test_dataloader)

            train_mse_losses.append(train_mse_loss)
            train_ce_losses.append(train_ce_loss)
            eval_mse_losses.append(eval_mse_loss)
            eval_ce_losses.append(eval_ce_loss)

            # debugObj.updateEpoch()

            print(
            f"Train mse loss={train_mse_loss:.5f} Train ce loss={train_ce_loss:.5f} Eval mse loss={eval_mse_loss:.5f} Eval ce loss={eval_ce_loss:.5f}"
        )


        print(
            f"Train mse loss={train_mse_losses[-1]:.5f} Train ce loss={train_ce_losses[-1]:.5f} Eval mse loss={eval_mse_losses[-1]:.5f} Eval ce loss={eval_ce_losses[-1]:.5f}"
        )

        # breakpoint()

    def trainEpoch(self):
        batches_mse_loss = 0
        batches_ce_loss = 0

        num_batches = 0

        self.model.train()

        # debugObj.updateBatch(setZero=True)
        for state, target_state_val, target_policy in self.train_dataloader:
            state = state.to(self.device)
            target_state_val = target_state_val.to(self.device)
            target_policy = target_policy.to(self.device)
            
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
            # debugObj.updateBatch()

        # print(f"TrainLoss={batches_loss/num_batches:.5f}")
        return float(batches_mse_loss / num_batches), float(
            batches_ce_loss / num_batches
        )

    def evalEpoch(self, dataloader):
        batches_mse_loss = 0
        batches_ce_loss = 0
        num_batches = 0

        self.model.eval()

        for state, target_state_val, target_policy in dataloader:
            state = state.to(self.device)
            target_state_val = target_state_val.to(self.device)
            target_policy = target_policy.to(self.device)
            
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
