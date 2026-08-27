from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from .enums import MedicineType


class MedicationCreate(BaseModel):
    """Schema for creating a new medication entry."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., max_length=200, description="Name of the medicine")
    medicine_type: MedicineType = Field(..., description="Type of the medicine (e.g., Tablet, Syrup)")
    dosage: str = Field(..., max_length=100, description="Dosage (e.g., '500mg', '2 drops')")
    frequency: str = Field(..., max_length=100, description="Frequency (e.g., 'Daily', 'Twice a day')")
    instructions: str | None = Field(default=None, max_length=500, description="Special instructions")
    start_date: date = Field(..., description="When to start taking the medicine")
    end_date: date | None = Field(default=None, description="When to stop taking the medicine")
    reminder_times: list[str] = Field(default_factory=list, description="List of times in HH:MM format")


class MedicationCreateInternal(MedicationCreate):
    user_id: int
    created_by_user_id: int


class MedicationUpdate(BaseModel):
    """Schema for updating an existing medication entry."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=200)
    medicine_type: MedicineType | None = Field(default=None)
    dosage: str | None = Field(default=None, max_length=100)
    frequency: str | None = Field(default=None, max_length=100)
    instructions: str | None = Field(default=None, max_length=500)
    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)
    reminder_times: list[str] | None = Field(default=None)


class MedicationRead(BaseModel):
    """Schema for reading a medication entry."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    medicine_type: MedicineType
    dosage: str
    frequency: str
    instructions: str | None
    start_date: date
    end_date: date | None
    reminder_times: list[str]
    created_by_user_id: int
