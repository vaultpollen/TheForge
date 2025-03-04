# To do: Calculate spread cover percentages
import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO
import numpy as np
from scipy.stats import poisson
from collections import Counter
import scrape_odds

# Load CSV file with team codes and their respective baseball-reference.com URLs
# Use direct filepath for remote access
team_file_path = r"path\to\team_pages.csv" # Path to file that contains team codes and their respective pages on baseball-reference
team_file = pd.read_csv(team_file_path, header=None)

def get_team_url(team_code):
    # Search for the team's URL based on their team code
    team_url = team_file.loc[team_file[0] == team_code, 1]

    # Convert the DataFrame object to a string
    if not team_url.empty:
        return team_url.iloc[0]
    else:
        print(f"URL for team code {team_code} not found.")
        return None

def scrape_game_data(team_url):
    # Send a GET request to the team's URL
    response = requests.get(team_url)

    # Check if the request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table element with ID 'team_schedule'
        table = soup.find('table', {'id': 'team_schedule'})

        # Check if the table element was found
        if table:
            # Convert the HTML table to a DataFrame
            html_str = str(table)
            try:
                df = pd.read_html(StringIO(html_str))[0]
                return df
            except ValueError:
                print(f"Could not parse table for URL: {team_url}")
                return None
        else:
            print(f"Table with ID 'team_schedule' not found on page: {team_url}")
            return None
    else:
        print(f"Failed to retrieve webpage: {team_url}. Status code: {response.status_code}")
        return None

def data_analysis(team_log):
    # Drop missing and non-numerical values from the team's runs scored column
    team_log = team_log.dropna(subset=['R'])
    team_log.loc[:, 'R'] = pd.to_numeric(team_log['R'], errors='coerce')

    # Calculate the 1st and 3rd quartile, low, high, and adjusted average for the team's runs scored
    q1 = team_log['R'].quantile(0.25)
    q3 = team_log['R'].quantile(0.75)
    low = q1 - (1.5 * (q3 - q1))
    high = q3 + (1.5 * (q3 - q1))

    # Filter all values between 'low' and 'high', then calculate the average
    filtered = team_log['R'][(team_log['R'] > low) & (team_log['R'] < high)]
    adj_avg = filtered.mean()

    # Calculate the cumulative Poisson distribution from 0 to 15
    poisson_dist = [poisson.cdf(k, mu=adj_avg) for k in range(16)]

    # Print the results
    #for k, cdf in enumerate(poisson_dist):
        #print(f"P(X <= {k} = {cdf:.4f}")

    # Perform a Monte Carlo simulation using the Poisson distribution results
    num_simulations = 10000
    results = []

    for _ in range(num_simulations):
        random = np.random.rand()
        for k, cdf in enumerate(poisson_dist):
            if random < cdf:
                results.append(k)
                break

    return results

def final_simulation(away_results, home_results, total_line):
    # Combine the results of both Monte Carlo simulations as game scores
    final_scores = [
        (away_score, home_score, away_score + home_score)
        for away_score, home_score in zip(away_results, home_results)
    ]

    # Count the occurrences of each unique combination of scores
    count = Counter(final_scores)

    # Convert the results to a DataFrame
    results = pd.DataFrame.from_dict(count, orient='index', columns=['Count'])
    results.reset_index(inplace=True)
    results[['Away Score', 'Home Score', 'Total Score']] = pd.DataFrame(results['index'].tolist(), index=results.index)
    results.drop(columns='index', inplace=True)


    # Calculate the total number of game simulations
    sim_total = results['Count'].sum()

    # Calculate the probability of each score combination
    results['Probability'] = results['Count'] / sim_total
    print(results)

    # Calculate the over/under percentage based in the user input total line
    total_line_new = float(total_line)
    over_chance = results[results['Total Score'] > total_line_new]['Count'].sum()
    under_chance = results[results['Total Score'] <= total_line_new]['Count'].sum()

    # Change to percentages
    over_percentage = (over_chance / sim_total) * 100
    under_percentage = (under_chance / sim_total) * 100

    # Print over/under probabilities
    print(f"Percentage of games where the total score is over {total_line}: {over_percentage:.2f}%")
    print(f"Percentage of games where the total score is under {total_line}: {under_percentage:.2f}%")

    # Exclude ties and calculate win percentages
    non_tied_results = results[results['Away Score'] != results['Home Score']]

    # Recalculate total simulations excluding ties
    non_tied_total = non_tied_results['Count'].sum()

    # Calculate win percentages
    away_wins = non_tied_results[non_tied_results['Away Score'] > non_tied_results['Home Score']]['Count'].sum()
    away_win_percentage = (away_wins / non_tied_total) * 100

    home_wins = non_tied_results[non_tied_results['Away Score'] < non_tied_results['Home Score']]['Count'].sum()
    home_win_percentage = (home_wins / non_tied_total) * 100

    # Print win percentages
    print(f"Percentage of games where the away team wins: {away_win_percentage:.2f}%")
    print(f"Percentage of games where the home team wins: {home_win_percentage:.2f}%")

    return over_percentage, under_percentage, away_win_percentage, home_win_percentage

