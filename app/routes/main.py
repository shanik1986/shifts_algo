from flask import Blueprint, render_template, jsonify
from app.google_sheets.import_sheet_data import get_fresh_data, parse_shift_requirements
from app.scheduler.shifts_algo import run_shift_algorithm
from app.scheduler.constants import DAYS, SHIFTS

bp = Blueprint('main', __name__)
TIMEOUT_SECONDS = 15

@bp.route('/')
def index():
    return render_template('index.html', DAYS=DAYS, SHIFTS=SHIFTS)

@bp.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    # Get fresh data using the centralized function
    shift_group, people = get_fresh_data()
    
    # Run the algorithm with fresh data
    success, assignments, reason, shift_counts, people = run_shift_algorithm(
        shift_group=shift_group,
        people=people,
        timeout=TIMEOUT_SECONDS
    )
    
    if success:
        result = {
            'success': True,
            'assignments': assignments,
            'shifts_per_person': shift_counts  # shift_counts is already in the right format
        }
    else:
        result = {
            'success': False,
            'reason': reason
        }
    
    return jsonify(result) 