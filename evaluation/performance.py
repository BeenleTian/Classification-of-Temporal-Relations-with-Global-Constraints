from Data import Data
from System import System
from TrainingSet import TrainingSet
import time
import pickle
from os import listdir
import matplotlib.pyplot as plt
import sys
from collections import OrderedDict

STEPS_RELATIONS = 20

def measure_time(data):
    start = time.time()

    system = System(data)
    system.use_all_features()
    system.use_feature_selection()

    system.create_features()
    system.train()
    system.save_classifiers()

    system.eval()
    system.create_confidence_scores()
    system.apply_global_model()

    end = time.time()

    return end-start

def create_data():
    training_files = _get_training_files()
    series_training_files = _get_series_of_files(training_files)

    for series in series_training_files:
        data = Data(False, False)
        data.training = TrainingSet(False, False, *series)

        yield data

def _get_training_files():
    aquaint = listdir("data/training/TBAQ-cleaned/AQUAINT/")
    aquaint = ["data/training/TBAQ-cleaned/AQUAINT/"+f for f in aquaint]
    timebank = listdir("data/training/TBAQ-cleaned/TimeBank/")
    timebank = ["data/training/TBAQ-cleaned/TimeBank/"+f for f in timebank]

    return aquaint + timebank

def _get_series_of_files(training_files):
    length = len(training_files)
    len_part = length/STEPS_RELATIONS

    lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]

    parts = lol(training_files, len_part)

    series = []
    for i in range(STEPS_RELATIONS):
        s = []
        for j in range(i+1):
            s += parts[j]

        series.append(s)

    return series

def get_number_of_training_relations(data):
    return len(data.training.relations)

def save_time_relations_data():
    rels = []
    times = []

    for data in create_data():
        num_relations = get_number_of_training_relations(data)
        time = measure_time(data)
        print time

        rels.append(num_relations)
        times.append(times)

    pickle.dump((rels,times), open("rels_times.p", "wb"))

def plot(rels, times):
    plt.plot(rels, times)

    plt.xlabel("Number of relations")
    plt.ylabel("Time in seconds")
    plt.grid(True)

    plt.savefig("performance.pdf")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "plot":
        rels, times = pickle.load(open("rels_times.p"))
        plot(rels, times)
    else:
        save_time_relations_data()
