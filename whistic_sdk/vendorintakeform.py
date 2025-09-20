import requests
import logging
from typing import Dict, Any, List, Optional


class VendorFormValidationError(Exception):
    """Custom exception for vendor form validation errors."""
    pass


class VendorIntakeForm:
    """
    Handles vendor intake form operations for the Whistic API.

    This class provides methods to retrieve the vendor intake form
    from the Whistic platform and generate form submissions.
    """

    def __init__(self, whistic_instance):
        """
        Initialize VendorIntakeForm with a Whistic instance.

        Args:
            whistic_instance: The main Whistic client instance
        """
        self.whistic = whistic_instance
        self.question_map = None
        self.required_questions = None
        self.all_questions = None

    def get(self):
        """
        Get the vendor intake form from /company/vendor-intake-form.

        Returns:
            dict: The vendor intake form data if successful, None otherwise
        """
        logging.debug("Querying vendor intake form")
        # this is what the documentation says
        #url = f"{self.whistic.endpoint}/company/vendor-intake-form"
        
        url = f"{self.whistic.endpoint}/questionnaireVersions/vendorIntake?expand=sections.controls.questions"
        response = self.whistic._make_request_with_retry(url)

        if response and response.status_code == 200:
            logging.info(f"{response.status_code} - {url}")
            return response.json()
        else:
            if response:
                logging.error(f"{response.status_code} - {url} - {response.content}")
            return None

    def describe(self):
        """
        Extract the hierarchical structure from the vendor intake form.

        Uses the get() method to retrieve the raw form data and creates
        a dictionary structure with sections as top-level keys and
        question texts as the field names within each section.

        Returns:
            dict: A nested dictionary with section headings as keys and
                  lists of question texts as values, or empty dict if form cannot be retrieved
        """
        logging.debug("Extracting hierarchical structure from vendor intake form")
        form_data = self.get()

        if not form_data:
            logging.warning("Could not retrieve form data to extract structure")
            return {}

        structure = {}

        # Extract structure from sections -> controls -> questions
        sections = form_data.get('sections', [])
        for section in sections:
            section_heading = section.get('heading', 'Unknown Section')

            if section_heading not in structure:
                structure[section_heading] = []

            # Each section has controls
            controls = section.get('controls', [])
            for control in controls:
                # Each control has questions
                questions = control.get('questions', [])
                for question in questions:
                    # Extract the text field from each question
                    question_text = question.get('text')
                    if question_text and question_text not in structure[section_heading]:
                        structure[section_heading].append(question_text)

        total_questions = sum(len(questions) for questions in structure.values())
        logging.info(f"Extracted structure with {len(structure)} sections and {total_questions} total questions")
        return structure

    def _build_question_map(self, intake_form: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Build a hierarchical mapping from section -> question text -> question details."""
        question_map = {}

        for section in intake_form.get('sections', []):
            section_heading = section.get('heading', 'Unknown Section')
            if section_heading not in question_map:
                question_map[section_heading] = {}

            for control in section.get('controls', []):
                for question in control.get('questions', []):
                    question_text = question.get('text', '').strip()
                    if question_text:
                        question_map[section_heading][question_text] = {
                            'question': question,
                            'control': control,
                            'section': section
                        }

        return question_map

    def _get_required_questions(self) -> Dict[str, List[str]]:
        """Get a hierarchical dictionary of required questions by section."""
        required = {}
        for section_heading, questions in self.question_map.items():
            required[section_heading] = []
            for question_text, info in questions.items():
                if info['question'].get('required', False):
                    required[section_heading].append(question_text)
        return required

    def validate_input_data(self, input_data: Dict[str, Dict[str, str]]) -> None:
        """Validate input data for required fields and field existence."""

        # Initialize question mapping if not done
        if self.question_map is None:
            intake_form = self.get()
            if not intake_form:
                raise VendorFormValidationError("Could not retrieve intake form for validation")
            self.question_map = self._build_question_map(intake_form)
            self.required_questions = self._get_required_questions()

        # Check for invalid sections
        invalid_sections = []
        for section_name in input_data.keys():
            if section_name not in self.question_map:
                invalid_sections.append(section_name)

        if invalid_sections:
            error_msg = f"Invalid sections found: {invalid_sections}\n\n"
            error_msg += "Valid sections are:\n"
            for i, valid_section in enumerate(sorted(self.question_map.keys()), 1):
                error_msg += f"{i:2d}. {valid_section}\n"
            raise VendorFormValidationError(error_msg)

        # Check for invalid fields within sections
        invalid_fields = []
        for section_name, section_data in input_data.items():
            if section_name in self.question_map:
                for field_name in section_data.keys():
                    if field_name not in self.question_map[section_name]:
                        invalid_fields.append(f"{section_name}.{field_name}")

        if invalid_fields:
            error_msg = f"Invalid fields found: {invalid_fields}\n\n"
            error_msg += "Valid fields by section:\n"
            for section_name, questions in self.question_map.items():
                error_msg += f"\n{section_name}:\n"
                for i, question_text in enumerate(sorted(questions.keys()), 1):
                    required_marker = " (REQUIRED)" if question_text in self.required_questions.get(section_name, []) else ""
                    error_msg += f"  {i:2d}. {question_text}{required_marker}\n"
            raise VendorFormValidationError(error_msg)

        # Check for missing required fields
        missing_required = []
        for section_name, required_fields in self.required_questions.items():
            section_data = input_data.get(section_name, {})
            for required_field in required_fields:
                if required_field not in section_data or not section_data[required_field] or str(section_data[required_field]).strip() == "":
                    missing_required.append(f"{section_name}.{required_field}")

        if missing_required:
            error_msg = f"Missing required fields: {missing_required}\n\n"
            error_msg += "All required fields by section:\n"
            for section_name, required_fields in self.required_questions.items():
                if required_fields:
                    error_msg += f"\n{section_name}:\n"
                    section_data = input_data.get(section_name, {})
                    for i, req_field in enumerate(required_fields, 1):
                        status = "[PROVIDED]" if req_field in section_data and section_data[req_field] and str(section_data[req_field]).strip() != "" else "[MISSING]"
                        error_msg += f"  {i:2d}. {req_field} - {status}\n"
            raise VendorFormValidationError(error_msg)

    def generate_vendor_submission(self, input_data: Dict[str, Dict[str, str]], validate: bool = True) -> Dict[str, Any]:
        """Generate a complete vendor submission from hierarchical input data."""

        # Get intake form if not already loaded
        intake_form = self.get()
        if not intake_form:
            raise VendorFormValidationError("Could not retrieve intake form")

        # Initialize question mapping if not done
        if self.question_map is None:
            self.question_map = self._build_question_map(intake_form)
            self.required_questions = self._get_required_questions()

        # Validate input data if requested
        if validate:
            self.validate_input_data(input_data)

        # Start with the basic structure
        submission = {
            "questionnaireVersionIdentifier": intake_form['identifier'],
            "questionResponses": []
        }

        # Process each section and its fields
        for section_name, section_data in input_data.items():
            if section_name in self.question_map:
                for question_text, answer_value in section_data.items():
                    if question_text in self.question_map[section_name]:
                        question_info = self.question_map[section_name][question_text]
                        question_response = self._create_question_response(
                            question_info, answer_value
                        )
                        if question_response:
                            submission["questionResponses"].append(question_response)
                    else:
                        logging.warning(f"Question '{question_text}' not found in section '{section_name}'")
            else:
                logging.warning(f"Section '{section_name}' not found in intake form")

        return submission

    def _create_question_response(self, question_info: Dict[str, Any],
                                answer_value: str) -> Optional[Dict[str, Any]]:
        """Create a question response structure."""
        question = question_info['question']
        control = question_info['control']
        section = question_info['section']

        # Skip if no answer provided
        if not answer_value or answer_value.strip() == "":
            return None

        # Build the response structure
        response = {
            "question": {
                "language": question.get("language", "ENGLISH"),
                "type": question.get("type", "TEXT"),
                "text": question.get("text"),
                "identifier": question.get("identifier"),
                "identification": question.get("identification"),
                "options": question.get("options", []),
                "required": question.get("required", False),
                "showNotApplicable": question.get("showNotApplicable", False),
                "answeredTag": question.get("answeredTag"),
                "notApplicableTag": question.get("notApplicableTag"),
                "questionLevelCommentTag": question.get("questionLevelCommentTag"),
                "fileUploadTag": question.get("fileUploadTag"),
                "answeredCondition": question.get("answeredCondition"),
                "warningCondition": question.get("warningCondition"),
                "commentRequiredCondition": question.get("commentRequiredCondition"),
                "fileUploadRequiredCondition": question.get("fileUploadRequiredCondition"),
                "control": {
                    "identifier": control.get("identifier"),
                    "heading": control.get("heading"),
                    "identification": control.get("identification"),
                    "section": {
                        "identifier": section.get("identifier"),
                        "heading": section.get("heading")
                    }
                },
                "metadata": question.get("metadata"),
                "questionIdentifier": question.get("questionIdentifier")
            },
            "customFormControlIdentifier": question.get("identifier"),
            "choices": [question.get("answeredTag")] if question.get("answeredTag") else [],
            "answerText": answer_value
        }

        return response

    def get_available_questions(self) -> Dict[str, List[str]]:
        """Get a hierarchical dictionary of all available questions by section."""
        if self.question_map is None:
            intake_form = self.get()
            if intake_form:
                self.question_map = self._build_question_map(intake_form)
                self.required_questions = self._get_required_questions()

        if self.question_map:
            return {section: list(questions.keys()) for section, questions in self.question_map.items()}
        return {}

    def get_required_questions(self) -> Dict[str, List[str]]:
        """Get a hierarchical dictionary of all required questions by section."""
        if self.required_questions is None:
            intake_form = self.get()
            if intake_form:
                self.question_map = self._build_question_map(intake_form)
                self.required_questions = self._get_required_questions()
        return self.required_questions.copy() if self.required_questions else {}

    def get_optional_questions(self) -> Dict[str, List[str]]:
        """Get a hierarchical dictionary of all optional questions by section."""
        if self.question_map is None or self.required_questions is None:
            intake_form = self.get()
            if intake_form:
                self.question_map = self._build_question_map(intake_form)
                self.required_questions = self._get_required_questions()

        optional = {}
        if self.question_map and self.required_questions:
            for section, questions in self.question_map.items():
                required_in_section = set(self.required_questions.get(section, []))
                optional[section] = [q for q in questions.keys() if q not in required_in_section]
        return optional
    
    def new(self, form, **KW):
        """
        Submits a new vendor intake form

        Args:
            form: Dictionary containing form field values
            **KW: Additional keyword arguments:
                - force (bool): If True, skip domain existence check
                - validate (bool): If True, validate form data (default: True)

        Returns:
            boolean: state of submission
        """

        force = KW.get('force', False)
        validate = KW.get('validate', True)

        # Extract domain from form (check Vendor Information section)
        vendor_info = form.get('Vendor Information', {})
        domain = vendor_info.get('Vendor URL')
        if not domain:
            logging.error("No domain found in form data. Required field: 'Vendor Information.Vendor URL'")
            return False

        # == Does the domain already exist?  If it does, return False (UNLESS force is true)
        vendor_domain_data = self.whistic.vendors.domain(domain)
        if not force and vendor_domain_data:
            logging.warning(f"Domain {domain} already exists. Intake will be skipped.")
            return False

        # == grab the vendor intake form
        intake_form = self.get()
        if not intake_form:
            logging.error("Could not retrieve vendor intake form")
            return False

        # == Generate the payload to be passed to the vendor method
        try:
            # Generate the vendor submission payload
            submission_payload = self.generate_vendor_submission(form, validate=validate)

            logging.info(f"Generated submission payload with {len(submission_payload.get('questionResponses', []))} responses")

            # Create the vendor using the submission payload
            result = self.whistic.vendors.new(submission_payload)

            if result:
                logging.info(f"Successfully submitted vendor intake form for domain: {domain}")
                return True
            else:
                logging.error(f"Failed to submit vendor intake form for domain: {domain}")
                return False

        except VendorFormValidationError as e:
            logging.error(f"Form validation failed: {e}")
            return False
        except Exception as e:
            logging.error(f"Error generating vendor submission: {e}")
            return False

