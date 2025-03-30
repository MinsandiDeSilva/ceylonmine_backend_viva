# # from flask import Blueprint, jsonify, request
# # from supabase import create_client, Client
# # from config import Config
# # from datetime import datetime, timedelta

# # # Create a Blueprint for miner-related routes
# # minerpage_bp = Blueprint('minerpage', _name_, url_prefix='/miner')

# # # Function to calculate expiration date based on period_of_validation
# # def calculate_expiration_date(start_date, period_of_validation):
# #     years = int(period_of_validation.split()[0])  # Extract the number of years
# #     expiration_date = start_date + timedelta(days=365 * years)  # Add years to the start date
# #     return expiration_date

# # # Endpoint to fetch license status, license number, and expiry date
# # @minerpage_bp.route('/license', methods=['GET'])
# # def get_license():
# #     try:
# #         # Get the userId of the currently logged-in user (passed in the request headers)
# #         user_id = request.headers.get('User-ID')
# #         if not user_id:
# #             return jsonify({"error": "User ID is required"}), 400

# #         # Fetch license status from the 'users' table
# #         user_response = supabase.table('users').select("license_status, active_date").eq('userId', user_id).execute()
# #         if not user_response.data:
# #             return jsonify({"error": "User not found"}), 404

# #         user_data = user_response.data[0]
# #         license_status = user_data['license_status']
# #         active_date_str = user_data.get('active_date')

# #         # Fetch exploration_license_no and period_of_validation from the 'application' table
# #         application_response = supabase.table('application').select("exploration_license_no, period_of_validation").eq('userId', user_id).execute()
# #         if not application_response.data:
# #             return jsonify({"error": "No application found for the user"}), 404

# #         application_data = application_response.data[0]
# #         exploration_license_no = application_data['exploration_license_no']
# #         period_of_validation = application_data.get('period_of_validation', '1 yr')  # Default to 1 year if not provided

# #         # Calculate expiry date
# #         if active_date_str:
# #             active_date = datetime.strptime(active_date_str, '%Y-%m-%d')
# #             expiry_date = calculate_expiration_date(active_date, period_of_validation)
# #         else:
# #             return jsonify({"error": "Active date is not available"}), 400

# #         return jsonify({
# #             "license_status": license_status,
# #             "license_number": exploration_license_no,
# #             "active_date": active_date_str,
# #             "period_of_validation": period_of_validation,
# #             "expires": expiry_date.strftime('%Y-%m-%d')  # Format expiry date
# #         })
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # # Endpoint to fetch royalty amount due
# # @minerpage_bp.route('/royalty', methods=['GET'])
# # def get_royalty():
# #     try:
# #         # Get the userId of the currently logged-in user
# #         user_id = request.headers.get('User-ID')
# #         if not user_id:
# #             return jsonify({"error": "User ID is required"}), 400

# #         # Fetch total_royalty from the 'royalty' table
# #         royalty_response = supabase.table('royalty').select("total_royalty").eq('userId', user_id).execute()
# #         if not royalty_response.data:
# #             return jsonify({"error": "No royalty data found for the user"}), 404

# #         royalty_data = royalty_response.data[0]
# #         royalty_amount_due = royalty_data['total_royalty']

# #         return jsonify({
# #             "royalty_amount_due": royalty_amount_due
# #         })
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # # Endpoint to fetch recent announcements
# # @minerpage_bp.route('/announcements', methods=['GET'])
# # def get_announcements():
# #     try:
# #         # Fetch data from the 'comments' table, ordered by creation date in descending order
# #         response = supabase.table('comments').select("*").order('created_at', desc=True).execute()
# #         announcements = response.data
# #         return jsonify(announcements)
# #     except Exception as e:
# #         return jsonify({"error": str(e)}), 500

# # # Function to initialize routes
# # def init_routes(bp):
# #     global supabase
# #     supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)  # Initialize Supabase client
# #     bp.add_url_rule('/license', view_func=get_license)
# #     bp.add_url_rule('/royalty', view_func=get_royalty)
# #     bp.add_url_rule('/announcements', view_func=get_announcements)



