from flask import jsonify, request, current_app
import os
from werkzeug.utils import secure_filename
import logging
import re
import uuid
from datetime import datetime

# Define the allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('miner_application.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    logger.debug(f"Checking if file {filename} is allowed")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder):
    """Upload file to Supabase storage bucket."""
    logger.debug(f"Attempting to save file: {file.filename if file else 'None'}")
    
    if file and allowed_file(file.filename):
        try:
            # Generate a unique filename
            filename = secure_filename(file.filename)
            file_ext = filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            
            logger.debug(f"Generated unique filename: {unique_filename}")
            
            # Get file content
            file_content = file.read()
            logger.debug(f"File size: {len(file_content)} bytes")
            logger.debug(f"Content type: {file.content_type}")
            
            # Upload to Supabase storage
            supabase = current_app.supabase
            
            # Debug: Check available buckets
            try:
                buckets = supabase.storage.list_buckets()
                logger.debug(f"Available buckets: {[b['name'] for b in buckets]}")
            except Exception as e:
                logger.error(f"Error listing buckets: {str(e)}", exc_info=True)
                return None
            
            # Upload file
            logger.debug("Attempting file upload to Supabase storage")
            try:
                response = supabase.storage.from_('documents').upload(
                    unique_filename,
                    file_content,
                    file_options={
                        "content-type": file.content_type,
                        "cache-control": "3600",
                        "upsert": False
                    }
                )
                
                if not response:
                    logger.error("Upload failed - no response received")
                    raise Exception("Upload failed - no response received")
                
                # Get the public URL for the uploaded file
                file_url = supabase.storage.from_('documents').get_public_url(unique_filename)
                logger.info(f"File uploaded successfully. Public URL: {file_url}")
                
                return file_url
            except Exception as upload_error:
                logger.error(f"Upload error: {str(upload_error)}", exc_info=True)
                return None
                
        except Exception as e:
            logger.error(f"Error in save_file: {str(e)}", exc_info=True)
            return None
    else:
        logger.warning(f"File not allowed or missing: {file.filename if file else 'None'}")
    return None

def clean_numeric_value(value):
    """Clean numeric values by removing special characters and units."""
    logger.debug(f"Cleaning numeric value: {value}")
    
    if value is None:
        logger.debug("Value is None, returning None")
        return None
        
    if isinstance(value, (int, float)):
        logger.debug(f"Value is already numeric: {value}")
        return float(value)
        
    if isinstance(value, str):
        logger.debug(f"Processing string value: {value}")
        # Remove common units and special characters
        original_value = value
        value = value.lower().strip()
        value = value.replace(',', '')
        value = value.replace('usd', '')
        value = value.replace('$', '')
        value = value.replace('tons/day', '')
        value = value.replace('m', '')
        value = value.replace('%', '')
        value = value.replace('years', '')
        value = value.replace('year', '')
        value = value.strip()
        
        logger.debug(f"After cleaning: {value}")
        
        # Extract the first number found
        number_match = re.search(r'[\d.]+', value)
        if number_match:
            try:
                result = float(number_match.group())
                logger.debug(f"Extracted number: {result}")
                return result
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not convert {number_match.group()} to float: {str(e)}")
                return None
        else:
            logger.debug(f"No numbers found in: {original_value}")
    return None

