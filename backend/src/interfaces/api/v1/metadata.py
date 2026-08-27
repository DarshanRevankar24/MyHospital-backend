from fastapi import APIRouter

from ....modules.ambulance.enums import AmbulanceType
from ....modules.family.enums import RelationType
from ....modules.hospital.enums import BookingStatus as HospitalBookingStatus
from ....modules.hospital.enums import Speciality
from ....modules.laboratory.enums import CollectionType, TestCategory
from ....modules.medication.enums import MedicineType
from ....modules.pharmacy.enums import DeliveryType, MedicineForm
from ....modules.user.enums import BloodGroupEnum, GenderEnum, KYCDocumentType

router = APIRouter(tags=["Metadata"])


def enum_to_options(enum_class) -> list[dict[str, str]]:
    """Converts an Enum class to a list of {value, label} options for frontend dropdowns."""
    options = []
    for e in enum_class:
        # Use the value as the label, formatted nicely (e.g., 'driving_licence' -> 'Driving Licence')
        label = str(e.value).replace("_", " ").title()

        # Special case for blood groups to avoid formatting like 'A+' -> 'A+' (it's already fine)
        # but title() is safe on A+.

        options.append({"value": e.value, "label": label})
    return options


@router.get("/options", summary="Get all system dropdown options")
async def get_all_options() -> dict[str, list[dict[str, str]]]:
    """
    Fetch all available dropdown options for frontend forms in a single request.
    This ensures the frontend is always in sync with the backend database schemas.
    """
    return {
        "genders": enum_to_options(GenderEnum),
        "blood_groups": enum_to_options(BloodGroupEnum),
        "kyc_document_types": enum_to_options(KYCDocumentType),
        "medicine_types": enum_to_options(MedicineType),
        "relation_types": enum_to_options(RelationType),
        "delivery_types": enum_to_options(DeliveryType),
        "medicine_forms": enum_to_options(MedicineForm),
        "hospital_booking_statuses": enum_to_options(HospitalBookingStatus),
        "hospital_specialities": enum_to_options(Speciality),
        "lab_collection_types": enum_to_options(CollectionType),
        "lab_test_categories": enum_to_options(TestCategory),
        "ambulance_types": enum_to_options(AmbulanceType),
    }