# # # from flask import Blueprint, jsonify, request, make_response
# # # from supabase import create_client
# # # from datetime import datetime, timedelta
# # # from secrets import token_urlsafe
# # # import bcrypt
# # # import os
# # # from dotenv import load_dotenv
# # # import logging

# # # # Load environment variables
# # # load_dotenv()

# # # # Configure logging
# # # logging.basicConfig(
# # #     level=logging.DEBUG,
# # #     format='%(asctime)s - %(levelname)s - %(message)s',
# # #     handlers=[
# # #         logging.FileHandler('app.log'),
# # #         logging.StreamHandler()
# # #     ]
# # # )

# # # # Initialize Supabase client
# # # supabase_url = os.getenv('SUPABASE_URL')
# # # supabase_key = os.getenv('SUPABASE_KEY')

# # # # Add debug logging
# # # logging.debug(f"SUPABASE_URL: {supabase_url}")
# # # logging.debug(f"SUPABASE_KEY length: {len(supabase_key or '')}")

# # # if not supabase_url or not supabase_key:
# # #     raise ValueError("Missing required environment variables SUPABASE_URL or SUPABASE_KEY")

# # # # Make sure the URL starts with https:// and ends with .supabase.co
# # # if not supabase_url.startswith('https://') or not supabase_url.endswith('.supabase.co'):
# # #     raise ValueError("Invalid Supabase URL format. It should start with 'https://' and end with '.supabase.co'")

# # # print(f"Using Supabase URL: '{supabase_url}'")

# # # # Add this before create_client
# # # print(f"URL characters: {[ord(c) for c in supabase_url]}")

# # # supabase = create_client(supabase_url, supabase_key)

# # # # Create a Blueprint for authentication
# # # auth_bp = Blueprint('auth', _name_, url_prefix='/api')

# # # # Store reset tokens with expiry (in memory - will be cleared when server restarts)
# # # reset_tokens = {}

# # # def hash_password(password):
# # #     # Convert the password to bytes
# # #     password_bytes = password.encode('utf-8')
# # #     # Generate salt and hash the password
# # #     salt = bcrypt.gensalt()
# # #     hashed = bcrypt.hashpw(password_bytes, salt)
# # #     # Return the hashed password as a string
# # #     return hashed.decode('utf-8')

# # # def verify_password(password, hashed_password):
# # #     # Convert passwords to bytes
# # #     password_bytes = password.encode('utf-8')
# # #     hashed_bytes = hashed_password.encode('utf-8')
# # #     # Verify the password
# # #     return bcrypt.checkpw(password_bytes, hashed_bytes)

# # # # Decorator to check if the user is authenticated
# # # def login_required(f):
# # #     @wraps(f)
# # #     def decorated(*args, **kwargs):
# # #         # Get the user_id from the cookie
# # #         user_id = request.cookies.get('user_id')
# # #         if not user_id:
# # #             logging.warning("Unauthorized access attempt (missing user_id cookie)")
# # #             return jsonify({'error': 'User not authenticated'}), 401
# # #         logging.debug(f"Authenticated request for user_id: {user_id}")
# # #         return f(user_id, *args, **kwargs)
# # #     return decorated

# # # @auth_bp.route("/home", methods=['GET'])
# # # def return_home():
# # #     logging.info("Home route accessed")  # Log an info message
# # #     return jsonify({
# # #         'message': "Hello World!"
# # #     })

# # # @auth_bp.route("/signup", methods=['POST'])
# # # def signup():
# # #     try:
# # #         data = request.get_json()
# # #         logging.debug(f"Signup request data: {data}")  # Log the request data
        
# # #         # Basic validation
# # #         required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
# # #         if not all(key in data for key in required_fields):
# # #             logging.warning("Missing required fields in signup request")  # Log a warning
# # #             return jsonify({'error': 'Missing required fields'}), 400
        
