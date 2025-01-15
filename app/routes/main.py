from flask import Blueprint, render_template, jsonify
import time
from app.scheduler.shifts_algo import run_shift_algorithm
from functools import wraps

bp = Blueprint('main', __name__)

def timeout_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 5:
            return jsonify({
                'error': 'Operation timed out. Please try again.'
            }), 408
        
        return result
    return wrapper

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

@bp.route('/generate_schedule', methods=['POST'])
@timeout_handler
def generate_schedule():
    # Run the algorithm
    success, assignments, reason, shift_counts, people = run_shift_algorithm()
    
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