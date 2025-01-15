from flask import Blueprint, render_template, jsonify
import time
from app.scheduler.shifts_algo import run_shift_algorithm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/run-algorithm')
def run_algorithm():
    # Run the algorithm
    success, assignments, reason, shift_counts, people = run_shift_algorithm()
    
    if success:
        # Format the results
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