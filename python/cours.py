############## METADATA ################
Q1 = True
Q2 = False
CM = True
TP = False
########################################

class Cours:
    def __init__(self, name, code, professor, nb_weeks=13, Q=Q2, weight=1, type_course=CM):
        """
        Represents a given course, with the name and code of the course,
        the professor and the mail adress of the professor
        example:
        - name: "Automatique lineaire"
        - code: "LINMA1510"
        - professor: Professor or list of Professors
        - nb_weeks: the duration of the course, starting at S1
        """
        self.name = name
        self.code = code
        self.professor = professor
        self.slots = {}
        self.Q = Q
        self.nb_weeks = nb_weeks
        self.type_course = type_course
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
        return self.code + ": " + self.name + ", " + str(self.professor)

    def __eq__(self, value):
        if not isinstance(value, Cours):
            raise TypeError
        return self.code == value.code and self.type_course == value.type_course

    def scheduling(self):
        s = str(self)
        s += "Below all the possibilities of the course " + self.code + ":\n\n"
        for i in range(1, self.nb_weeks + 1):
            s += "================= S" + str(i) + " =================\n"
            for j in self.slots[i]:
                s += str(j) + "\n"
            s += "\n"
        print(s)


class CM(Cours):
    def __init__(self, name, code, professor, nb_weeks=13, Q=Q2, weight=1):
        super().__init__(name, code, professor, nb_weeks=nb_weeks, Q=Q, weight=weight, type_course=CM)


class TP(Cours):
    def __init__(self, name, code, professor, nb_weeks=13, Q=Q2, weight=1):
        super().__init__(name, code, professor, nb_weeks=nb_weeks, Q=Q, weight=weight, type_course=TP)
