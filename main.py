from fastapi import FastAPI,HTTPException,Path,Query
from pydantic import BaseModel,Field, computed_field
from fastapi.responses import JSONResponse
from typing import Annotated, Literal,Optional
import json

app = FastAPI()

class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

def load_data(file_path: str):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data
    
def save_data(patients):
    with open('patients.json', 'w') as file:
        json.dump(patients, file, indent=4)

@app.get("/")
def hello():   
    return {"message": "Patient Management System API"}

@app.get("/about")
def about():
    return {"message": "A fully functional API to manage your patient records"}

@app.get("/view")
def view():
    data = load_data('patients.json')
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str=Path(..., description="The ID of the patient to view",example="P001")):
    patients = load_data('patients.json')
    if patient_id in patients:
        return patients[patient_id]
    
    raise HTTPException(status_code=404, detail="Patient not found") 

@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="Sort patients by height, weight or bmi", example="weight"),
    order: str = Query("asc", description="Order of sorting: asc or desc", example="asc")
    ):
    valid_sort_keys = ["height", "weight", "bmi"]
    if sort_by not in valid_sort_keys:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by parameter. Valid options are: {', '.join(valid_sort_keys)}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail=f"Invalid order parameter. Valid options are: asc, desc")
    
    patients = load_data('patients.json')
    sorted_patients = sorted(patients.values(), key=lambda x: x[sort_by], reverse=(order == "desc"))

    return sorted_patients

@app.post("/create")
def create_patient(patient: Patient):
    patients = load_data('patients.json')
    
    if patient.id in patients:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    
    patients[patient.id] = patient.model_dump(exclude=['id'])

    save_data(patients)
    
    return JSONResponse(status_code=201, content={"message": "Patient created successfully", "patient": patient.model_dump()})

@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    patients = load_data('patients.json')
    
    if patient_id not in patients:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    existing_patient = patients[patient_id]
    
    updated_data = patient_update.model_dump(exclude_unset=True)
    
    for key, value in updated_data.items():
        if value is not None:
            existing_patient[key] = value
    
    existing_patient['id']= patient_id  
    existing_patient_obj = Patient(**existing_patient)
    
    patients[patient_id] = existing_patient_obj.model_dump(exclude=['id'])
    
    save_data(patients)
    
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully", "patient": existing_patient})

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    patients = load_data('patients.json')
    
    if patient_id not in patients:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del patients[patient_id]
    
    save_data(patients)
    
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})