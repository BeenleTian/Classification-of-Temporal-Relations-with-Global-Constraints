class Event(object):
    def __init__(self, eid, eiid, text_obj, text, sentence, position_in_sentence, e_class, tense, aspect, polarity, pos, modality):
        self.eid = eid
        self.eiid = eiid
        self.parent_node = text_obj
        self.text = text
        self.sentence = sentence
        self.position_in_sentence = position_in_sentence

        # As definied in xml data
        self.e_class = e_class
        self.tense = tense
        self.aspect = aspect
        self.polarity = polarity
        self.pos = pos
        self.modality = modality
