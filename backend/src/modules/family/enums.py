"""Family module enums."""

from enum import StrEnum


class RelationType(StrEnum):
    """Relationship type declared by the requester when sending a family connection request."""

    SPOUSE = "spouse"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    GRANDPARENT = "grandparent"
    GRANDCHILD = "grandchild"
    OTHER = "other"