# # #         try:
# # #             # Check if email already exists
# # #             existing_email = supabase.table('users').select('*').eq('email', data['email']).execute()
# # #             if len(existing_email.data) > 0:
# # #                 logging.warning(f"Email already registered: {data['email']}")  # Log a warning
# # #                 return jsonify({'error': 'This email is already registered. Please use a different email or try logging in.'}), 400
            
# # #             # Check if username already exists
# # #             existing_username = supabase.table('users').select('*').eq('username', data['username']).execute()
# # #             if len(existing_username.data) > 0:
# # #                 logging.warning(f"Username already taken: {data['username']}")  # Log a warning
# # #                 return jsonify({'error': 'This username is already taken. Please choose a different username.'}), 400
            
# # #             # Hash the password before storing
# # #             hashed_password = hash_password(data['password'])
# # #             logging.debug("Password hashed successfully")  # Log a debug message
            
# # #             # Insert new user with hashed password and default role
# # #             new_user = supabase.table('users').insert({
# # #                 'first_name': data['firstName'],
# # #                 'last_name': data['lastName'],
# # #                 'username': data['username'],
# # #                 'email': data['email'],
# # #                 'password': hashed_password,
# # #                 'role': 'public'  
# # #             }).execute()
# # #             logging.info(f"New user registered: {data['email']}")  # Log an info message
            
# # #             return jsonify({
# # #                 'message': 'User registered successfully',
# # #                 'user': {
# # #                     'firstName': data['firstName'],
# # #                     'lastName': data['lastName'],
# # #                     'username': data['username'],
# # #                     'email': data['email'],
# # #                     'role': 'public'
# # #                 }
# # #             }), 201
            
# # #         except Exception as db_error:
# # #             logging.error(f"Database error during signup: {str(db_error)}", exc_info=True)  # Log the error with traceback
# # #             return jsonify({'error': 'An error occurred during registration. Please try again.', 'details': str(db_error)}), 500
            
# # #     except Exception as e:
# # #         logging.critical(f"Server error during signup: {str(e)}", exc_info=True)  # Log the critical error with traceback
# # #         return jsonify({'error': 'Server error. Please try again later.', 'details': str(e)}), 500

# # # @auth_bp.route("/login", methods=['POST'])
# # # def login():
# # #     try:
# # #         data = request.get_json()
# # #         logging.debug(f"Login request data: {data}")  # Log the request data
        
# # #         if not all(key in data for key in ['email', 'password']):
# # #             logging.warning("Missing email or password in login request")  # Log a warning
# # #             return jsonify({'error': 'Missing email or password'}), 400
        
# # #         try:
# # #             # Find user by email
# # #             result = supabase.table('users').select('*').eq('email', data['email']).execute()
            
# # #             if len(result.data) == 0:
# # #                 logging.warning(f"Invalid email: {data['email']}")  # Log a warning
# # #                 return jsonify({'error': 'Invalid email or password'}), 401
            
# # #             user = result.data[0]
            
# # #             # Verify password
# # #             if verify_password(data['password'], user['password']):
# # #                 logging.info(f"User logged in: {data['email']}")  # Log an info message
                
# # #                 # Create a response and set a cookie
# # #                 response = make_response(jsonify({
# # #                     'message': 'Login successful',
# # #                     'user': {
# # #                         'firstName': user['first_name'],
# # #                         'lastName': user['last_name'],
# # #                         'username': user['username'],
# # #                         'email': user['email'],
# # #                         'role': user['role']  # Include role in response
# # #                     }
# # #                 }))
# # #                 response.set_cookie('user_id', str(user['userId']), max_age=3600)  # Cookie expires in 1 hour
# # #                 return response
# # #             else:
# # #                 logging.warning(f"Invalid password for email: {data['email']}")  # Log a warning
# # #                 return jsonify({'error': 'Invalid email or password'}), 401
                
# # #         except Exception as db_error:
# # #             logging.error(f"Database error during login: {str(db_error)}", exc_info=True)  # Log the error with traceback
# # #             return jsonify({'error': 'Login failed. Please try again.', 'details': str(db_error)}), 500
            
