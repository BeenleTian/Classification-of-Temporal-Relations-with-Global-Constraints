from Data import Data
from sklearn import svm
from System import System
import cPickle as pickle
from TrainingSet import TrainingSet
from sklearn.metrics import accuracy_score
import itertools
import numpy as np
from scipy import sparse

def div(data, pieces):
    chunk = int(round(len(data)/float(pieces)))
    result = [data[i:i+chunk] for i in range(0,len(data),chunk)]

    return result

def leave_out(data_chunks, i):
    train = [piece for j, piece in enumerate(data_chunks) if j != i]
    train = list(itertools.chain(*train))

    test = data_chunks[i]

    return (train, test)

def transform_to_list(sparse_matrix):
    return sparse_matrix.toarray()

def transform_to_sparse_matrix(array):
    matrix = sparse.csr_matrix(array[0])

    for row in array[1:]:
        matrix = sparse.vstack((matrix, row))

    return matrix

def kfold(X, y, k):
    accs = []

    for i in range(k):
        clf = svm.SVC(probability=True, kernel="poly", degree=2, C=1000, gamma=0.001, class_weight=None)

        # Divide data into k pieces
        pieces_X = div(X, k)
        pieces_y = div(y, k)

        # Leave out i for testing
        train_X, test_X = leave_out(pieces_X, i)
        train_y, test_y = leave_out(pieces_y, i)

        # Transform back to sparse
        train_X = transform_to_sparse_matrix(train_X)
        test_X = transform_to_sparse_matrix(test_X)

        clf.fit(train_X, train_y)
        predicted = clf.predict(test_X)

        print accuracy_score(test_y, predicted)
        accs.append(accuracy_score(test_y, predicted))

    return np.mean(accs)

data = Data()
data.training = TrainingSet(False, False, "data/training/TBAQ-cleaned/TimeBank/")

system = System(data, ["lemma", "token"])
system.create_features()

X_event_event, y_event_event = system.training_event_event
X_event_timex, y_event_timex = system.training_event_timex

X_event_event = transform_to_list(X_event_event)
X_event_timex = transform_to_list(X_event_timex)
print "Transformed sparse matrices."

print kfold(X_event_event, y_event_event, 5)
print kfold(X_event_timex, y_event_timex, 5)
