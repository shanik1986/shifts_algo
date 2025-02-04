from flask import Blueprint, render_template, jsonify, request
from app.google_sheets.import_sheet_data import get_fresh_data
from app.scheduler.shifts_algo import run_shift_algorithm
from app.scheduler.constants import DAYS, SHIFTS

bp = Blueprint('main', __name__)
TIMEOUT_SECONDS = 15

@bp.route('/')
def index():
    return render_template('index.html', DAYS=DAYS, SHIFTS=SHIFTS)

@bp.route('/generate_schedule', methods=['POST'])
def generate_schedule():
    # Get max_weekend from the request JSON data
    data = request.get_json()
    max_weekend = int(data.get('max_weekend', 1))  # Default to 1 if not provided
    
    # Get fresh data using the centralized function with max_weekend parameter
    shift_group = get_fresh_data(max_weekend=max_weekend)
    
    # Run the algorithm with fresh data
    success, assignments, reason, shift_counts, people = run_shift_algorithm(
        shift_group=shift_group,
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