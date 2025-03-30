from flask import jsonify, request, current_app
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init_routes(bp):
    @bp.route('/submit', methods=['POST'])
    def submit_contact():
        try:
            data = request.json
            supabase = current_app.supabase

            # Log the received data for debugging
            logger.debug(f"Received data: {data}")

            # Validate required fields
            if not all([data.get('name'), data.get('email'), data.get('message')]):
                return jsonify({
                    "error": "Missing required fields",
                    "details": "Name, email, and message are required"
                }), 400

            # Prepare the data for insertion (only fields shown in the FE image)
            contact_data = {
                'name': data['name'],
                'email': data['email'],
                'message': data['message']
            }

            # Insert data into Supabase
            response = supabase.table('contact_data').insert(contact_data).execute()

            # Log the response from Supabase
            logger.debug(f"Supabase response: {response}")

            if response.data:
                return jsonify({
                    "message": "Contact message submitted successfully!",
                    "data": response.data
                }), 201
            else:
                logger.error(f"Supabase error: No data returned")
                return jsonify({
                    "error": "Failed to submit contact message",
                    "details": "No data returned from Supabase"
                }), 500

        except Exception as e:
            logger.error(f"Error submitting contact message: {e}")
            return jsonify({"error": str(e)}), 500

    @bp.route('/get', methods=['GET'])
    def get_contacts():
        try:
            supabase = current_app.supabase
            response = supabase.table('contact_data').select('*').execute()

            logger.debug(f"Fetched contacts: {response.data}")

            if response.data:
                return jsonify(response.data), 200
            else:
                logger.error(f"Supabase error: No data returned")
                return jsonify({
                    "error": "Failed to fetch contacts",
                    "details": "No data returned from Supabase"
                }), 500

        except Exception as e:
            logger.error(f"Error fetching contacts: {e}")
            return jsonify({"error": str(e)}), 500
