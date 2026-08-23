"""add_extended_user_profile_fields

Adds health profile, KYC identity, address, and contact fields to the user table
for the hospital signup flow.

Revision ID: 001_extended_user_profile
Revises: None
Create Date: 2026-08-23
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001_extended_user_profile"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Health profile ────────────────────────────────────────────────────────
    op.add_column("user", sa.Column("date_of_birth", sa.Date(), nullable=True))
    op.add_column("user", sa.Column("gender", sa.String(10), nullable=True))
    op.add_column("user", sa.Column("blood_group", sa.String(5), nullable=True))
    op.add_column("user", sa.Column("height_cm", sa.Float(), nullable=True))
    op.add_column("user", sa.Column("weight_kg", sa.Float(), nullable=True))

    # ── KYC / Identity ────────────────────────────────────────────────────────
    op.add_column("user", sa.Column("kyc_document_type", sa.String(20), nullable=True))
    op.add_column("user", sa.Column("kyc_document_number", sa.String(50), nullable=True))
    op.create_unique_constraint("uq_user_kyc_document_number", "user", ["kyc_document_number"])
    op.create_index("ix_user_kyc_document_number", "user", ["kyc_document_number"], unique=True)

    # ── Address ───────────────────────────────────────────────────────────────
    op.add_column("user", sa.Column("address_line1", sa.String(120), nullable=True))
    op.add_column("user", sa.Column("address_line2", sa.String(120), nullable=True))
    op.add_column("user", sa.Column("city", sa.String(60), nullable=True))
    op.add_column("user", sa.Column("state", sa.String(60), nullable=True))
    op.add_column("user", sa.Column("pincode", sa.String(10), nullable=True))
    op.add_column("user", sa.Column("country", sa.String(60), nullable=True, server_default="India"))

    # ── Contact ───────────────────────────────────────────────────────────────
    op.add_column("user", sa.Column("phone_number", sa.String(15), nullable=True))
    op.create_unique_constraint("uq_user_phone_number", "user", ["phone_number"])
    op.create_index("ix_user_phone_number", "user", ["phone_number"], unique=True)

    op.add_column("user", sa.Column("emergency_contact_name", sa.String(60), nullable=True))
    op.add_column("user", sa.Column("emergency_contact_phone", sa.String(15), nullable=True))


def downgrade() -> None:
    # ── Contact ───────────────────────────────────────────────────────────────
    op.drop_index("ix_user_phone_number", table_name="user")
    op.drop_constraint("uq_user_phone_number", "user", type_="unique")
    op.drop_column("user", "emergency_contact_phone")
    op.drop_column("user", "emergency_contact_name")
    op.drop_column("user", "phone_number")

    # ── Address ───────────────────────────────────────────────────────────────
    op.drop_column("user", "country")
    op.drop_column("user", "pincode")
    op.drop_column("user", "state")
    op.drop_column("user", "city")
    op.drop_column("user", "address_line2")
    op.drop_column("user", "address_line1")

    # ── KYC / Identity ────────────────────────────────────────────────────────
    op.drop_index("ix_user_kyc_document_number", table_name="user")
    op.drop_constraint("uq_user_kyc_document_number", "user", type_="unique")
    op.drop_column("user", "kyc_document_number")
    op.drop_column("user", "kyc_document_type")

    # ── Health profile ────────────────────────────────────────────────────────
    op.drop_column("user", "weight_kg")
    op.drop_column("user", "height_cm")
    op.drop_column("user", "blood_group")
    op.drop_column("user", "gender")
    op.drop_column("user", "date_of_birth")
