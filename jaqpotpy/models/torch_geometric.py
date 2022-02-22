from jaqpotpy.models.base_classes import Model
from jaqpotpy.doa.doa import DOA
from jaqpotpy.descriptors.base_classes import MolecularFeaturizer
from typing import Any, Iterable
import pandas as pd
import pickle
from jaqpotpy.datasets import MolecularTabularDataset, Dataset, TorchGraphDataset
from jaqpotpy.models import Evaluator, Preprocesses
from torch_geometric.loader import DataLoader
import torch
from jaqpotpy.models import MolecularModel
import numpy as np
import torch_geometric
from jaqpotpy.cfg import config


class MolecularTorchGeometric(Model):

    def __init__(self, dataset: TorchGraphDataset, model_nn: torch.nn.Module
                 , doa: DOA = None
                 , eval: Evaluator = None, preprocess: Preprocesses = None
                 , dataLoaderParams: Any = None, epochs: int = None
                 , criterion: torch.nn.Module = None, optimizer: Any = None
                 , train_batch: int = 50, test_batch: int = 50, log_steps: int = 1):
        # super(InMemMolModel, self).__init__(dataset=dataset, doa=doa, model=model)
        self.dataset: TorchGraphDataset = dataset
        self.model_nn = model_nn
        self.doa = doa
        self.doa_m = None
        self.external = None
        self.evaluator: Evaluator = eval
        self.preprocess: Preprocesses = preprocess
        self.train_batch = train_batch
        self.test_batch = test_batch
        self.trainDataLoaderParams = {'batch_size': self.train_batch, 'shuffle': False, 'num_workers': 0}
        self.testDataLoaderParams = {'batch_size': self.test_batch, 'shuffle': False, 'num_workers': 0}
        self.epochs = epochs
        self.criterion = criterion
        self.trained_model = None
        self.model_fitted: MolecularModel = None
        self.optimizer = optimizer
        self.train_loader = None
        self.test_loader = None
        self.log_steps = log_steps
        self.best_model = None
        # torch.multiprocessing.freeze_support()

    def __call__(self, smiles):
        self

    def fit(self):
        if self.doa:
            if self.doa.__name__ == 'SmilesLeverage':
                self.doa_m = self.doa.fit(self.dataset.smiles_strings)
            else:
                print("Only SmilesLeverage is suported for graph models")
        if self.dataset.df is not None:
            pass
        else:
            self.dataset.create()
        if self.evaluator is not None:
            if self.evaluator.dataset.df is not None:
                pass
            else:
                self.evaluator.dataset.create()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_fitted = MolecularModel()
        self.model_nn.to(device)
        # self.train_loader = DataLoader(dataset=self.dataset.df, **self.trainDataLoaderParams)
        # self.test_loader = DataLoader(dataset=self.evaluator.dataset.df, **self.testDataLoaderParams)
        self.train_loader = DataLoader(dataset=self.dataset, **self.trainDataLoaderParams)
        self.test_loader = DataLoader(dataset=self.evaluator.dataset, **self.testDataLoaderParams)
        temp_loss = None
        for epoch in range(1, self.epochs):
            self.train()
            train_loss = self.test(self.train_loader)
            test_loss = self.test(self.test_loader)
            if epoch % self.log_steps == 0:
                if self.dataset.task == "classification":
                    los = test_loss[2]
                    if temp_loss is None:
                        temp_loss = test_loss[2]
                    if temp_loss < los:
                        self.best_model = self.model_nn
                    print(f'Epoch: {epoch:03d}, Train Accuracy: {train_loss[2]}, Test Accuracy: {test_loss[2]}')
                else:
                    los = test_loss[1]
                    if temp_loss is None:
                        temp_loss = test_loss[1]
                    if temp_loss > los:
                        self.best_model = self.model_nn
                    print(f'Epoch: {epoch:03d}, Train Loss: {train_loss[1]}, Test Loss: {test_loss[1]}')
        return self

    def train(self):
        self.model_nn.train()
        for data in self.train_loader:
            out = self.model_nn(data)
            # print(out.size())
            # print(data.y.size())
            loss = self.criterion(out, data.y)
            loss.backward()
            self.optimizer.step()
            self.optimizer.zero_grad()

    def test(self, dataloader):
        self.model_nn.eval()
        if self.dataset.task == 'classification':
            correct = 0
            for data in dataloader:
                out = self.model_nn(data)
                pred = out.argmax(dim=1)
                correct += int((pred == data.y).sum())
            return out, pred.numpy(), correct / len(dataloader.dataset)
        else:
            self.model_nn.eval()
            for data in dataloader:
                out = self.model_nn(data)
                loss = self.criterion(out, data.y)
            return out, loss

    def eval(self):
        self.best_model.eval()
        if self.evaluator.functions:
            eval_keys = self.evaluator.functions.keys()
            correct = 0
            truth = np.array([])
            preds = np.array([])
            for data in self.test_loader:
                out = self.best_model(data)
                pred = out.argmax(dim=1)
                correct += int((pred == data.y).sum())
                truth = np.append(truth, data.y.numpy())
                preds = np.append(preds, pred.numpy())
            # return out, pred.numpy(), correct / len(dataloader.dataset)
            for eval_key in eval_keys:
                eval_function = self.evaluator.functions.get(eval_key)
                print(eval_key + ": " + str(eval_function(truth, preds)))
        else:
            print("No eval functions passed")

    def create_molecular_model(self):
        model = MolecularModel()
        model.descriptors = self.dataset.featurizer
        model.doa = self.doa
        model.model = self.best_model
        model.X = self.dataset.X
        model.Y = self.dataset.y
        model.library = ['torch_geometric', 'torch']
        model.version = [torch_geometric.__version__, torch.__version__]
        model.jaqpotpy_version = config.version
        model.modeling_task = self.dataset.task
        # model.external_feats = self.dataset.external
        return model

