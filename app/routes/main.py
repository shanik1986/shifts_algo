from flask import g, Blueprint, render_template, jsonify
import time
from functools import wraps
from app.google_sheets.import_sheet_data import get_fresh_data
from app.scheduler.shifts_algo import run_shift_algorithm

# Define the timeout constant at module level
TIMEOUT_SECONDS = 15

bp = Blueprint('main', __name__)

@bp.before_request
def before_request():
    g.request_active = True

@bp.after_request
def after_request(response):
    g.request_active = False
    return response

def timeout_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > TIMEOUT_SECONDS:
            return jsonify({
                'error': 'Operation timed out. Please try again.'
            }), 408
        
        return result
    return wrapper

@bp.route('/')
def index():
    return render_template('index.html', timeout_seconds=TIMEOUT_SECONDS)

@bp.route('/generate_schedule', methods=['POST'])
@timeout_handler
def generate_schedule():
    # Get fresh data using the centralized function
    shift_constraints, shift_requirements = get_fresh_data()
    
    # Run the algorithm with fresh data
    success, assignments, reason, shift_counts, people = run_shift_algorithm(
        shift_requirements=shift_requirements,
        shift_constraints=shift_constraints
    )
    
    if success:
        result = {
            'success': True,
            'assignments': assignments,
            'shifts_per_person': {
                person['name']: shift_counts[person['name']] 
                for person in people
            }
        }
    else:
        result = {
            'success': False,
            'reason': reason
        }
    
    return jsonify(result) 