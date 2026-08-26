"""add_relation_and_document_access_to_family_connection

Adds `relation` (the requester's declared relationship) and
`document_access_enabled` (cross-member medical record access toggle) columns
to the family_connection table.

Revision ID: 002_family_relation_doc_access
Revises: 001_extended_user_profile
Create Date: 2026-08-26
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "002_family_relation_doc_access"
down_revision = "001_extended_user_profile"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Relation type declared by the requester (spouse, parent, child, sibling, etc.)
    op.add_column(
        "family_connection",
        sa.Column("relation", sa.String(20), nullable=False, server_default="other"),
    )
    # Mutual medical document access flag (default enabled)
    op.add_column(
        "family_connection",
        sa.Column("document_access_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )


def downgrade() -> None:
    op.drop_column("family_connection", "document_access_enabled")
    op.drop_column("family_connection", "relation")
