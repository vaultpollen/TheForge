import requests
from bs4 import BeautifulSoup
import csv

def scrape():
    # Load URL
    url = "https://sportsbook.draftkings.com/leagues/baseball/mlb"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find("div", id="root")
                   
    # Write teams and odds to CSV
    with open('mlb_dk_lines.csv', 'w', encoding='utf-8') as file:
        # Scrape away teams and odds
        row_elements = results.find_all("tr", class_=["", "break-line"])
        for row_element in row_elements:
            team = row_element.find("div", class_="event-cell__name-text")
            odds = row_element.find_all("span", class_="sportsbook-odds american default-color")
            total = row_element.find_all("span", class_="sportsbook-outcome-cell__line")
            moneyline = row_element.find_all("span", class_="sportsbook-odds american no-margin default-color")

            # Map weird abbreviation discrepancies to a dictionary
            replacement_map = {
                "CHI Cubs": "CHC",
                "WAS Nationals": "WSN",
                "KC Royals": "KCR",
                "NY Yankees": "NYY",
                "TB Rays": "TBR",
                "NY Mets": "NYM",
                "LA Dodgers": "LAD",
                "CHI White Sox": "CHW",
                "SD Padres": "SDP",
                "LA Angels": "LAA",
                "SF Giants": "SFG"
            }

            # Replace weird abbreviations with the correct team codes for functionality with the main script
            if team is not None:
                team_text = team.text.strip()

                if team_text in replacement_map:
                    team_text = replacement_map[team_text]
                
                # Write all relevant data to the CSV file
                #print(team_text.split()[0])
                file.write(team_text.split()[0])
                file.write(',')
                
                for a in odds:
                    #print(a.get_text())
                    file.write(a.get_text())
                    file.write(',')

                for b in total:
                    #print(b.get_text())
                    file.write(b.get_text())
                    file.write(',')
                    
                for c in moneyline:
                    #print(c.get_text())
                    file.write(c.get_text())
                    file.write(',')
                file.write('\n')