#
# class MolecularTorch(Model):
#
#     def __init__(self, dataset: TorchGraphDataset, model_nn: torch.nn.Module
#                  , doa: DOA = None
#                  , eval: Evaluator = None, preprocess: Preprocesses = None
#                  , dataLoaderParams: Any = None, epochs: int = None
#                  , criterion: torch.nn.Module = None, optimizer: Any = None
#                  , train_batch: int = 50, test_batch: int = 50, log_steps: int = 1):
#         # super(InMemMolModel, self).__init__(dataset=dataset, doa=doa, model=model)
#         self.dataset: TorchGraphDataset = dataset
#         self.model_nn = model_nn
#         self.doa = doa
#         self.doa_m = None
#         self.external = None
#         self.evaluator: Evaluator = eval
#         self.preprocess: Preprocesses = preprocess
#         self.train_batch = train_batch
#         self.test_batch = test_batch
#         self.trainDataLoaderParams = {'batch_size': self.train_batch, 'shuffle': False, 'num_workers': 0}
#         self.testDataLoaderParams = {'batch_size': self.test_batch, 'shuffle': False, 'num_workers': 0}
#         self.epochs = epochs
#         self.criterion = criterion
#         self.trained_model = None
#         self.model_fitted: MolecularModel = None
#         self.optimizer = optimizer
#         self.train_loader = None
#         self.test_loader = None
#         self.log_steps = log_steps
#         self.best_model = None
#         # torch.multiprocessing.freeze_support()
#
#     def __call__(self, smiles):
#         self
#
#     def fit(self):
#         if self.doa:
#             if self.doa.__name__ == 'SmilesLeverage':
#                 self.doa_m = self.doa.fit(self.dataset.smiles_strings)
#             else:
#                 print("Only SmilesLeverage is suported for graph models")
#         if self.dataset.df is not None:
#             pass
#         else:
#             self.dataset.create()
#         if self.evaluator is not None:
#             if self.evaluator.dataset.df is not None:
#                 pass
#             else:
#                 self.evaluator.dataset.create()
#         device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#         self.model_fitted = MolecularModel()
#         self.model_nn.to(device)
#         self.train_loader = DataLoader(dataset=self.dataset.df, **self.trainDataLoaderParams)
#         self.test_loader = DataLoader(dataset=self.evaluator.dataset.df, **self.testDataLoaderParams)
#         temp_loss = None
#         for epoch in range(1, self.epochs):
#             self.train()
#             train_loss = self.test(self.train_loader)
#             test_loss = self.test(self.test_loader)
#             if epoch % self.log_steps == 0:
#                 if self.dataset.task == "classification":
#                     los = test_loss[2]
#                     if temp_loss is None:
#                         temp_loss = test_loss[2]
#                     if temp_loss < los:
#                         self.best_model = self.model_nn
#                     print(f'Epoch: {epoch:03d}, Train Accuracy: {train_loss[2]}, Test Accuracy: {test_loss[2]}')
#                 else:
#                     los = test_loss[1]
#                     if temp_loss is None:
#                         temp_loss = test_loss[1]
#                     if temp_loss < los:
#                         self.best_model = self.model_nn
#                     print(f'Epoch: {epoch:03d}, Train Loss: {train_loss[1]}, Test Loss: {test_loss[1]}')
#         return self
#
#     def train(self):
#         self.model_nn.train()
#         for data in self.train_loader:
#             out = self.model_nn(data)
#             loss = self.criterion(out, data.y)
#             loss.backward()
#             self.optimizer.step()
#             self.optimizer.zero_grad()
#
#     def test(self, dataloader):
#         self.model_nn.eval()
#         if self.dataset.task == 'classification':
#             correct = 0
#             for data in dataloader:
#                 out = self.model_nn(data)
#                 pred = out.argmax(dim=1)
#                 correct += int((pred == data.y).sum())
#             return out, pred.numpy(), correct / len(dataloader.dataset)
#         else:
#             self.model_nn.eval()
#             for data in dataloader:
#                 out = self.model_nn(data)
#                 loss = self.criterion(out, data.y)
#             return out, loss
#
#     def eval(self):
#         self.best_model.eval()
#         if self.evaluator.functions:
#             eval_keys = self.evaluator.functions.keys()
#             correct = 0
#             truth = np.array([])
#             preds = np.array([])
#             for data in self.test_loader:
#                 out = self.best_model(data)
#                 pred = out.argmax(dim=1)
#                 correct += int((pred == data.y).sum())
#                 truth = np.append(truth, data.y.numpy())
#                 preds = np.append(preds, pred.numpy())
#             # return out, pred.numpy(), correct / len(dataloader.dataset)
#             for eval_key in eval_keys:
#                 eval_function = self.evaluator.functions.get(eval_key)
#                 print(eval_key + ":" + str(eval_function(truth, preds)))
#         else:
#             print("No eval functions passed")


