from flask_login import AnonymousUserMixin
from flask_login import UserMixin as BaseUserMixin

import backend.models as md


class UserMixin(BaseUserMixin):
    def has_role(self, role):
        """Checks if the user has a given role. `role` can be a string or a Role instance"""
        if isinstance(role, str):
            return role in (role.name for role in self.roles)
        else:
            return role in self.roles

    def add_role(self, role):
        """Add `role` to this user."""
        if isinstance(role, str):
            role = md.Role.query.filter_by(name=role).first()

        if role is not None:
            self.roles.append(role)
        md.db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def has_role(self, role):
        """Returns `False`."""
        return False
