"""
Implement the following models for classification.

Feel free to modify the arguments for each of model's __init__ function.
This will be useful for tuning model hyperparameters such as hidden_dim, num_layers, etc,
but remember that the grader will assume the default constructor!
"""

from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F


class ClassificationLoss(nn.Module):
    def forward(self, logits: torch.Tensor, target: torch.LongTensor) -> torch.Tensor:
        """
        Multi-class classification loss
        Hint: simple one-liner

        Args:
            logits: tensor (b, c) logits, where c is the number of classes
            target: tensor (b,) labels

        Returns:
            tensor, scalar loss
        """
        #import pdb
        #pdb.set_trace()
        loss = nn.CrossEntropyLoss()(logits, target)
        print('DLHW2 loss', loss)

        return loss

class LinearClassifier(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6,
    ):
        """
        Args:
            h: int, height of the input image
            w: int, width of the input image
            num_classes: int, number of classes
        """
        super().__init__()

        input_size = 3 * h * w

        self.fc1 = nn.Linear(input_size, 128)  # First Linear layer, maps to 128 nodes
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: tensor (b, 3, H, W) image

        Returns:
            tensor (b, num_classes) logits
        """
        # Flatten the input image tensor from (b, 3, H, W) to (b, 3 * H * W)
        x = x.view(x.size(0), -1)  # Flattening the input

        # Apply the first fully connected layer
        x = self.fc1(x)

        # Apply the second fully connected layer (output layer)
        x = self.fc2(x)

        return x


class MLPClassifier(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6
    ):
        """
        An MLP with a single hidden layer

        Args:
            h: int, height of the input image
            w: int, width of the input image
            num_classes: int, number of classes
        """
        super().__init__()

        input_size = 3 * h * w
        # Input size after flattening the image
        input_size = 3 * h * w  # 3 channels (RGB) and h by w image size

        # Hidden layer
        self.fc1 = nn.Linear(input_size, 128)

        # Output layer
        self.fc2 = nn.Linear(128, num_classes)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: tensor (b, 3, H, W) image

        Returns:
            tensor (b, num_classes) logits
        """
        # Flatten the input image (batch_size, 3, H, W) -> (batch_size, 3*H*W)
        x = x.view(x.size(0), -1)

        # First fully connected layer + ReLU activation
        x = F.relu(self.fc1(x))

        # Second fully connected layer (output layer)
        x = self.fc2(x)

        return x



class MLPClassifierDeep(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6,
        hidden_dim: int = 128,
        num_layers: int = 4
    ):
        """
        An MLP with multiple hidden layers

        Args:
            h: int, height of image
            w: int, width of image
            num_classes: int

        Hint - you can add more arguments to the constructor such as:
            hidden_dim: int, size of hidden layers
            num_layers: int, number of hidden layers
        """
        super().__init__()

        self.input_dim = h * w * 3  # Flattened input dimension
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_classes = num_classes

        # Define the layers
        layers = []
        layers.append(nn.Linear(self.input_dim, self.hidden_dim))
        layers.append(nn.ReLU())

        for _ in range(self.num_layers - 1):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.LayerNorm(hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(p=0.5))  # Add Dropout

        layers.append(nn.Linear(self.hidden_dim, self.num_classes))

        # Convert the list of layers into a Sequential module
        self.network = nn.Sequential(*layers)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: tensor (b, 3, H, W) image

        Returns:
            tensor (b, num_classes) logits
        """
        b = x.size(0)  # Batch size
        x = x.view(b, -1)  # Flatten the input tensor
        x = self.network(x)  # Pass through the network
        return x


class MLPClassifierDeepResidual(nn.Module):
    def __init__(
        self,
        h: int = 64,
        w: int = 64,
        num_classes: int = 6,
        hidden_dim: int = 128,
        num_layers: int = 5,
        dropout_rate: float = 0.5
    ):
        """
        Args:
            h: int, height of image
            w: int, width of image
            num_classes: int

        Hint - you can add more arguments to the constructor such as:
            hidden_dim: int, size of hidden layers
            num_layers: int, number of hidden layers
        """
        super().__init__()

        self.input_dim = 3 * h * w  # 3 channels * height * width

        # Input layer with batch normalization
        self.input_layer = nn.Sequential(
            nn.Linear(self.input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU()
        )

        # Hidden layers with residual connections
        self.hidden_layers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate),
                nn.Linear(hidden_dim, hidden_dim),
                nn.LayerNorm(hidden_dim)
            ) for _ in range(num_layers)
        ])

        # Output layer
        self.output_layer = nn.Linear(hidden_dim, num_classes)

        # Activation function
        self.relu = nn.ReLU()

        # Dropout
        self.dropout = nn.Dropout(dropout_rate)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: tensor (b, 3, H, W) image

        Returns:
            tensor (b, num_classes) logits
        """
        # Flatten the input
        x = x.view(x.size(0), -1)

        # Input layer
        x = self.input_layer(x)

        # Hidden layers with residual connections
        for layer in self.hidden_layers:
            residual = x
            x = layer(x)
            x += residual  # Add residual connection
            x = self.relu(x)

        # Final dropout before output layer
        x = self.dropout(x)

        # Output layer
        logits = self.output_layer(x)

        return logits


model_factory = {
    "linear": LinearClassifier,
    "mlp": MLPClassifier,
    "mlp_deep": MLPClassifierDeep,
    "mlp_deep_residual": MLPClassifierDeepResidual,
}


def calculate_model_size_mb(model: torch.nn.Module) -> float:
    """
    Args:
        model: torch.nn.Module

    Returns:
        float, size in megabytes
    """
    return sum(p.numel() for p in model.parameters()) * 4 / 1024 / 1024


def save_model(model):
    """
    Use this function to save your model in train.py
    """
    for n, m in model_factory.items():
        if isinstance(model, m):
            return torch.save(model.state_dict(), Path(__file__).resolve().parent / f"{n}.th")
    raise ValueError(f"Model type '{str(type(model))}' not supported")


def load_model(model_name: str, with_weights: bool = False, **model_kwargs):
    """
    Called by the grader to load a pre-trained model by name
    """
    r = model_factory[model_name](**model_kwargs)
    if with_weights:
        model_path = Path(__file__).resolve().parent / f"{model_name}.th"
        assert model_path.exists(), f"{model_path.name} not found"
        try:
            r.load_state_dict(torch.load(model_path, map_location="cpu"))
        except RuntimeError as e:
            raise AssertionError(
                f"Failed to load {model_path.name}, make sure the default model arguments are set correctly"
            ) from e

    # Limit model sizes since they will be zipped and submitted
    model_size_mb = calculate_model_size_mb(r)
    if model_size_mb > 10:
        raise AssertionError(f"{model_name} is too large: {model_size_mb:.2f} MB")
    print(f"Model size: {model_size_mb:.2f} MB")

    return r
