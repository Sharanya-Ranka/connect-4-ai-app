import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    """
    A standard Residual Block as used in AlphaZero-like architectures.
    Consists of two convolutional layers with batch normalization and ReLU activation,
    and a skip connection that adds the input to the output of the convolutional layers.
    """

    def __init__(self, num_filters, kernel_size):
        super().__init__()
        padding = (
            kernel_size // 2
        )  # Ensure output size matches input size for same padding

        self.conv1 = nn.Conv2d(
            num_filters, num_filters, kernel_size=kernel_size, padding=padding
        )
        self.bn1 = nn.BatchNorm2d(num_filters)
        self.conv2 = nn.Conv2d(
            num_filters, num_filters, kernel_size=kernel_size, padding=padding
        )
        self.bn2 = nn.BatchNorm2d(num_filters)

    def forward(self, x):
        # Store the original input for the skip connection
        identity = x

        # First convolutional layer, batch norm, and ReLU
        out = F.relu(self.bn1(self.conv1(x)))
        # Second convolutional layer and batch norm
        out = self.bn2(self.conv2(out))

        # Add the identity (skip connection) to the output
        out += identity
        # Apply ReLU after the skip connection
        out = F.relu(out)
        return out


class ConvolutionalPAndVNetwork(nn.Module):
    """
    A Convolutional Neural Network (CNN) based Policy and Value network
    for Connect4, inspired by AlphaZero.
    It takes the board state as input and outputs a policy (move probabilities)
    and a value (game outcome prediction).
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

        num_rows = config["NUM_ROWS"]
        num_cols = config["NUM_COLS"]
        unique_tokens = config[
            "UNIQUE_TOKENS"
        ]  # Number of channels (e.g., 3 for player1, player2, empty)
        num_filters = config["NUM_CNN_FILTERS"]
        kernel_size = config["KERNEL_SIZE"]
        num_residual_blocks = config["NUM_RESIDUAL_BLOCKS"]
        dropout_rate = config["DROPOUT_RATE"]
        policy_head_filters = config["POLICY_HEAD_FILTERS"]
        value_head_filters = config["VALUE_HEAD_FILTERS"]

        # Calculate padding to maintain spatial dimensions
        padding = kernel_size // 2

        # --- Initial Convolutional Block ---
        # This layer processes the raw board state (unique_tokens channels)
        # into a higher-dimensional feature map (num_filters).
        self.initial_conv = nn.Conv2d(
            unique_tokens, num_filters, kernel_size=kernel_size, padding=padding
        )
        self.initial_bn = nn.BatchNorm2d(num_filters)

        # --- Residual Tower ---
        # A stack of residual blocks to extract deeper features.
        self.residual_blocks = nn.ModuleList(
            [
                ResidualBlock(num_filters, kernel_size)
                for _ in range(num_residual_blocks)
            ]
        )

        # --- Policy Head ---
        # Predicts the probability distribution over possible moves (columns).
        # It typically has fewer filters and then a final linear layer.
        self.policy_conv = nn.Conv2d(
            num_filters, policy_head_filters, kernel_size=1
        )  # 1x1 conv to reduce channels
        self.policy_bn = nn.BatchNorm2d(policy_head_filters)
        # AdaptiveAvgPool2d reduces each feature map to a 1x1 spatial dimension,
        # effectively performing global average pooling.
        self.policy_pool = nn.AdaptiveAvgPool2d((1, 1))
        # Linear layer to output logits for each column (action)
        self.policy_fc1 = nn.Linear(policy_head_filters, policy_head_filters//2)
        self.policy_fc2 = nn.Linear(policy_head_filters//2, num_cols)
        self.policy_dropout = nn.Dropout(dropout_rate)

        # --- Value Head ---
        # Predicts the scalar value of the board state (e.g., win/loss/draw).
        # Similar structure to the policy head but outputs a single value.
        self.value_conv = nn.Conv2d(
            num_filters, value_head_filters, kernel_size=1
        )  # 1x1 conv to reduce channels
        self.value_bn = nn.BatchNorm2d(value_head_filters)
        self.value_pool = nn.AdaptiveAvgPool2d((1, 1))
        # Linear layer to output a single value
        self.value_fc1 = nn.Linear(
            value_head_filters, value_head_filters // 2
        )  # Intermediate linear layer
        self.value_fc2 = nn.Linear(
            value_head_filters // 2, 1
        )  # Final linear layer for scalar output
        self.value_dropout = nn.Dropout(dropout_rate)

    def forwardInference(self, inp):
        return self.forward(inp)

    def forward(self, inp):
        # The input `inp` is expected to be flattened, so we need to reshape it
        # from (batch_size, NUM_ROWS * NUM_COLS * UNIQUE_TOKENS)
        # to (batch_size, UNIQUE_TOKENS, NUM_ROWS, NUM_COLS)
        # batch_size = inp.shape[0]
        num_rows = self.config["NUM_ROWS"]
        num_cols = self.config["NUM_COLS"]
        unique_tokens = self.config["UNIQUE_TOKENS"]

        # Reshape input to (batch_size, channels, height, width)
        # Make sure the order of dimensions is correct: unique_tokens as channels
        # breakpoint()
        # x = inp.view(batch_size, unique_tokens, num_rows, num_cols)

        # Initial convolutional block
        x = F.relu(self.initial_bn(self.initial_conv(inp)))

        # Pass through residual tower
        for block in self.residual_blocks:
            x = block(x)

        # --- Policy Head Forward Pass ---
        # Apply 1x1 convolution, batch norm, and ReLU
        policy_x = F.relu(self.policy_bn(self.policy_conv(x)))
        # Global average pooling
        policy_x = self.policy_pool(policy_x)
        # Flatten for the linear layer (removes 1x1 spatial dimensions)
        policy_x = torch.flatten(policy_x, 1)
        # Apply dropout
        policy_x = self.policy_dropout(policy_x)
        # Final linear layer for policy logits
        policy_x = F.relu(self.policy_fc1(policy_x))
        policy_op =   self.policy_fc2(policy_x) # Output logits

        # --- Value Head Forward Pass ---
        # Apply 1x1 convolution, batch norm, and ReLU
        value_x = F.relu(self.value_bn(self.value_conv(x)))
        # Global average pooling
        value_x = self.value_pool(value_x)
        # Flatten for the linear layers
        value_x = torch.flatten(value_x, 1)
        # Apply dropout
        value_x = self.value_dropout(value_x)
        # Intermediate linear layer with ReLU
        value_x = F.relu(self.value_fc1(value_x))
        # Final linear layer for value output
        value_lin_op = self.value_fc2(value_x)

        # Compress value to between -1 and +1 using tanh
        # Squeeze to remove the last dimension (from (batch_size, 1) to (batch_size,))
        value_op = torch.tanh(value_lin_op).squeeze(-1)

        return value_op, policy_op


class SimplePAndVNetwork(torch.nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config

        in_features = config["NUM_ROWS"] * config["NUM_COLS"] * config["UNIQUE_TOKENS"]
        actions = config["NUM_COLS"]
        hidden_dim = config["HIDDEN_DIM"]

        # Make a simple NN
        self.inp_layer = torch.nn.Linear(in_features, hidden_dim)
        self.h1 = torch.nn.Linear(hidden_dim, hidden_dim)
        self.h2 = torch.nn.Linear(hidden_dim, hidden_dim)
        self.policy_layer_lin = torch.nn.Linear(hidden_dim, actions)
        self.value_layer_lin = torch.nn.Linear(hidden_dim, 1)
        self.relu = torch.nn.ReLU()

    def forward(self, inp):
        inp_layer_op = self.relu(self.inp_layer(inp))
        h1_op = self.relu(self.h1(inp_layer_op))
        h2_op = self.relu(self.h2(h1_op))
        policy_lin_op = self.policy_layer_lin(h2_op)
        value_lin_op = self.value_layer_lin(h2_op).sum(dim=-1)

        # Leave the policy op as logits
        policy_op = policy_lin_op
        # Compress value to between -1 and +1
        value_op = torch.tanh(value_lin_op)
        # breakpoint()

        return value_op, policy_op
