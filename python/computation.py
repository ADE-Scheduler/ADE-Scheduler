import itertools as itools

class Computation:
    """
    Class defining the computation of a scheduling.
    For the moment, computed to work for a one-week schedule
    => Class not necessary, but for the moment, it is simpler to do so
    """

    def __init__(self):
        self.courses = []
        self.up_to_date = False
        self.valid = []
        self.working_courses = []

    def add_course(self, course):
        if not course in self.courses:
            self.courses.append(course)
        self.up_to_date = False
    
    def remove_course(self, course):
        if course in self.courses:
            self.courses.remove(course)
        self.up_to_date = False
    
    def add_valid_schedule(self, schedule):
        """
        Add the valid schedule in valid as a form of dictionnary
        @pre: schedule is a valid schedule
        @post: -
        """
        new_valid = {}
        for i, course in enumerate(self.courses):
            new_valid[course.code] = schedule[i]
        self.valid.append(new_valid)

    def compute(self, week):
        """
        Computes all the valids schedulings for the given courses
        in self.courses, where each course has his own slots
        FOR THE MOMENT: input:
        - week: the week (UCLouvain-like) where the computation
        has to be done.
        ///////////////////////////
        ||WORKS ONLY FOR ONE WEEK||
        \\\\\\\\\\\\\\\\\\\\\\\\\\\\
        ---------------------------------------------------------
        A 'valid' scheduling is one which has no conflict for all
        the courses (CM/APE).
        TO DO: preferences

        @post: 
        * a list of dictionnaries, where each item is a 
        valid schedule. Each dictionnary has the form code:slot :
            - code is the code of the course (e.g. 'LINMA1510')
            - slot is the slot object (of class Slot)
        * working_courses: all the courses listed for the week
        week

        /!\ The dictionnary is only computed if there is a change
            since the last computation
        """
        
        # No change since last time
        if self.up_to_date:
            return self.valid, self.working_courses
        
        # Reset the valid, since changes
        self.valid = []
        self.working_courses = []

        all_slots = []
        for c in self.courses:
            l = c.slots[week]
            if len(l) > 0:
                all_slots.append(l)
                self.working_courses.append(c)
        
        """
        for i in all_slots:
            for j in i:
                print(j)
            print('----')
        
        for i in self.working_courses:
            print(i)
        """
        # Computing the permutations based on the slots
        permutations = list(itools.product(*all_slots))

        # Looping through permutations
        for perm in permutations:
            # Looping through the slots of perm, checking if valid
            overlap = False # Stop the loop if there is an overlap

            """
            This method can be improved !
            Idea: cheking thanks to Python build-in methods if there exists any two
            copies of a slot in the list
            Requires: permute the definition of Slot.__eq__ and Slot.overlap
            /!\ Doing so will break the methods: Cours.add_slot and Cours.remove_slot
                because it uses the actual __eq__ method to check if two slot are identical
                to avoid duplicates in the list
            """
            for i in range(len(perm)-1):
                if overlap:
                    break
                for j in range(i+1, len(perm)):
                    if perm[i].overlap(perm[j]):
                        overlap = True
                        break
            # No overlap: it is a valid schedule
            if not overlap:
                self.add_valid_schedule(perm)
        
        self.up_to_date = True
        return self.valid, self.working_courses
