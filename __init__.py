from flask import Flask, Blueprint
from flask_cors import CORS
from supabase import create_client, Client
from config import Config
from dotenv import load_dotenv
import complain
import royalty
import license
import map
import contact
import minerpage
import unlicensedminer
import authentication

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for all routes
    # change the resource to front end deployed link
    # CORS(app, origins=["https://your-frontend-domain.com"])
    # CORS(app, resources={r"/*": {"origins": "*"}})

    CORS(app, resources={r"/*": {"origins": ["https://ceylonminefront.netlify.app", "http://localhost:3000"]}})

    #  CORS(app, resources={
    # r"/*": {
    #     "origins": ["https://ceylonminefront.netlify.app", "http://localhost:3000"],
    #     "methods": ["GET" , "POST"],
    #     "allow_headers": ["Content-Type", "Authorization"]
    #     }
    # })

    # Initialize Supabase client
    load_dotenv()  # Load environment variables from .env file
    supabase: Client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])
    app.supabase = supabase  # Attach Supabase client to the app

    # Create and register Blueprints
    complaints_bp = Blueprint('complaints', __name__, url_prefix='/complaints')
    royalty_bp = Blueprint('royalty', __name__, url_prefix='/royalty')
    license_bp = Blueprint('license', __name__, url_prefix='/license')
    map_bp = Blueprint('map',__name__, url_prefix='/map')
    contact_bp = Blueprint('contact', __name__,url_prefix='/contact')
    minerpage_bp = Blueprint('minerpage', __name__, url_prefix='/miner')
    unlicensedminer_bp = Blueprint('unlicensedminer', __name__, url_prefix='/unlicensedminer')
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

    # Register the routes with the blueprints
    complain.init_routes(complaints_bp)
    royalty.init_routes(royalty_bp)
    license.init_routes(license_bp)
    map.init_routes(map_bp)
    contact.init_routes(contact_bp)
    minerpage.init_routes(minerpage_bp)
    unlicensedminer.init_routes(unlicensedminer_bp)
    # authentication.init_routes(auth_bp)

    # Register blueprints with the app
    app.register_blueprint(complaints_bp)
    app.register_blueprint(royalty_bp)
    app.register_blueprint(license_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(minerpage_bp)
    app.register_blueprint(unlicensedminer_bp)
    app.register_blueprint(auth_bp)

    return app