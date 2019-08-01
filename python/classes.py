class Cours:
    def __init__(self, name, code, professor, professor_email, nb_weeks=1, weight=1):
        """
        Creates an object Cours, with the name and code of the course,
        the professor and the mail adress of the professor
        example:
        - name: "Automatique lineaire"
        - code: "LINMA1510"
        - professor: "Denis Dochain"
        - professor_email: "denisdochain@uclouvain.be"
        """
        self.name = name
        self.code = code
        self.professor = professor
        self.professor_email = professor_email
        self.slots = {}
        for i in range(1, nb_weeks + 1):
            slots[i] = []
        self.weight = weight

    def add_slot(self, slot, week):
        """
        Add a slot to this course
        """
        if slot not in self.slots[week]:
            self.slots[week].append(slot)
            return True
        return False

    def remove_slot(self, slot, week):
        """
        Removes a slot to this course
        """
        if not slot in self.slots[week]:
            return False
        else:
            self.slots[week].remove(slot)
            return True


class CM(Cours):
    def __init__(self, name, code, professor, professor_email):
        super.__init__(self, name, code, professor, professor_email)

    def add_slot(self, slot, week):
        return super().add_slot(slot, week)(self, slot, week)

    def remove_slot(self, slot, week):
        return super().remove_slot(slot, week)


class TP(Cours):
    def __init__(self, name, code, professor, professor_email, obligatoire=False):
        super.__init__(self, name, code, professor, professor_email)
        self.obligatoire = obligatoire

    def add_slot(self, slot, week):
        return super().add_slot(slot, week)(self, slot, week)

    def remove_slot(self, slot, week):
        return super().remove_slot(slot, week)
