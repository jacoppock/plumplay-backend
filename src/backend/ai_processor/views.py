import json
import logging
from typing import Any, Dict, List, Optional

import requests
from auth import TokenManager
from base import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from llama_index.core import PromptTemplate

from .llm import llm

logger = logger = logging.getLogger(__name__)
token_manager = TokenManager(
    settings.MEDPLUM_CLIENT_ID, settings.MEDPLUM_CLIENT_SECRET, "https://api.medplum.dev.automated.co/oauth2/token"
)


@csrf_exempt
def process_voice_memo(request: HttpRequest) -> JsonResponse:
    if request.method == "POST":
        # Get the raw text from the request
        raw_text: str = request.POST.get("text", "")

        if not raw_text:
            return JsonResponse({"error": "No text provided."}, status=400)

        # Process the text to extract clinical information
        extracted_data = extract_clinical_data(raw_text)

        # Convert extracted data to FHIR resources
        # fhir_resources = create_fhir_resources(extracted_data)
        out = create_task_and_note_with_llm(
            extracted_data=extracted_data,
            patient_id="919d82f5-bd4d-45fb-a637-7c6c485640ee",
            practitioner_id="c8b8127f-5592-4963-9298-901068902fee",
        )
        # Optionally, save resources to Medplum via your existing proxy
        # save_resources_to_medplum(fhir_resources)

        return JsonResponse({"fhir_resources": out}, status=200)
    else:
        return JsonResponse({"error": "POST a voice memo instead."}, status=405)


def extract_clinical_data(raw_text: str) -> Dict[str, Any]:
    # Initialize the LLM Predictor
    llm_predictor = llm

    # Define the prompt
    template = (
        "Extract the patient's name, age, gender, medical conditions, medications, "
        "and any lab results from the following text:\n\n"
        f"{raw_text}\n\n"
        "Provide the output strictly in JSON format without any additional text. "
        "The JSON should have the following keys: "
        "name (string), age (integer), gender (string), "
        "conditions (list of strings), medications (list of strings), labs (list of strings)."
    )

    # Log the prompt for debugging purposes
    logger.debug(f"Prompt sent to LLM: {template}")

    # Create a PromptTemplate instance
    prompt_template = PromptTemplate(template=template, template_var_mappings={"raw_text": raw_text})

    try:
        # Get the prediction
        response = llm_predictor.predict(prompt_template)
        logger.debug(f"Raw LLM response: {response}")

        # Remove any backticks or extra formatting
        cleaned_response = response.strip("```").replace("json", "").strip()
        logger.debug(f"Cleaned LLM response: {cleaned_response}")

        if not cleaned_response.strip():  # Check if the response is empty or only whitespace
            raise ValueError("Received empty response from LLM")

        # Parse the JSON output
        extracted_data = json.loads(cleaned_response)

    except json.JSONDecodeError as e:
        logger.exception("Failed to parse JSON from LLM response.")
        raise ValueError(f"Invalid JSON response from LLM: {cleaned_response}") from e

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise ValueError("An error occurred while processing the LLM response.") from e

    return extracted_data


def create_fhir_resources(extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    fhir_resources: List[Dict[str, Any]] = []

    # Create Patient resource
    patient_name = extracted_data.get("name", "")
    patient_gender = extracted_data.get("gender", "").lower()
    patient_age = extracted_data.get("age")

    if not patient_name or not patient_age or not patient_gender:
        print("Missing required patient data (name, gender, or age).")
        return []  # Early return if critical data is missing

    patient_resource: Dict[str, Any] = {
        "resourceType": "Patient",
        "name": [{"text": patient_name}],
        "gender": patient_gender,
        "birthDate": calculate_birth_date(patient_age),
    }

    # Save Patient resource first to obtain patient_id
    patient_id: Optional[str] = save_resource_to_medplum(patient_resource)

    if not patient_id:
        print("Failed to save Patient resource.")
        return []  # Handle error appropriately, returning empty resources list

    # Update the subject reference with the actual patient ID
    subject_reference: str = f"Patient/{patient_id}"

    # Create Condition resources
    conditions: List[str] = extracted_data.get("conditions", [])
    for condition in conditions:
        if condition:  # Ensure that the condition is not empty
            condition_resource: Dict[str, Any] = {
                "resourceType": "Condition",
                "code": {"text": condition},
                "subject": {"reference": subject_reference},
            }
            fhir_resources.append(condition_resource)

    # Create MedicationRequest resources
    medications: List[str] = extracted_data.get("medications", [])
    for medication in medications:
        if medication:  # Ensure that the medication is not empty
            medication_resource: Dict[str, Any] = {
                "resourceType": "MedicationRequest",
                "medicationCodeableConcept": {"text": medication},
                "subject": {"reference": subject_reference},
                "status": "active",
                "intent": "order",
            }
            fhir_resources.append(medication_resource)

    # Save all resources to Medplum
    for resource in fhir_resources:
        save_resource_to_medplum(resource)

    return fhir_resources


def calculate_birth_date(age: Optional[str]) -> Optional[str]:
    from datetime import date

    try:
        birth_year: int = date.today().year - int(age)  # type: ignore
        return f"{birth_year}-01-01"  # Use January 1st as an approximation
    except (ValueError, TypeError):
        print(f"Invalid age provided: {age}")
        return None


def save_resource_to_medplum(resource: Dict[str, Any]) -> Optional[str]:
    resource_type = resource.get("resourceType", "")

    # Ensure MEDPLUM_BASE_URL doesn't have a trailing slash
    base_url = settings.MEDPLUM_BASE_URL

    # Properly construct the full URL
    url = f"{base_url}/{resource_type}"

    # Obtain access token using your TokenManager
    access_token = token_manager.get_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/fhir+json",
        "Accept": "application/fhir+json",
    }

    response = requests.post(url, headers=headers, json=resource)

    if response.status_code == 201:
        print(f"{resource_type} resource created successfully.")
        created_resource: Dict[str, Any] = response.json()
        return created_resource.get("id")
    else:
        print(f"Failed to create {resource_type}. Status code: {response.status_code}")
        print("Error:", response.text)
        created_resource: Dict[str, Any] = response.json()
        return created_resource.get("id")


