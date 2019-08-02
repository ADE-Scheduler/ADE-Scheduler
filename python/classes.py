from datetime import datetime, timedelta

############ CHANGING DATA #############
date_q1 = '16/09/2019'
date_q2 = '04/02/2020'

# One of the two is useless
date_spring_b = '06/04/2019'
date_spring_e = '19/04/2019'
########################################

############## METADATA ################
time_q1_q2 = '00h00'
start_q1_week = datetime.strptime(date_q1+'-'+time_q1_q2, '%d/%m/%Y-%Hh%M')
week_q1 = start_q1_week.isocalendar()[1]
start_q2_week = datetime.strptime(date_q2+'-'+time_q1_q2, '%d/%m/%Y-%Hh%M')
week_q2 = start_q2_week.isocalendar()[1]

start_spring = datetime.strptime(date_spring_b+'-'+time_q1_q2, '%d/%m/%Y-%Hh%M')

Q1 = True
Q2 = False
########################################


class Cours:
    def __init__(self, name, code, professor, professor_email, nb_weeks=13, Q=Q2, weight=1):
        """
        Represents a given course, with the name and code of the course,
        the professor and the mail adress of the professor
        example:
        - name: "Automatique lineaire"
        - code: "LINMA1510"
        - professor: "Denis Dochain"
        - professor_email: "denisdochain@uclouvain.be"
        - nb_weeks: the duration of the course, starting at S1
        """
        self.name = name
        self.code = code
        self.professor = professor
        self.professor_email = professor_email
        self.slots = {}
        self.Q = Q
        self.nb_weeks = nb_weeks
        # Here the dictionnary starts at index 1 until nb_weeks included
        for i in range(1, self.nb_weeks + 1):
            self.slots[i] = []
        self.weight = weight

    def add_slot(self, slot):
        """
        Add a slot to this course
        The week where the slot is saved is the week of slot.week
        The slot is not added if it is already in the available slots
        """
        if slot not in self.slots[slot.week]:
            self.slots[slot.week].append(slot)
            return True
        return False

    def remove_slot(self, slot):
        """
        Removes a slot to this course
        """
        if not slot in self.slots[slot.week]:
            return False
        else:
            self.slots[slot.week].remove(slot)
            return True

    def __str__(self):
        return self.code + ": " + self.name + ", " + self.professor + "(" + self.professor_email + ")\n"

    def scheduling(self):
        s = str(self)
        s += "Below all the possibilities of the course " + self.code + ":\n\n"
        for i in range(1, self.nb_weeks+1):
            s += "================= S" + str(i) + " =================\n"
            for j in self.slots[i]:
                s += str(j) + "\n"
            s += "\n"
        print(s)


class CM(Cours):
    pass


class TP(Cours):
    pass


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
        @post: None if other is not of type Slot
               True if there is an overlap (bad)
               False if there isn't any overlap (good)
        """
        if not type(self) == type(other):
            return None
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
        if type(self) == type(value) and self.week == value.week and self.begin == value.begin and self.end == value.end:
            return True
        return False
    


if __name__ == '__main__':
    a = CM("Autolin", "LINMA1510", "Denis Dochain", "denis@uc.c", Q = Q2, nb_weeks = 13)

    ########

    duration = '2h'
    date = '13/05/2019'
    date2 = '14/05/2019'
    time = '14h00'
    time2 = '12h01'

    tdebut = datetime.strptime(date+'-'+time, '%d/%m/%Y-%Hh%M')
    h, m = [0 if x is '' else int(x) for x in duration.split('h')]
    dt = timedelta(hours=h, minutes=m)
    tfin = tdebut + dt

    tdebut2 = datetime.strptime(date2+'-'+time2, '%d/%m/%Y-%Hh%M')
    h, m = [0 if x is '' else int(x) for x in duration.split('h')]
    dt = timedelta(hours=h, minutes=m)
    tfin2 = tdebut2 + dt

    slotA = Slot(tdebut, tfin)
    slotB = Slot(tdebut2, tfin2)
    slotC = Slot(tdebut, tfin)

    a.add_slot(slotA)
    a.add_slot(slotB)
    a.add_slot(slotC)
    a.scheduling()
    print(slotA.overlap(slotB))