def ev_calculation(a_ml_odds, h_ml_odds, over_odds, under_odds, a_win, h_win, over_chance, under_chance, total, away_team, home_team):
    # Calculate the implied probabilities
    def implied_probability(odds):
        if odds > 0:
            return 100 / (odds + 100) * 100
        else:
            return -odds / (-odds + 100) * 100

    a_ml_implied = implied_probability(a_ml_odds)
    h_ml_implied = implied_probability(h_ml_odds)
    over_implied = implied_probability(over_odds)
    under_implied = implied_probability(under_odds)

    # Compare the calculated implied odds to the probabilities calculated by the simulation
    a_ml_edge = a_win - a_ml_implied
    h_ml_edge = h_win - h_ml_implied
    over_edge = over_chance - over_implied
    under_edge = under_chance - under_implied

    # Initialize the list for +EV bets
    ev_bets = []

    # Identify +EV bets
    if a_ml_edge > 0:
        bet_info = f"Moneyline: {away_team} | Edge: {a_ml_edge:.2f}% | Odds: {a_ml_odds}\n"
        print(bet_info)
        ev_bets.append(bet_info)
    if h_ml_edge > 0:
        bet_info = f"Moneyline: {home_team} | Edge: {h_ml_edge:.2f}% | Odds: {h_ml_odds}\n"
        print(bet_info)
        ev_bets.append(bet_info)
    if over_edge > 0:
        bet_info = f"{away_team} vs {home_team} Over: {total} | Edge: {over_edge:.2f}% | Odds: {over_odds}\n"
        print(bet_info)
        ev_bets.append(bet_info)
    if under_edge > 0:
        bet_info = f"{away_team} vs {home_team} Under: {total} | Edge: {under_edge:.2f}% | Odds: {under_odds}\n"
        print(bet_info)
        ev_bets.append(bet_info)

    return ev_bets

def read_odds_csv(file_path):
    games = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)

        for i in range(0, len(rows), 2):
            try:
                team_a = rows[i]
                team_b = rows[i + 1]

                game = {
                    "away_team": team_a[0].strip(),
                    "home_team": team_b[0].strip(),
                    "spread_a": team_a[1].strip() if len(team_a) > 1 else '',
                    "spread_b": team_b[1].strip() if len(team_b) > 1 else '',
                    "over_odds": int(team_a[2].strip().replace('−', '-')) if len(team_a) > 2 else None,
                    "under_odds": int(team_b[2].strip().replace('−', '-')) if len(team_b) > 2 else None,
                    "total": float(team_a[4].strip()) if len(team_a) > 3 else None,
                    "moneyline_away": int(team_a[5].strip().replace('−', '-')) if len(team_a) > 5 else None,
                    "moneyline_home": int(team_b[5].strip().replace('−', '-')) if len(team_b) > 5 else None
                }
                games.append(game)
            except IndexError:
                print(f"Error processing rows {i} and {i+1}. Check if the CSV file has correct formatting.")
            except ValueError as ve:
                print(f"Value error: {ve} in rows {i} and {i+1}.")

    return games   

def main():
        # Scrape current slate's odds from DraftKings
        scrape_odds.scrape()

        # Load the scraped data
        games_path = r'path\to\mlb_dk_lines.csv' # This is a file output by scrape_odds.py
        games = read_odds_csv(games_path)
        all_ev_bets = []

        # Begin a loop that iterates through all the games in today's available slate
        for game in games:
            away_team = game['away_team']
            home_team = game['home_team']
            away_win_odds = game['moneyline_away']
            home_win_odds = game['moneyline_home']
            over_odds = game['over_odds']
            under_odds = game['under_odds']
            total_line = float(game['total'])

            print(f"\nSimulating game: {away_team} at {home_team}")
            print(f"Away Moneyline: {away_win_odds}, Home Moneyline: {home_win_odds}")
            print(f"Over Odds: {over_odds}, Under Odds: {under_odds}")
            print(f"Total Line: {total_line}\n")
        
            # Get URLs for both teams
            away_url = get_team_url(away_team)
            home_url = get_team_url(home_team)
            
            # Scrape game logs for both teams
            away_data = scrape_game_data(away_url)
            home_data = scrape_game_data(home_url)

            if away_data is None or home_data is None:
                print(f"Skipping simulation for {away_team} vs {home_team} due to missing data.\n")
                continue

            # Perform data analysis on game logs
            away_analysis = data_analysis(away_data)
            home_analysis = data_analysis(home_data)

            # Perform final Monte Carlo simulation functions
            over_percentage, under_percentage, away_win_percentage, home_win_percentage = final_simulation(
                away_analysis, home_analysis, total_line
                )

            # Calculate the EV of the moneyline and over/under totals based on slate data
            ev_bets = ev_calculation(
                away_win_odds, home_win_odds,
                over_odds, under_odds,
                away_win_percentage, home_win_percentage,
                over_percentage, under_percentage,
                total_line,
                away_team, home_team,
            )

            all_ev_bets.extend(ev_bets)
            print("\n" + "-"*50 + "\n")     

        # Display all +EV bets
        if all_ev_bets:
            print("Summary of +EV Bets:\n")
            for bet in all_ev_bets:
                print(bet)
        else:
            print("No +EV bets found for today's slate.")

        # Removed this because it was bugging the remote access
        #quit_script = input("\nPress enter to continue...")
if __name__ == "__main__":
    main()
