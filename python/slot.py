from datetime import datetime, timedelta
from static_data import *

############ CHANGING DATA #############
# One of the two is useless
date_spring_b = '06/04/2019'
date_spring_e = '19/04/2019'
########################################

############## METADATA ################
time_q1_q2 = '00h00'
start_q1_week = datetime.strptime(Q1_START_DATE+'-'+time_q1_q2, '%d/%m/%Y-%Hh%M')
week_q1 = start_q1_week.isocalendar()[1]
start_q2_week = datetime.strptime(Q2_START_DATE+'-'+time_q1_q2, '%d/%m/%Y-%Hh%M')
week_q2 = start_q2_week.isocalendar()[1]

start_spring = datetime.strptime(SPING_BREAK_START_DATE+'-'+time_q1_q2, '%d/%m/%Y-%Hh%M')

Q1 = True
Q2 = False
########################################

class Slot:
    """
    Representing a scheduling slot: it is used to represent the different (if any)
    possible outcomes of a same CM/TP. 
    Example of use:
    - date: a date object representing the day of the scheduling slot
    - week: the week of the event (in UCLouvain-style: S1, S2, ...)
    - begin: the date and hour when starts the CM/TP of this slot
    - end: the date and hour when ends the CM/TP of this slot
    """

    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
        week = begin.isocalendar()[1]
        # Determine which 'quadrimestre'
        if begin > start_q1_week:
            self.Q = Q1
            self.week = week - week_q1 + 1
        else:
            self.Q = Q2
            if begin > start_spring:
                self.week = week - week_q2 + 1 - 2
            else:
                self.week = week - week_q2 + 1
    
    def overlap(self, other):
        """
        Checks if there is an overlap between the two slots
        if a.begin < b.begin, there is an overlap if b.begin < a.end
        @pre: -
               True if there is an overlap (bad)
               False if there isn't any overlap (good)
        """
        if not type(other) is Slot:
            raise TypeError('The argument is not of type Slot')
        if self.begin < other.begin:
            if self.end <= other.begin:
                return False
            else:
                return True
        else:
            if other.end <= self.begin:
                return False
            else:
                return True

    def __str__(self):
        return "(S" + str(self.week) + ") " + str(self.begin) + " - " + str(self.end)

    def __eq__(self, value):
        """
        Check if two Slot represent the same scheduling
        """
        if type(value) is Slot and self.week == value.week and self.begin == value.begin and self.end == value.end:
            return True
        return False
