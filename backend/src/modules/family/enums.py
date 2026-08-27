"""Family module enums."""

import enum


class RelationType(str, enum.Enum):
    """Relationship type declared by the requester when sending a family connection request."""

    SPOUSE = "spouse"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    GRANDPARENT = "grandparent"
    GRANDCHILD = "grandchild"
    OTHER = "other"
