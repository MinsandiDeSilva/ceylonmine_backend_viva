from flask import Blueprint, jsonify, request
from supabase import create_client, Client
from config import Config
from datetime import datetime, timedelta
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for miner-related routes
minerpage_bp = Blueprint('minerpage', __name__, url_prefix='/miner')

# Initialize Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def get_user_id():
    """Helper function to get user_id from cookies"""
    user_id = request.cookies.get('userId') or request.headers.get('X-User-ID')
    if not user_id:
        logger.error("User ID not found in cookies or headers")
        return None
    return user_id

def parse_period(period_str):
    """Robustly parse period strings into years"""
    try:
        period = str(period_str).lower()
        # Extract first number found
        num_match = re.search(r'\d+', period)
        if not num_match:
            return 1  # Default to 1 year
        
        num = int(num_match.group())
        
        if 'month' in period:
            return num / 12
        elif any(x in period for x in ['year', 'yr', 'y']):
            return num
        else:
            return num  # Assume years if no unit specified
    except Exception as e:
        logger.warning(f"Couldn't parse period '{period_str}': {str(e)}")
        return 1  # Default to 1 year on error

def parse_date(date_str):
    """Robust date parsing from multiple formats"""
    if not date_str:
        return None
        
    try:
        if isinstance(date_str, datetime):
            return date_str.date()
            
        if 'T' in date_str:  # ISO format
            return datetime.strptime(date_str.split('T')[0], '%Y-%m-%d').date()
        else:  # Simple date
            return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception as e:
        logger.error(f"Failed to parse date '{date_str}': {str(e)}")
        return None

@minerpage_bp.route('/license', methods=['GET'])
def get_license():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "User ID not provided"}), 401

        # Fetch user data
        user_data = supabase.table('users') \
                          .select("license_status, active_date") \
                          .eq('id', user_id) \
                          .execute().data
        
        if not user_data:
            return jsonify({"error": "User not found"}), 404
            
        user_data = user_data[0]
        license_status = user_data['license_status']
        active_date = parse_date(user_data.get('active_date'))
        
        if not active_date:
            return jsonify({"error": "Invalid or missing active date"}), 400

        # Fetch application data
        app_data = supabase.table('application') \
                         .select("exploration_license_no, period_of_validity") \
                         .eq('miner_id', user_id) \
                         .execute().data
                         
        if not app_data:
            return jsonify({"error": "No application found"}), 404
            
        app_data = app_data[0]
        license_no = app_data['exploration_license_no']
        period = app_data.get('period_of_validity', '1 year')
        
        # Calculate expiry
        years = parse_period(period)
        expiry_date = active_date + timedelta(days=round(365 * years))
        
        return jsonify({
            "license_status": license_status,
            "license_number": license_no,
            "active_date": active_date.strftime('%Y-%m-%d'),
            "period_of_validity": period,
            "expires": expiry_date.strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        logger.error(f"License endpoint error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@minerpage_bp.route('/royalty', methods=['GET'])
def get_royalty():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "User ID not provided"}), 401

        royalty_data = supabase.table('royalty') \
                            .select("total_amount") \
                            .eq('miner_id', user_id) \
                            .execute().data
                            
        if not royalty_data:
            return jsonify({"error": "No royalty data found"}), 404
            
        return jsonify({
            "royalty_amount_due": royalty_data[0]['total_amount'],
            "due_by": "2025-03-15"  # Should be fetched from DB
        })
        
    except Exception as e:
        logger.error(f"Royalty endpoint error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@minerpage_bp.route('/announcements', methods=['GET'])
def get_announcements():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"error": "User ID not provided"}), 401

        announcements = supabase.table('comments') \
                             .select("text, created_at") \
                             .eq('miner_id', user_id) \
                             .order('created_at', desc=True) \
                             .limit(5) \
                             .execute().data
        
        formatted_announcements = []
        for item in announcements:
            date_str = item.get('created_at', '')
            date_display = ""
            
            if date_str:
                date_obj = parse_date(date_str)
                if date_obj:
                    date_display = date_obj.strftime('%b %d, %Y')
            
            formatted_announcements.append({
                "text": item.get('text', 'No text'),
                "date": date_display
            })
            
        return jsonify({
            "announcements": formatted_announcements,
            "status_categories": ["Pending", "Submitted", "Completed", "Approved"]
        })
        
    except Exception as e:
        logger.error(f"Announcements endpoint error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

def init_routes(bp):
    bp.add_url_rule('/license', view_func=get_license)
    bp.add_url_rule('/royalty', view_func=get_royalty)
    bp.add_url_rule('/announcements', view_func=get_announcements)
