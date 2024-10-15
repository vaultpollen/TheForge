# Optimizer for DraftKings short slate Tennis (CPT/A-CPT/P). Spits out the highest FPPG lineup given DKSalaries.csv.
# Does not consider whether or not players are facing each other.
import pandas as pd
import os

def fire():
    # Update the working directory for file imports
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)

    # Load the CSV file
    file_path = 'DKSalaries.csv'
    data = pd.read_csv(file_path)

    # Set the salary cap
    salary_cap = 50000

    # Filter players by their roster positions
    cpt_players = data[data['Roster Position'] == 'CPT']
    a_cpt_players = data[data['Roster Position'] == 'A-CPT']
    p_players = data[data['Roster Position'] == 'P']

    # Function to validate if the lineup stays under the salary cap
    def is_valid_lineup(lineup):
        total_salary = sum(player.Salary for player in lineup)
        return total_salary <= salary_cap

    # Function to calculate the total points for the lineup
    def total_points(lineup):
        return sum(player.AvgPointsPerGame for player in lineup)

    # Initialize the best lineup and max points
    best_lineup = None
    max_points = 0

    # Iterate through combinations of CPT, A-CPT, and P
    for cpt in cpt_players.itertuples():
        for a_cpt in a_cpt_players.itertuples():
            if cpt.Name == a_cpt.Name:
                continue  # Skip if the same player is selected for CPT and A-CPT
            for p in p_players.itertuples():
                if p.Name in [cpt.Name, a_cpt.Name]:
                    continue  # Skip if the same player is selected for multiple positions
                lineup = [cpt, a_cpt, p]
                if is_valid_lineup(lineup):
                    points = total_points(lineup)
                    if points > max_points:
                        max_points = points
                        best_lineup = lineup

    # Output the best lineup found
    if best_lineup:
        print("Best Lineup:")
        for player in best_lineup:
            print(f"Name: {player.Name}, Position: {player._5}, Salary: {player.Salary}, AvgPointsPerGame: {player.AvgPointsPerGame}")
        print(f"Total Salary: {sum(player.Salary for player in best_lineup)}")
        print(f"Total AvgPointsPerGame: {total_points(best_lineup)}")
    else:
        print("No valid lineup found within the salary cap.")
