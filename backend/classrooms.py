class Address:

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return str(self)

    @staticmethod
    def __str__(self):
        location = ''
        if self.address['address_2'] != '':
            location += self.address['address_2']
        if self.address['address_1'] != '':
            if location != '' and ['address_2'] != '':
                location += ' ' + self.address['address_1']
            else:
                location += '\n' + self.address['address_1']
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
        self.infos = kwargs

    def __str__(self):
        return str(self.infos)

    def __repr__(self):
        return str(self)
