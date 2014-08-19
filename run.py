from TrainingSet import TrainingSet
from TestSet import TestSet
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from feature.lemma import Lemma
from feature.token import Token
import logging
import sys

if __name__ == "__main__":
    # Set log level
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)

    # Creating xml mapping objects from scratch with "False" as first argument
    load = False

    if load:
        print "Loading training and test set"
    else:
        print "Creating training and test set"

    training = TrainingSet(load, "data/training/TE3-Silver-data/", "data/training/TBAQ-cleaned/AQUAINT/", "data/training/TBAQ-cleaned/TimeBank/")
    test = TestSet(load, "data/test/te3-platinum/")

    # Must be called before training.get_classification_data_event_event()
    lemma = Lemma(training)
    token = Token(training)

    if load:
        print "Done loading training and test set"
    else:
        print "Done creating training and test set"
    print

    print "Creating features for the training data"
    X_train, y_train = training.get_classification_data_event_event(lemma, token)
    print "Done creating features"
    print

    # Train a random forest classifier
    print "Train the classifier"
    rf = RandomForestClassifier(n_jobs=2, n_estimators=5)
    rf.fit(X_train, y_train)
    print "Done training the classifier"
    print

    print "Creating features for the test data"
    r_ee = test.classify_existing_event_event_relations(rf, lemma, token)
    print "Event-event : " + str(r_ee) + "%"
    r_et = test.classify_existing_event_timex_relations(rf, lemma, token)
    print "Event-timex: " + str(r_et) + "%"

    print "Creating the evaluation data"
    test.create_evaluation_files()