# # #     except Exception as e:
# # #         logging.critical(f"Server error during login: {str(e)}", exc_info=True)  # Log the critical error with traceback
# # #         return jsonify({'error': 'Server error. Please try again later.', 'details': str(e)}), 500

# # # @auth_bp.route("/logout", methods=['POST'])
# # # def logout():
# # #     try:
# # #         # Create a response and clear the cookie
# # #         response = make_response(jsonify({'message': 'Logout successful'}))
# # #         response.set_cookie('user_id', '', max_age=0)  # Clear the cookie
# # #         return response
# # #     except Exception as e:
# # #         logging.error(f"Error in logout: {str(e)}", exc_info=True)
# # #         return jsonify({'error': str(e)}), 500

# # # @auth_bp.route("/request-reset", methods=['POST'])
# # # def request_reset():
# # #     try:
# # #         data = request.get_json()
# # #         email = data.get('email')
# # #         logging.debug(f"Password reset request for email: {email}")  # Log the request data
        
# # #         if not email:
# # #             logging.warning("Email is required for password reset")  # Log a warning
# # #             return jsonify({'error': 'Email is required'}), 400
        
# # #         try:
# # #             # Check if user exists
# # #             result = supabase.table('users').select('*').eq('email', email).execute()
            
# # #             if len(result.data) == 0:
# # #                 logging.warning(f"Email not found: {email}")  # Log a warning
# # #                 return jsonify({'message': 'If the email exists, a reset token will be sent'}), 200
            
# # #             # Generate reset token
# # #             reset_token = token_urlsafe(32)
# # #             logging.debug(f"Generated reset token: {reset_token} for email: {email}")  # Log a debug message
            
# # #             # Store token with expiry (1 hour)
# # #             reset_tokens[reset_token] = {
# # #                 'email': email,
# # #                 'expiry': datetime.now() + timedelta(hours=1)
# # #             }
            
# # #             # Return the token directly
# # #             return jsonify({
# # #                 'message': 'Password reset token generated',
# # #                 'token': reset_token
# # #             }), 200
            
# # #         except Exception as db_error:
# # #             logging.error(f"Database error during password reset request: {str(db_error)}", exc_info=True)  # Log the error with traceback
# # #             return jsonify({'error': 'Failed to process reset request', 'details': str(db_error)}), 500
            
# # #     except Exception as e:
# # #         logging.critical(f"Server error during password reset request: {str(e)}", exc_info=True)  # Log the critical error with traceback
# # #         return jsonify({'error': 'Server error', 'details': str(e)}), 500

# # # @auth_bp.route("/reset-password", methods=['POST'])
# # # def reset_password():
# # #     try:
# # #         data = request.get_json()
# # #         email = data.get('email')
# # #         new_password = data.get('newPassword')
# # #         logging.debug(f"Password reset request for email: {email}")  # Log the request data
        
# # #         if not email or not new_password:
# # #             logging.warning("Email and new password are required for password reset")  # Log a warning
# # #             return jsonify({'error': 'Email and new password are required'}), 400
        
# # #         try:
# # #             # Check if user exists
# # #             result = supabase.table('users').select('*').eq('email', email).execute()
            
# # #             if len(result.data) == 0:
# # #                 logging.warning(f"Email not found: {email}")  # Log a warning
# # #                 return jsonify({'error': 'Email not found'}), 404
            
# # #             # Hash the new password
# # #             hashed_password = hash_password(new_password)
# # #             logging.debug("New password hashed successfully")  # Log a debug message
            
# # #             # Update password in database
# # #             result = supabase.table('users').update({
# # #                 'password': hashed_password
# # #             }).eq('email', email).execute()
# # #             logging.info(f"Password updated for email: {email}")  # Log an info message
            
# # #             return jsonify({'message': 'Password updated successfully'}), 200
            
# # #         except Exception as db_error:
# # #             logging.error(f"Database error during password reset: {str(db_error)}", exc_info=True)  # Log the error with traceback
# # #             return jsonify({'error': 'Failed to update password', 'details': str(db_error)}), 500
            
