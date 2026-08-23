from fastcrud import FastCRUD
from .models import AmbulanceProvider, AmbulanceVehicle, AmbulanceRequest

crud_ambulance_providers: FastCRUD = FastCRUD(AmbulanceProvider)
crud_ambulance_vehicles: FastCRUD = FastCRUD(AmbulanceVehicle)
crud_ambulance_requests: FastCRUD = FastCRUD(AmbulanceRequest)