def create_task_and_note_with_llm(
    extracted_data: Dict[str, Any], patient_id: str, practitioner_id: str
) -> List[Dict[str, Any]]:
    fhir_resources: List[Dict[str, Any]] = []
    llm_predictor = llm

    # Ensure extracted_data contains required fields
    name = extracted_data.get("name", "N/A")
    age = extracted_data.get("age", "N/A")
    gender = extracted_data.get("gender", "N/A")
    conditions = ", ".join(extracted_data.get("conditions", [])) or "None"
    medications = ", ".join(extracted_data.get("medications", [])) or "None"
    labs = ", ".join(extracted_data.get("labs", [])) or "None"

    # Use LLM to generate the clinical note content
    note_prompt_template = PromptTemplate(
        template=(
            "Generate a clinical note for a patient based on the following information:\n"
            f"Name: {name}\n"
            f"Age: {age}\n"
            f"Gender: {gender}\n"
            f"Conditions: {conditions}\n"
            f"Medications: {medications}\n"
            f"Labs: {labs}\n"
        ),
        template_var_mappings={
            "name": name,
            "age": age,
            "gender": gender,
            "conditions": conditions,
            "medications": medications,
            "labs": labs,
        },
    )

    # Call LLM to generate the formatted clinical note
    note_content = llm_predictor.predict(prompt=note_prompt_template)

    # Create the Note (as a Communication resource)
    note_resource: Dict[str, Any] = {
        "resourceType": "Communication",
        "status": "completed",
        "subject": {"reference": f"Patient/{patient_id}"},
        "sent": "2024-09-20T12:00:00Z",  # You may want to dynamically set this date
        "note": [{"text": note_content}],
    }

    # Save the Note resource
    note_id = save_resource_to_medplum(note_resource)

    if not note_id:
        print("Failed to save Note (Communication) resource.")
        return []  # Handle error appropriately

    # Use LLM to generate a task description for the clinician
    task_prompt_template = PromptTemplate(
        template=(
            "Generate a task description for a clinician to review and confirm a patient's note. "
            "The note contains the patient's name, age, gender, conditions, medications, and lab results."
            f"\n\nNote Content: {note_content}"
        ),
        template_var_mappings={"note_content": note_content},
    )

    task_description = llm_predictor.predict(prompt=task_prompt_template)

    # Create Task resource for clinician review
    task_resource: Dict[str, Any] = {
        "resourceType": "Task",
        "status": "requested",  # Task has been requested, awaiting action
        "intent": "order",  # Clinician is ordered to review
        "priority": "routine",
        "description": task_description,  # LLM-generated task description
        "for": {"reference": f"Patient/{patient_id}"},
        "focus": {"reference": f"Communication/{note_id}"},  # Link the task to the note
        "owner": {"reference": f"Practitioner/{practitioner_id}"},  # Replace with actual clinician ID
        "authoredOn": "2024-09-20T12:00:00Z",  # Set the time when task is created
        "requester": {"reference": f"Practitioner/{practitioner_id}"},  # The clinician requesting the review
    }

    # Save the Task resource
    task_id = save_resource_to_medplum(task_resource)

    if not task_id:
        print("Failed to save Task resource.")
        return []  # Handle error appropriately

    # Append the created Note and Task resources to the list
    fhir_resources.append(note_resource)
    fhir_resources.append(task_resource)

    return fhir_resources


def some_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"message": "Welcome to the AI Processor!"})
