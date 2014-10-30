import os
from lxml import etree
from lxml.etree import tostring
from itertools import chain
from parsexml.event import Event
from parsexml.relation import Relation
from parsexml.sentence import Sentence
from parsexml.timex import Timex
from parsexml.relationtype import RelationType
from parsexml.text_structure import Text_structure
from helper.closure import Closure
import re

class Parser(object):
    def __init__(self, filename, text_obj, full_closure=False):
        self.filename = filename
        self.text_obj = text_obj
        self.text = None
        self.events = None
        self.timex = None
        self.relations = None
        self.inversed_relations = None
        self.closure_relations = None
        self.text_structure = None
        self.full_closure = full_closure

        self._parse()

    def get_text(self):
        return self.text

    def get_events(self):
        return self.events

    def get_timex(self):
        return self.timex

    def get_relations(self):
        return self.relations

    def get_text_structure(self):
        return self.text_structure

    def get_entities_order(self):
        return self.text_structure.get_entities_ordered()

    def _get_closure_obj(self, relation_type):
        if self.full_closure:
            closure = Closure(self.text_obj, relation_type, transitives_of_transitives=True)
        else:
            closure = Closure(self.text_obj, relation_type)

        return closure

    def get_closured_relations(self):
        closure_relations = []

        # Create temporal closures for BEFORE
        closure = self._get_closure_obj(RelationType.BEFORE)
        closure_relations += closure.get_closure_relations()

        # Create temporal closures for AFTER
        closure = self._get_closure_obj(RelationType.AFTER)
        closure_relations += closure.get_closure_relations()

        # Create temporal closures for INCLUDES
        closure = self._get_closure_obj(RelationType.INCLUDES)
        closure_relations += closure.get_closure_relations()

        # Create temporal closures for IS_INCLUDED
        closure = self._get_closure_obj(RelationType.IS_INCLUDED)
        closure_relations += closure.get_closure_relations()

        # Create temporal closures for DURING
        closure = self._get_closure_obj(RelationType.DURING)
        closure_relations += closure.get_closure_relations()

        # Remove timex-timex closures
        closure_relations = [closure for closure in closure_relations if type(closure.source) is not Timex and type(closure.target) is not Timex]

        # Remove closure relations which already exist
        closure_relations = [closure for closure in closure_relations if closure not in self.relations]

        # Append to internal relations, so that when generating other relations, we consider the relations here
        self.closure_relations = closure_relations

        return closure_relations

    def get_inversed_relations(self):
        relations = self.text_obj.relations
        inversed_relations = []

        for relation in relations:
            # Switching source and target and using inverse of relation
            if relation.relation_type == RelationType.AFTER:
                # Switching AFTER to BEFORE
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.BEFORE)
            elif relation.relation_type == RelationType.BEFORE:
                # Switching BEFORE to AFTER
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.AFTER)
            elif relation.relation_type == RelationType.INCLUDES:
                # Switching INCLUDES to IS_INCLUDED
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.IS_INCLUDED)
            elif relation.relation_type == RelationType.IS_INCLUDED:
                # Switching IS_INCLUDED to INCLUDES
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.INCLUDES)
            elif relation.relation_type == RelationType.ENDS:
                # Switching ENDS to ENDED_BY
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.ENDED_BY)
            elif relation.relation_type == RelationType.ENDED_BY:
                # Switching ENDED_BY to ENDS
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.ENDS)
            elif relation.relation_type == RelationType.DURING:
                # Switching DURING to DURING_INV
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.DURING_INV)
            elif relation.relation_type == RelationType.DURING_INV:
                # Switching DURING_INV to DURING
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.DURING)
            elif relation.relation_type == RelationType.IAFTER:
                # Switching IAFTER to IBEFORE
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.IBEFORE)
            elif relation.relation_type == RelationType.IBEFORE:
                # Switching IBEFORE to IAFTER
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.IAFTER)
            elif relation.relation_type == RelationType.BEGINS:
                # Switching BEGINS to BEGUN_BY
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.BEGUN_BY)
            elif relation.relation_type == RelationType.BEGUN_BY:
                # Switching BEGUN_BY to BEGINS
                inverse_rel = Relation(relation.lid, self.text_obj, relation.target, relation.source, RelationType.BEGINS)
            else:
                continue

            # Adding relation if it does not exist yet
            if not inverse_rel in self.relations:
                inversed_relations.append(inverse_rel)

        # Append to internal relations, so that when generating closure relations, we consider those relations here
        self.inversed_relations = inversed_relations

        return inversed_relations

    def _produce_none_relations(self):
        """Produce a NONE-relation between all pairs of events which don't share a relation."""
        print "Producing NONE-relations"
        relations = self.relations
        events = self.events
        none_relations = []

        for source in events:
            for target in events:
                new_relation = Relation("NONE", self.text_obj, source, target, RelationType.NONE)
                print new_relation

                if new_relation in relations:
                    continue
                else:
                    none_relations.append(new_relation)

        self.relations = self.relations + none_relations

        print "Finished producing NONE-relations"

    def produce_relations(self):
        self._produce_inverse_relations()
        #self._produce_closure_relations()

        # TODO: Trying out if adding NONE relations between pairs of events with no relationship helps the classifier or not
        #self._produce_none_relations()

    def _parse(self):
        """Mapping xml data to python objects."""
        tree = etree.parse(self.filename)
        root_node = tree.getroot()

        text_node = root_node.find("TEXT")

        # Get text
        self.text = self._extract_text(text_node)

        # Get and create Event objects
        self.events = self._get_and_create_event_objects(text_node, root_node)

        # Get and create Timex objects
        self.timex = self._get_and_create_timex_objects(text_node, root_node)

        # Create Relation objects and link them
        self.relations = self._get_and_create_relation_objects(root_node)

        # Build text structure. Must be called last.
        self.text_structure = self._get_and_build_text_structure()

    def _stringify_children(self, node):
        # Transfer sub tree into string
        text_with_tags = tostring(node)

        # Remove tags
        regex = re.compile(r"<.*?>")
        text = re.sub(r"<.*?>", "", text_with_tags)

        return text

    def _extract_text(self, node):
        text = self._stringify_children(node)
        return text

    def _get_and_create_event_objects(self, text_node, root_node):
        events = []

        for instance in root_node.iterdescendants("MAKEINSTANCE"):
            instance_eid = instance.get("eventID")
            eiid = instance.get("eiid")
            tense = instance.get("tense")
            aspect = instance.get("aspect")
            polarity = instance.get("polarity")
            pos = instance.get("pos")
            modality = instance.get("modality")


            # Get text, sentence, position in sentence and class for event
            text = None
            sentence = None
            e_class = None
            pos_in_sentence = None
            for event in text_node.iterdescendants("EVENT"):
                eid = event.get("eid")
                if instance_eid == eid:
                    text = event.text

                    # Getting surrounding sentence
                    sentence = Sentence(event, self.text_obj.filename)
                    pos_in_sentence = sentence.get_position(event.text)

                    e_class = event.get("class")
                    break

            # Create Event object or append new eiid
            event_obj = self.find_event_by_eid(events, eid)
            if event_obj:
                # There is already an Event object with this eid but a different eiid
                event_obj.eiid.append(eiid)
            else:
                # There is no Event object yet with this eid
                event_obj = Event(eid, eiid, self.text_obj, text, sentence, pos_in_sentence, e_class, tense, aspect, polarity, pos, modality)
                events.append(event_obj)

        return events

    def find_event_by_eid(self, events, eid):
        for event in events:
            if event.eid == eid:
                return event

        return None

    def _get_and_create_timex_objects(self, text_node, root_node):
        timex_list = []

        for timex in text_node.iterdescendants("TIMEX3"):
            timex_list.append(self._create_timex_object(timex))

        # Also looking for timex in <DCT></DCT>
        dct_node = root_node.find("DCT")
        for timex in dct_node.iterdescendants("TIMEX3"):
            timex_list.append(self._create_timex_object(timex, dct=True))

        return timex_list

    def _create_timex_object(self, timex_node, dct=False):
        # TODO: I should put this directly into parsexml/timex.py
        tid = timex_node.get("tid")
        type = timex_node.get("type")
        value = timex_node.get("value")
        text = timex_node.text
        sentence = Sentence(timex_node, self.text_obj.filename)
        pos_in_sentence = sentence.get_position(timex_node.text)
        parent = self.text_obj

        # Create Timex object
        if dct:
            timex_obj = Timex(tid, type, value, text, sentence, pos_in_sentence, True, parent)
        else:
            timex_obj = Timex(tid, type, value, text, sentence, pos_in_sentence, False, parent)

        return timex_obj

    def _get_and_create_relation_objects(self, root_node):
        """Must be called after _create_event_objects."""
        relations = []

        for relation in root_node.iterdescendants("TLINK"):
            # Only consider event-event and event-timex relations; Ignoring timex-timex
            if not relation.get("eventInstanceID") and not relation.get("relatedToEventInstance"):
                continue

            lid = relation.get("lid")

            # Get relation type as a string
            relation_type = relation.get("relType")

            # Get relation_type_id
            relation_type_id = RelationType.get_id(relation_type)

            if not relation.get("timeID") and not relation.get("relatedToTime"):
                # This is event-event
                source_eiid = relation.get("eventInstanceID")
                target_eiid = relation.get("relatedToEventInstance")

                # Find source event
                source_obj = self.find_event_by_eiid(self.events, source_eiid)
                # Find target event
                target_obj = self.find_event_by_eiid(self.events, target_eiid)

            else:
                # This must be event-timex or timex-event or timex-timex
                target_tid = relation.get("relatedToTime")
                target_eiid = relation.get("relatedToEventInstance")

                source_tid = relation.get("timeID")
                source_eiid = relation.get("eventInstanceID")

                if source_tid and target_eiid:
                    # timex-event
                    source_obj = self.find_timex_by_tid(source_tid)
                    target_obj = self.find_event_by_eiid(self.events, target_eiid)
                elif source_eiid and target_tid:
                    # event-timex
                    source_obj = self.find_event_by_eiid(self.events, source_eiid)
                    target_obj = self.find_timex_by_tid(target_tid)
                elif source_tid and target_tid:
                    # timex-timex
                    source_obj = self.find_timex_by_tid(source_tid)
                    target_obj = self.find_timex_by_tid(target_tid)

            relation_obj = Relation(lid, self.text_obj, source_obj, target_obj, relation_type_id)

            # There are sometimes duplicates which we do not want to have
            if relation_obj not in relations:
                relations.append(relation_obj)

        return relations

    def find_event_by_eiid(self, events, eiid):
        for event in events:
            if eiid in event.eiid:
                return event

        return None

    def find_timex_by_tid(self, tid):
        for timex in self.timex:
            if timex.tid == tid:
                return timex

        return None

    def _get_and_build_text_structure(self):
        """Must be called after all entities got appended."""
        return Text_structure(self.filename, self)
