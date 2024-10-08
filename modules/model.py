from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Tuple    

import numpy as np
from nptyping import Number, NDArray, Shape
from tqdm import tqdm

from .loader import DatasetLoader


class Sequential:
    def __init__(self, blocks: List[Layer]) -> None:
        self.blocks = blocks
        self.is_training = True    

    def forward(
        self, 
        X: NDArray[Any, Number]
    ) -> NDArray[Any, Number]:
        for block in self.blocks:
            X = block(X, train=self.is_training)
        return X

    def backward(
        self, 
        grad: NDArray[Any, Number]
    ) -> None:
        for block in reversed(self.blocks):
            grad = block.backward(grad)

    def train(self) -> None:
        self.is_training = True

    def eval(self) -> None:
        self.is_training = False

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)
    

class RBF_Sequential:
    def __init__(self, blocks: List[Layer]) -> None:
        self.blocks = blocks
        self.is_training = True    

    def forward(
        self, 
        X: NDArray[Any, Number],
        **kwargs
    ) -> NDArray[Any, Number]:
        for block in self.blocks:
            if self.is_training:
                X = block(X, train=self.is_training, y=kwargs['y'])
            else:
                X = block(X, train=self.is_training)
        return X

    def backward(
        self, 
        grad: NDArray[Any, Number]
    ) -> None:
        for block in reversed(self.blocks):
            grad = block.backward(grad)

    def train(self) -> None:
        self.is_training = True

    def eval(self) -> None:
        self.is_training = False
    
    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)
    

def train(
    model: Sequential, 
    X_train: NDArray[Any, Number], 
    y_train: NDArray[Any, Number], 
    criterion: Loss,
    optimizer: Optimizer,
    epochs: int,
    batch_size: int
) -> Tuple[List[Number], List[Number]]:
    loss_list = []
    acc_list = []
    train_loader = DatasetLoader(X_train, y_train, batch_size=batch_size)
    model.train()

    for epoch in range(epochs):
        print(f'\nEpoch {epoch + 1}')
        correct = 0
        loss = 0

        for X, y in tqdm(train_loader, desc='Training'):
            #y_pred = model(X.reshape(batch_size, -1))
            y_pred = model(X)
            correct += np.sum(np.argmax(y_pred, axis=1) == y)
            loss += criterion(y, y_pred)
            grad = criterion.backward()
            model.backward(grad)
            optimizer.step()

        acc = correct / len(y_train)
        acc_list.append(acc)
        loss_list.append(loss)
        print(f'Accuracy: {acc} | Loss: {loss}')

    return acc_list, loss_list


def test(
    model: Sequential,
    X_test: NDArray[Any, Number],
    y_test: NDArray[Any, Number],
    batch_size: int
) -> float:
    correct = 0
    test_loader = DatasetLoader(X_test, y_test, batch_size=batch_size)
    model.eval()

    for X, y in tqdm(test_loader, desc='Testing'):
        y_pred = model(X)
        correct += np.sum(np.argmax(y_pred, axis=1) == y)
        
    return correct / len(y_test)