def init_routes(bp):
    @bp.route('/submit', methods=['POST'])
    def submit_license():
        logger.info("===== STARTING LICENSE SUBMISSION =====")
        try:
            # Get authenticated user ID
            logger.debug("Checking for user ID in cookies/headers")
            user_id = request.cookies.get('userId') or request.headers.get('X-User-ID')
            logger.debug(f"Extracted user_id: {user_id}")
            
            if not user_id:
                logger.error("No user ID provided in request")
                return jsonify({"error": "User ID not provided"}), 401

            # Create upload folder
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            logger.debug(f"Ensuring upload folder exists: {upload_folder}")
            os.makedirs(upload_folder, exist_ok=True)

            # Prepare form data with automatic miner_id assignment
            logger.debug("Preparing form data")
            if request.is_json:
                logger.debug("Processing JSON request")
                data = request.get_json()
                logger.debug(f"Raw JSON data: {data}")
                
                form_data = {
                    "miner_id": user_id,
                    "exploration_license_no": data.get('exploration_license_no'),
                    # ... (rest of your fields)
                }
                logger.debug(f"Form data from JSON: {form_data}")
            else:
                logger.debug("Processing form data request")
                form_data = {
                    "miner_id": user_id,
                    "exploration_license_no": request.form.get('exploration_license_no'),
                    # ... (rest of your fields)
                }
                logger.debug(f"Initial form data: {form_data}")

                # Handle file uploads
                logger.debug("Processing file uploads")
                file_fields = [
                    'articles_of_association', 'annual_reports', 'licensed_boundary_survey',
                    # ... (rest of your file fields)
                ]

                for field in file_fields:
                    file = request.files.get(field)
                    logger.debug(f"Processing field {field}: {file.filename if file else 'None'}")
                    if file:
                        file_path = save_file(file, upload_folder)
                        form_data[field] = file_path
                        logger.debug(f"Saved file for {field} to: {file_path}")
                    else:
                        form_data[field] = None
                        logger.debug(f"No file provided for {field}")

            # Validate required fields
            required_fields = [
                'exploration_license_no', 'applicant_name', 'national_id',
                # ... (rest of your required fields)
            ]
            logger.debug("Validating required fields")

            missing_fields = []
            for field in required_fields:
                if field not in form_data or form_data[field] is None:
                    missing_fields.append(field)
                    logger.warning(f"Missing or invalid field: {field}")

            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                return jsonify({"error": f"Missing or invalid fields: {', '.join(missing_fields)}"}), 400

            # Insert data into Supabase
            logger.debug("Attempting to insert data into Supabase")
            try:
                supabase = current_app.supabase
                logger.debug(f"Inserting data: {form_data}")
                response = supabase.table('application').insert(form_data).execute()
                logger.debug(f"Supabase response: {response}")
                
                if not response.data:
                    logger.error("No data returned from Supabase insert")
                    raise Exception("No data returned from Supabase insert")
                
                logger.info("Successfully inserted application data")

                # Update user's license status
                logger.debug("Updating user license status")
                update_data = {
                    'license_status': 'pending',
                    'active_date': datetime.now().isoformat()
                }
                logger.debug(f"Update data: {update_data}")
                
                update_response = supabase.table('users').update(update_data).eq('id', user_id).execute()
                logger.debug(f"User update response: {update_response}")
                
                logger.info("Successfully updated user status")

                return jsonify({
                    "message": "License submitted successfully!",
                    "data": response.data,
                    "user_id": user_id
                }), 201

            except Exception as supabase_error:
                logger.error(f"Supabase operation failed: {str(supabase_error)}", exc_info=True)
                return jsonify({"error": "Database operation failed"}), 500

        except Exception as e:
            logger.critical(f"Unexpected error in submit_license: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500
        finally:
            logger.info("===== LICENSE SUBMISSION PROCESS COMPLETED =====")

    @bp.route('/get', methods=['GET'])
    def get_licenses():
        logger.info("===== STARTING LICENSE RETRIEVAL =====")
        try:
            # Get authenticated user ID
            user_id = request.cookies.get('userId') or request.headers.get('X-User-ID')
            logger.debug(f"User ID from request: {user_id}")
            
            if not user_id:
                logger.error("No user ID provided")
                return jsonify({"error": "User ID not provided"}), 401

            supabase = current_app.supabase
            logger.debug("Querying applications for user")
            
            try:
                response = supabase.table('application') \
                                 .select('*') \
                                 .eq('miner_id', user_id) \
                                 .execute()
                                 
                logger.debug(f"Retrieved {len(response.data)} applications")
                logger.debug(f"Sample application data: {response.data[:1] if response.data else 'None'}")
                
                return jsonify(response.data), 200
                
            except Exception as query_error:
                logger.error(f"Supabase query failed: {str(query_error)}", exc_info=True)
                return jsonify({"error": "Failed to retrieve applications"}), 500

        except Exception as e:
            logger.critical(f"Unexpected error in get_licenses: {str(e)}", exc_info=True)
            return jsonify({"error": "Internal server error"}), 500
        finally:
            logger.info("===== LICENSE RETRIEVAL COMPLETED =====")
