from flask import jsonify, request
from supabase import create_client, Client
from config import Config
from flask import Blueprint
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the blueprint
unlicensedminer_bp = Blueprint('unlicensedminer', __name__, url_prefix='/unlicensedminer')

# Initialize Supabase client
supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_user_id():
    """Consistent user ID retrieval from cookies/headers (matches minerpage.py)"""
    user_id = request.cookies.get('userId') or request.headers.get('X-User-ID')
    if not user_id:
        logger.warning("User ID not found in cookies or headers")
    return user_id

@unlicensedminer_bp.route('/status', methods=['GET'])
def get_user_status():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        logger.info(f"Fetching status for miner_id: {user_id}")
        
        # Query application table using miner_id (FK to users.id)
        response = supabase.table('application') \
                         .select('status') \
                         .eq('miner_id', user_id) \
                         .execute()

        if not response.data:
            logger.warning(f"No application found for miner_id: {user_id}")
            return jsonify({
                "error": "Application not found",
                "solution": "Please submit an application first"
            }), 404

        return jsonify({
            "status": response.data[0]['status'],
            "miner_id": user_id
        }), 200

    except Exception as e:
        logger.error(f"Status endpoint error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@unlicensedminer_bp.route('/application', methods=['GET'])
def get_application_details():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        # Get all application details using miner_id
        response = supabase.table('application') \
                         .select('*') \
                         .eq('miner_id', user_id) \
                         .execute()

        if not response.data:
            return jsonify({"error": "Application not found"}), 404

        return jsonify({"application": response.data[0]}), 200

    except Exception as e:
        logger.error(f"Application details error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@unlicensedminer_bp.route('/documents', methods=['GET'])
def get_documents():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        # Get all documents using miner_id
        response = supabase.table('documents') \
                         .select('*') \
                         .eq('miner_id', user_id) \
                         .execute()

        return jsonify({"documents": response.data}), 200

    except Exception as e:
        logger.error(f"Documents endpoint error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@unlicensedminer_bp.route('/upload-document', methods=['POST'])
def upload_document():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        description = request.form.get('description', '')
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Generate unique filename
        file_extension = file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload file to Supabase storage
        file_bytes = file.read()
        supabase.storage.from_('documents').upload(unique_filename, file_bytes)
        
        # Get public URL
        file_url = supabase.storage.from_('documents').get_public_url(unique_filename)
        
        # Save document metadata using miner_id
        document_data = {
            'miner_id': user_id,  # Changed to miner_id to match application table
            'document_name': file.filename,
            'document_type': description,
            'document_url': file_url,
            'upload_date': datetime.now().isoformat(),
            'status': 'pending_review'
        }
        
        supabase.table('documents').insert(document_data).execute()
        
        return jsonify({
            "message": "Document uploaded successfully",
            "document_url": file_url
        }), 200
        
    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@unlicensedminer_bp.route('/announcements', methods=['GET'])
def get_announcements():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "Authentication required"}), 401

        # Updated query to match actual table structure
        response = supabase.table('comments') \
                         .select('text, created_at') \
                         .eq('miner_id', user_id) \
                         .order('created_at', desc=True) \
                         .execute()

        # Format the response to match your frontend expectations
        announcements = []
        for item in response.data:
            date_str = item.get('created_at', '')
            date_display = datetime.fromisoformat(date_str).strftime('%b %d, %Y') if date_str else ''
            
            announcements.append({
                "text": item.get('text', ''),
                "date": date_display
            })

        return jsonify({"announcements": announcements}), 200

    except Exception as e:
        logger.error(f"Announcements error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def init_routes(bp):
    bp.add_url_rule('/status', view_func=get_user_status)
    bp.add_url_rule('/application', view_func=get_application_details)
    bp.add_url_rule('/documents', view_func=get_documents)
    bp.add_url_rule('/upload-document', view_func=upload_document)
    bp.add_url_rule('/announcements', view_func=get_announcements)
