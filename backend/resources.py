class Resource:

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return str(self.kwargs)

    def __repr__(self):
        return str(self.kwargs['name'])

    def __hash__(self):
        return hash(self.kwargs)

    def __eq__(self, other):
        return self.kwargs['name'] == other.kwargs['name']

    def get_category(self):
        category = self.kwargs['category']
        if category == 'category5':
            return 'course'
        elif category == 'trainee':
            return 'course-combo'
        elif category == 'classroom':
            return 'classroom'
        else:
            return category
