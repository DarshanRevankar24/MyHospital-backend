import os

fixes = [
    {
        'module': 'ambulance',
        'schemas_append': '\n\nclass AmbulanceRequestCreateInternal(AmbulanceRequestCreate):\n    user_id: int\n    request_ref: str\n    status: str\n',
        'service_replace': ('object=req_data', 'object=AmbulanceRequestCreateInternal(**req_data)'),
        'schema_import': ('AmbulanceRequestCreate,', 'AmbulanceRequestCreate, AmbulanceRequestCreateInternal,')
    },
    {
        'module': 'blood_bank',
        'schemas_append': '\n\nclass BloodRequestCreateInternal(BloodRequestCreate):\n    user_id: int\n    request_ref: str\n    status: str\n',
        'service_replace': ('object=req_data', 'object=BloodRequestCreateInternal(**req_data)'),
        'schema_import': ('BloodRequestCreate,', 'BloodRequestCreate, BloodRequestCreateInternal,')
    },
    {
        'module': 'family',
        'schemas_append': '\n\nclass FamilyConnectionCreateInternal(FamilyConnectionCreate):\n    requester_id: int\n    recipient_id: int\n    status: str\n    permissions: dict\n    document_access_enabled: bool\n',
        'service_replace': ('object=new_conn_data', 'object=FamilyConnectionCreateInternal(**new_conn_data)'),
        'schema_import': ('FamilyConnectionCreate,', 'FamilyConnectionCreate, FamilyConnectionCreateInternal,')
    },
    {
        'module': 'hospital',
        'schemas_append': '\n\nclass HospitalBookingCreateInternal(HospitalBookingCreate):\n    user_id: int\n    provider_id: int\n    doctor_id: int\n    slot_id: int\n    booking_ref: str\n    status: str\n    amount: float\n',
        'service_replace': ('object=booking_data', 'object=HospitalBookingCreateInternal(**booking_data)'),
        'schema_import': ('HospitalBookingCreate,', 'HospitalBookingCreate, HospitalBookingCreateInternal,')
    },
    {
        'module': 'laboratory',
        'schemas_append': '\n\nclass LabBookingCreateInternal(LabBookingCreate):\n    user_id: int\n    booking_ref: str\n    status: str\n    amount: float\n',
        'service_replace': ('object=booking_data', 'object=LabBookingCreateInternal(**booking_data)'),
        'schema_import': ('LabBookingCreate,', 'LabBookingCreate, LabBookingCreateInternal,')
    },
    {
        'module': 'pharmacy',
        'schemas_append': '\n\nclass PharmacyOrderCreateInternal(PharmacyOrderCreate):\n    user_id: int\n    order_ref: str\n    status: str\n    total_amount: float\n',
        'service_replace': ('object=order_data', 'object=PharmacyOrderCreateInternal(**order_data)'),
        'schema_import': ('PharmacyOrderCreate,', 'PharmacyOrderCreate, PharmacyOrderCreateInternal,')
    },
]

base_dir = 'd:/projects/MH/MH_user_backend/backend/src/modules/'

for fix in fixes:
    # 1. Update schemas.py
    schemas_path = os.path.join(base_dir, fix['module'], 'schemas.py')
    with open(schemas_path, 'a') as f:
        f.write(fix['schemas_append'])
        
    # 2. Update service.py
    service_path = os.path.join(base_dir, fix['module'], 'service.py')
    with open(service_path, 'r') as f:
        content = f.read()
    
    # modify import
    content = content.replace(fix['schema_import'][0], fix['schema_import'][1])
    # modify object pass
    content = content.replace(fix['service_replace'][0], fix['service_replace'][1])
    
    with open(service_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {fix['module']}")