# # #     except Exception as e:
# # #         logging.critical(f"Server error during password reset: {str(e)}", exc_info=True)  # Log the critical error with traceback
# # #         return jsonify({'error': 'Server error', 'details': str(e)}), 500

# # # def init_routes(bp):
# # #     bp.route("/home", methods=['GET'])(return_home)
# # #     bp.route("/signup", methods=['POST'])(signup)
# # #     bp.route("/login", methods=['POST'])(login)
# # #     bp.route("/logout", methods=['POST'])(logout)
# # #     bp.route("/request-reset", methods=['POST'])(request_reset)
# # #     bp.route("/reset-password", methods=['POST'])(reset_password)


# from flask import Blueprint, jsonify, request
# from supabase import create_client, Client
# from config import Config
# from datetime import datetime, timedelta

# # Create a Blueprint for miner-related routes
# minerpage_bp = Blueprint('minerpage', __name__, url_prefix='/miner')

# # Initialize Supabase client
# supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

# # Function to calculate expiration date based on period_of_validation
# def calculate_expiration_date(start_date, period_of_validation):
#     years = int(period_of_validation.split()[0])  # Extract the number of years
#     expiration_date = start_date + timedelta(days=365 * years)  # Add years to the start date
#     return expiration_date

# # Endpoint to fetch license status, license number, and expiry date
# @minerpage_bp.route('/license', methods=['GET'])
# def get_license():
#     try:
#         # Get the user_id from the Supabase session
#         session = supabase.auth.session()
#         if not session:
#             return jsonify({"error": "User not authenticated"}), 401

#         user_id = session.user.id

#         # Fetch license status from the 'users' table
#         user_response = supabase.table('users').select("license_status, active_date").eq('userId', user_id).execute()
#         if not user_response.data:
#             return jsonify({"error": "User not found"}), 404

#         user_data = user_response.data[0]
#         license_status = user_data['license_status']
#         active_date_str = user_data.get('active_date')

#         # Fetch exploration_license_no and period_of_validation from the 'application' table
#         application_response = supabase.table('application').select("exploration_license_no, period_of_validation").eq('userId', user_id).execute()
#         if not application_response.data:
#             return jsonify({"error": "No application found for the user"}), 404

#         application_data = application_response.data[0]
#         exploration_license_no = application_data['exploration_license_no']
#         period_of_validation = application_data.get('period_of_validation', '1 yr')  # Default to 1 year if not provided

#         # Calculate expiry date
#         if active_date_str:
#             active_date = datetime.strptime(active_date_str, '%Y-%m-%d')
#             expiry_date = calculate_expiration_date(active_date, period_of_validation)
#         else:
#             return jsonify({"error": "Active date is not available"}), 400

#         return jsonify({
#             "license_status": license_status,
#             "license_number": exploration_license_no,
#             "active_date": active_date_str,
#             "period_of_validation": period_of_validation,
#             "expires": expiry_date.strftime('%Y-%m-%d')  # Format expiry date
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Endpoint to fetch royalty amount due
# @minerpage_bp.route('/royalty', methods=['GET'])
# def get_royalty():
#     try:
#         # Get the user_id from the Supabase session
#         session = supabase.auth.session()
#         if not session:
#             return jsonify({"error": "User not authenticated"}), 401

#         user_id = session.user.id

#         # Fetch total_royalty from the 'royalty' table
#         royalty_response = supabase.table('royalty').select("total_royalty").eq('userId', user_id).execute()
#         if not royalty_response.data:
#             return jsonify({"error": "No royalty data found for the user"}), 404

#         royalty_data = royalty_response.data[0]
#         royalty_amount_due = royalty_data['total_royalty']

#         return jsonify({
#             "royalty_amount_due": royalty_amount_due
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Endpoint to fetch recent announcements
# @minerpage_bp.route('/announcements', methods=['GET'])
# def get_announcements():
#     try:
#         # Fetch data from the 'comments' table, ordered by creation date in descending order
#         response = supabase.table('comments').select("*").order('created_at', desc=True).execute()
#         announcements = response.data
#         return jsonify(announcements)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Function to initialize routes
# def init_routes(bp):
#     bp.add_url_rule('/license', view_func=get_license)
#     bp.add_url_rule('/royalty', view_func=get_royalty)
#     bp.add_url_rule('/announcements', view_func=get_announcements)


