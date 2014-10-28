from TrainingSet import TrainingSet
from TestSet import TestSet
import cPickle as pickle
import os.path

class Data:
    # TODO: reload=True since there is unsolved strange memory behaviour when loading from cache with pickle
    def __init__(self, inverse=True, closure=True):
        self.inverse = inverse
        self.closure = closure

        self._load_new()

    def _load_new(self):
        self.training = TrainingSet(self.inverse, self.closure, "data/training/TBAQ-cleaned/AQUAINT/", "data/training/TBAQ-cleaned/TimeBank/")
        self.test = TestSet(self.inverse, self.closure, True, "data/test/te3-platinum/")
