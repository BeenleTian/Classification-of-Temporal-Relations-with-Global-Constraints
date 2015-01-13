from Set import Set
from Feature import Feature
import numpy
from feature.exception import FailedProcessingFeature
from Constraints import Constraints

class TestSet(Set):
    def __init__(self, *corpora):
        # No inverses and closures in the test set
        Set.__init__(self, False, False, False, *corpora)
        self.relations_optimized = []

    def create_evaluation_files(self):
        for text_obj in self.text_objects:
            text_obj.generate_output_tml_file()

    def create_confidence_scores(self, classifier_event_event, classifier_event_timex):
        # Apply the global constraints to all relations of each text object
        for text_obj in self.text_objects:
            # Create all confidence scores between every relation
            text_obj.create_confidence_scores(classifier_event_event, classifier_event_timex)

    def apply_global_model(self):
        changed = 0
        no_changes = 0
        ee_changed = 0
        et_changed = 0
        improvement = 0
        degradation = 0
        changes_with_no_effect = 0

        for text_obj in self.text_objects:
            # Create all optimal relations for text object
            ilp = Constraints(text_obj)
            text_obj.relations_plain_optimized = ilp.get_best_set()
            self.relations_optimized += text_obj.relations_plain_optimized

            tmp_changed, tmp_ee_changed, tmp_et_changed, tmp_improvement, tmp_degradation, tmp_changes_with_no_effect = ilp.get_number_of_relations_changed()
            changed += tmp_changed
            ee_changed += tmp_ee_changed
            et_changed += tmp_et_changed
            improvement += tmp_improvement
            degradation += tmp_degradation
            changes_with_no_effect += tmp_changes_with_no_effect

        print "Global model changed %s relations" % changed
        print "%s relations were event-event relations" % ee_changed
        print "%s relations were event-timex relations" % et_changed
        print "The global model lead to %s improvements" % improvement
        print "The global model introduced %s new misclassifications" % degradation
        print "The global model changed %s relations wrongly which had no effect since they were already wrong" % changes_with_no_effect

    def get_event_event_targets(self):
        targets = []
        for relation in self.relations_optimized:
            if relation.is_event_event():
                targets.append(relation.relation_type)

        return targets

    def get_event_timex_targets(self):
        targets = []
        for relation in self.relations_optimized:
            if relation.is_event_timex():
                targets.append(relation.relation_type)

        return targets
