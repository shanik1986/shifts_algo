from app.scheduler.shift_group import ShiftGroup
from app.scheduler.shift import Shift
from app.scheduler.person import Person
from app.google_sheets.import_sheet_data import get_fresh_data

def test_ranking():
    # Get data from Google Sheets using your existing function
    shift_group = get_fresh_data()
    
    print("\n=== Starting Shift Analysis ===\n")
    
    # Calculate constraint scores for all people
    for person in shift_group.people:
        person.calculate_constraint_score(shift_group)
    
    # Get shift type ratios and display summary
    type_ratios = shift_group.get_shift_type_ratios()
    
    print("=== Shift Type Analysis ===")
    # Sort shift types by their ratios (most constrained first)
    sorted_types = sorted(type_ratios.items(), key=lambda x: x[1])
    
    for shift_type, ratio in sorted_types:
        unstaffed = [s for s in shift_group.shifts if not s.is_staffed and s.shift_type == shift_type]
        total_needed = sum(s.needed for s in unstaffed)
        total_capacity = sum(p.get_capacity_by_type(shift_type) for p in shift_group.people)
        
        print(f"\nShift Type: {shift_type}")
        print(f"  * Total needed: {total_needed}")
        print(f"  * Total capacity: {total_capacity}")
        print(f"  * Constraint ratio: {ratio:.2f}")
        print(f"  * Unstaffed shifts: {len(unstaffed)}")
    print("\n" + "=" * 50 + "\n")
    
    # Get ranked shifts
    ranked_shifts = shift_group.rank_shifts(shift_group.people)
    
    # Detailed analysis of each shift
    print("\n=== Detailed Shift Analysis ===\n")
    for rank, shift in enumerate(ranked_shifts, 1):
        eligible_people = [p for p in shift_group.people if p.is_eligible_for_shift(shift)]
        
        print(f"\nShift #{rank}: {shift.shift_day} {shift.shift_time}")
        print(f"Type: {shift.shift_type}")
        print(f"Needed: {shift.needed}")
        print(f"Eligible people count: {len(eligible_people)}")
        print("Eligible people and their scores:")
        for person in eligible_people:
            print(f"  - {person.name}")
            print(f"    * Constraint score: {person.constraint_scores[shift.shift_type]:.2f}")
            print(f"    * Remaining capacity: {person.get_capacity_by_type(shift.shift_type)}")
            
        total_capacity = sum(p.constraint_scores[shift.shift_type] for p in eligible_people)
        print(f"Total capacity: {total_capacity:.2f}")
        print(f"Constraint score (capacity/needed): {total_capacity/shift.needed if total_capacity > 0 else 'inf'}")
        print("-" * 50)

if __name__ == "__main__":
    test_ranking() 