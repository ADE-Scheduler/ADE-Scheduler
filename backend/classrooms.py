class Address:

    def __init__(self, **kwargs):
        """
        Creates address object.
        :param kwargs: dict with minimal entries:
            - address1
            - address2
            - zipCode
            - city
            - country
        """
        self.address = kwargs

    def __repr__(self):
        return str(self)

    def __str__(self):
        location = ''
        if self.address['address2'] != '':
            location += self.address['address2']
        if self.address['address1'] != '':
            if location != '' and ['address2'] != '':
                location += ' ' + self.address['address1']
            else:
                location += '\n' + self.address['address1']
        if self.address['zipCode'] != '':
            location += '\n' + self.address['zipCode']
        if self.address['city'] != '':
            if location != '' and self.address['zipCode'] != '':
                location += ' ' + self.address['city']
            else:
                location += '\n' + self.address['city']
        if self.address['country'] != '':
            location += '\n' + self.address['country']

        return location


class Classroom:

    def __init__(self, **kwargs):
        """
        Creates classroom object.
        :param kwargs: dict with minimal entries:
            - address
            - name
            - id
        """
        self.infos = kwargs

    def __str__(self):
        return str(self.infos['address'])

    def __repr__(self):
        id = self.infos['id']
        name = self.infos['name']
        return f'{id}: {name}'