from flask import Blueprint, jsonify, request
from supabase import create_client, Client
from config import Config
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Create a Blueprint for miner-related routes
minerpage_bp = Blueprint('minerpage', __name__, url_prefix='/miner')

# Initialize Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def calculate_expiration_date(start_date, period_of_validation):
    try:
        years = int(period_of_validation.split()[0])
        expiration_date = start_date + timedelta(days=365 * years)
        return expiration_date
    except Exception as e:
        logging.error(f"Error calculating expiration date: {str(e)}")
        return None

@minerpage_bp.route('/license', methods=['GET'])
def get_license():
    try:
        # Get user ID from request header
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            logging.warning("Missing user ID in request")
            return jsonify({"error": "User ID is required"}), 401

        # Fetch license status from users table
        user_response = supabase.table('users').select("license_status, active_date").eq('userId', user_id).execute()
        if not user_response.data:
            logging.warning(f"No user found for ID: {user_id}")
            return jsonify({"error": "User not found"}), 404

        user_data = user_response.data[0]
        license_status = user_data.get('license_status', 'Inactive')
        active_date = user_data.get('active_date')

        # Fetch license details from application table
        application_response = supabase.table('application').select("exploration_license_no, period_of_validation").eq('userId', user_id).execute()
        if not application_response.data:
            logging.warning(f"No application found for user ID: {user_id}")
            return jsonify({"error": "No application found"}), 404

        application_data = application_response.data[0]
        license_number = application_data.get('exploration_license_no')
        period_of_validation = application_data.get('period_of_validation', '1 yr')

        # Calculate expiry date
        if active_date:
            active_date_obj = datetime.strptime(active_date, '%Y-%m-%d')
            expiry_date = calculate_expiration_date(active_date_obj, period_of_validation)
            expiry_date_str = expiry_date.strftime('%Y-%m-%d') if expiry_date else None
        else:
            expiry_date_str = None

        return jsonify({
            "license_status": license_status,
            "license_number": license_number,
            "active_date": active_date,
            "period_of_validation": period_of_validation,
            "expires": expiry_date_str
        })

    except Exception as e:
        logging.error(f"Error in get_license: {str(e)}")
        return jsonify({"error": str(e)}), 500

@minerpage_bp.route('/royalty', methods=['GET'])
def get_royalty():
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            logging.warning("Missing user ID in request")
            return jsonify({"error": "User ID is required"}), 401

        royalty_response = supabase.table('royalty').select("total_royalty").eq('userId', user_id).execute()
        if not royalty_response.data:
            logging.warning(f"No royalty data found for user ID: {user_id}")
            return jsonify({"royalty_amount_due": 0})

        royalty_data = royalty_response.data[0]
        return jsonify({
            "royalty_amount_due": float(royalty_data.get('total_royalty', 0))
        })

    except Exception as e:
        logging.error(f"Error in get_royalty: {str(e)}")
        return jsonify({"error": str(e)}), 500

@minerpage_bp.route('/announcements', methods=['GET'])
def get_announcements():
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            logging.warning("Missing user ID in request")
            return jsonify({"error": "User ID is required"}), 401

        response = supabase.table('comments').select("*").order('created_at', desc=True).execute()
        
        announcements = []
        for item in response.data:
            announcement = {
                "id": item.get('id'),
                "content": item.get('content', ''),
                "created_at": item.get('created_at')
            }
            announcements.append(announcement)

        logging.info(f"Retrieved {len(announcements)} announcements")
        return jsonify(announcements)

    except Exception as e:
        logging.error(f"Error in get_announcements: {str(e)}")
        return jsonify({"error": str(e)}), 500

def init_routes(bp):
    bp.add_url_rule('/license', view_func=get_license)
    bp.add_url_rule('/royalty', view_func=get_royalty)
    bp.add_url_rule('/announcements', view_func=get_announcements)