# class MolecularTorch(Model):
#
#     def __init__(self, dataset: TorchGraphDataset, model_nn: torch.nn.Module
#                  , doa: DOA = None
#                  , eval: Evaluator = None, preprocess: Preprocesses = None
#                  , dataLoaderParams: Any = None, epochs: int = None
#                  , criterion: torch.nn.Module = None, optimizer: Any = None
#                  , train_batch: int = 50, test_batch: int = 50, log_steps: int = 1):
#         # super(InMemMolModel, self).__init__(dataset=dataset, doa=doa, model=model)
#         self.dataset: TorchGraphDataset = dataset
#         self.model_nn = model_nn
#         self.doa = doa
#         self.doa_m = None
#         self.external = None
#         self.evaluator: Evaluator = eval
#         self.preprocess: Preprocesses = preprocess
#         self.train_batch = train_batch
#         self.test_batch = test_batch
#         self.trainDataLoaderParams = {'batch_size': self.train_batch, 'shuffle': False, 'num_workers': 0}
#         self.testDataLoaderParams = {'batch_size': self.test_batch, 'shuffle': False, 'num_workers': 0}
#         self.epochs = epochs
#         self.criterion = criterion
#         self.trained_model = None
#         self.model_fitted: MolecularModel = None
#         self.optimizer = optimizer
#         self.train_loader = None
#         self.test_loader = None
#         self.log_steps = log_steps
#         self.best_model = None
#         # torch.multiprocessing.freeze_support()
#
#     def __call__(self, smiles):
#         self
#
#     def fit(self):
#         if self.doa:
#             if self.doa.__name__ == 'SmilesLeverage':
#                 self.doa_m = self.doa.fit(self.dataset.smiles_strings)
#             else:
#                 print("Only SmilesLeverage is suported for graph models")
#         if self.dataset.df is not None:
#             pass
#         else:
#             self.dataset.create()
#         if self.evaluator is not None:
#             if self.evaluator.dataset.df is not None:
#                 pass
#             else:
#                 self.evaluator.dataset.create()
#         device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#         self.model_fitted = MolecularModel()
#         self.model_nn.to(device)
#         # self.train_loader = DataLoader(dataset=self.dataset.df, **self.trainDataLoaderParams)
#         # self.test_loader = DataLoader(dataset=self.evaluator.dataset.df, **self.testDataLoaderParams)
#         self.train_loader = DataLoader(dataset=self.dataset, **self.trainDataLoaderParams)
#         self.test_loader = DataLoader(dataset=self.evaluator.dataset, **self.testDataLoaderParams)
#         temp_loss = None
#         for epoch in range(1, self.epochs):
#             self.train()
#             train_loss = self.test(self.train_loader)
#             test_loss = self.test(self.test_loader)
#             if epoch % self.log_steps == 0:
#                 if self.dataset.task == "classification":
#                     los = test_loss[2]
#                     if temp_loss is None:
#                         temp_loss = test_loss[2]
#                     if temp_loss < los:
#                         self.best_model = self.model_nn
#                     print(f'Epoch: {epoch:03d}, Train Accuracy: {train_loss[2]}, Test Accuracy: {test_loss[2]}')
#                 else:
#                     los = test_loss[1]
#                     if temp_loss is None:
#                         temp_loss = test_loss[1]
#                     if temp_loss < los:
#                         self.best_model = self.model_nn
#                     print(f'Epoch: {epoch:03d}, Train Loss: {train_loss[1]}, Test Loss: {test_loss[1]}')
#         return self
#
#     def train(self):
#         self.model_nn.train()
#         for data in self.train_loader:
#             out = self.model_nn(data)
#             loss = self.criterion(out, data.y)
#             loss.backward()
#             self.optimizer.step()
#             self.optimizer.zero_grad()
#
#     def test(self, dataloader):
#         self.model_nn.eval()
#         if self.dataset.task == 'classification':
#             correct = 0
#             for data in dataloader:
#                 out = self.model_nn(data)
#                 pred = out.argmax(dim=1)
#                 correct += int((pred == data.y).sum())
#             return out, pred.numpy(), correct / len(dataloader.dataset)
#         else:
#             self.model_nn.eval()
#             for data in dataloader:
#                 out = self.model_nn(data)
#                 loss = self.criterion(out, data.y)
#             return out, loss
#
#     def eval(self):
#         self.best_model.eval()
#         if self.evaluator.functions:
#             eval_keys = self.evaluator.functions.keys()
#             correct = 0
#             truth = np.array([])
#             preds = np.array([])
#             for data in self.test_loader:
#                 out = self.best_model(data)
#                 pred = out.argmax(dim=1)
#                 correct += int((pred == data.y).sum())
#                 truth = np.append(truth, data.y.numpy())
#                 preds = np.append(preds, pred.numpy())
#             # return out, pred.numpy(), correct / len(dataloader.dataset)
#             for eval_key in eval_keys:
#                 eval_function = self.evaluator.functions.get(eval_key)
#                 print(eval_key + ":" + str(eval_function(truth, preds)))
#         else:
#             print("No eval functions passed")