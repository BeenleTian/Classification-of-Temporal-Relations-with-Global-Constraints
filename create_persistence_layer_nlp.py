from helper.nlp_persistence import Nlp_persistence
from TrainingSet import TrainingSet
from TestSet import TestSet
import logging

# Setting up logging
logging.basicConfig(filename='creating_nlp_file.log',level=logging.DEBUG)

# Preprocessing nlp information for all relations
training = TrainingSet(False, "data/training/TBAQ-cleaned/AQUAINT/", "data/training/TBAQ-cleaned/TimeBank/")
test = TestSet("data/test/te3-platinum/")

persistence = Nlp_persistence(fallback=True)
persistence.create_persistence(training.relations + test.relations)
