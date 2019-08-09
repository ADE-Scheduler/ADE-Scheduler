from event import *
from itertools import chain
from operator import itemgetter

class Course:
    def __init__(self, code, name, weight=1):
        # A Course is defined by its code and its name
        self.code = code
        self.name = name
        self.weight = weight

        # A course can be composed of 5 different events: CM, TP, Exam, Oral and Other
        # Each event is classed by week
        self.CM = [[] for i in range(53)]       # EventCM
        self.TP = [[] for i in range(53)]       # EventTP
        self.E = [[] for i in range(53)]        # EventEXAM
        self.O = [[] for i in range(53)]        # EventORAL
        self.Other = [[] for i in range(53)]    # EventOTHER

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.code == other.code
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.code + ": " + self.name

    def getweek(self, week):
        # Bon on gère pas encore les "Other".. trop chiant
        return self.CM[week], self.TP[week], self.E[week], self.O[week]

    def getSummary(self, weeks='ALL'):
        if weeks == 'ALL':
            w = chain(self.CM, self.TP, self.E, self.O, self.Other) # [CM from week 1, CM from week 2, ..., TP from week 1, ...]
            e = chain(*w) # [CM1, CM2,... , TP1, ...]
        elif isinstance(weeks, slice):
            w = chain(self.CM[weeks], self.TP[weeks], self.E[weeks], self.O[weeks], self.Other[weeks])
            e = chain(*w)
        else:
            itg = itemgetter(*list(weeks))
            w = chain(itg(self.CM), itg(self.TP), itg(self.E), itg(self.O), itg(self.Other))
            e = chain(*w)
        return set(map(lambda x: x.getId(), e))


    def addEvent(self, event):
        """
        Add an event to this course
        The event is added in the corresponding week
        If the event is already there, it is not added
        """
        week = event.getweek()
        if isinstance(event, EventCM):
            if event not in self.CM[week]:
                self.CM[week].append(event)
                return True
            else:
                return False
        elif isinstance(event, EventTP):
            if event not in self.TP[week]:
                self.TP[week].append(event)
                return True
            else:
                return False
        elif isinstance(event, EventEXAM):
            if event not in self.E[week]:
                self.E[week].append(event)
                return True
            else:
                return False
        elif isinstance(event, EventORAL):
            if event not in self.O[week]:
                self.O[week].append(event)
                return True
            else:
                return False
        elif isinstance(event, EventOTHER):
            if event not in self.Other[week]:
                self.Other[week].append(event)
                return True
            else:
                return False
        else:
            raise TypeError

    def removeEvent(self, event):
        """
        Removes an event from this course
        """
        week = event.getweek()
        if isinstance(event, EventCM):
            if event not in self.CM[week]:
                return False
            else:
                self.CM[week].remove(event)
                return True
        if isinstance(event, EventTP):
            if event not in self.TP[week]:
                return False
            else:
                self.TP[week].remove(event)
                return True
        if isinstance(event, EventEXAM):
            if event not in self.E[week]:
                return False
            else:
                self.E[week].remove(event)
                return True
        if isinstance(event, EventORAL):
            if event not in self.O[week]:
                return False
            else:
                self.O[week].remove(event)
                return True
        if isinstance(event, EventOTHER):
            if event not in self.Other[week]:
                return False
            else:
                self.Other[week].remove(event)
                return True
        else:
            raise TypeError
