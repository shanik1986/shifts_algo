from flask import Blueprint, render_template, jsonify
from app.google_sheets.import_sheet_data import get_fresh_data
from app.scheduler.shifts_algo import run_shift_algorithm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/generate_schedule', methods=['POST'])
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