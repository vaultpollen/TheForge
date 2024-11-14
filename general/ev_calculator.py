# Extremely basic EV calculator that takes odds from two sides of a bet on a sportsbook the user deems to be "sharp", devigs those odds to calculate the fair value, then accepts odds from the user that they want to compare to the "fair" probability of the event.
# This is useful for comparing lines against sharp books like Pinnacle. You would input the two sides of Pinnacle's line, then input the odds of the bet you deem to have value on either side of the bet.
# After this you would specify whether you want to compare against sharp line 1 or 2 (the first two odds you put in, respectively). The script will devig the sharp odds and tell you the expected value of your chosen odds.
# Let's say one of Jayson Tatum's O/U Points lines is -132 (O) and +100 (U) on Pinnacle. You put -132, then +100 into the script. Then let's say you found a sportsbook that's offering the same Over at +115.
# You would put in +115, and then 1 because the Over is the first sharp line. Under would be 2. Same idea for all lines. In this case the expected value would be 0.14, which is very good value.
from typing import Tuple

def american_to_decimal(odds: float) -> float:
    if odds > 0:
        return (odds / 100) + 1
    else:
        return (100 / abs(odds)) + 1

def decimal_to_implied_prob(decimal_odds: float) -> float:
    return 1 / decimal_odds

def vig_adjusted_probs(prob1: float, prob2: float) -> Tuple[float, float]:
    total_prob = prob1 + prob2
    return prob1 / total_prob, prob2 / total_prob

def expected_value(proposed_odds: float, implied_prob: float) -> float:
    decimal_odds = american_to_decimal(proposed_odds)
    return (decimal_odds * implied_prob) - 1

def calculate_ev(sharp1: float, sharp2: float, proposed_odds: float, side: int) -> Tuple[float, float, float, float]:
    # Convert sharp odds to decimal
    sharp1_decimal = american_to_decimal(sharp1)
    sharp2_decimal = american_to_decimal(sharp2)
    
    # Get implied probabilities from sharp odds
    prob1 = decimal_to_implied_prob(sharp1_decimal)
    prob2 = decimal_to_implied_prob(sharp2_decimal)
    
    # Calculate devigged (fair) probabilities
    fair_prob1, fair_prob2 = vig_adjusted_probs(prob1, prob2)
    
    # Convert devigged probabilities back to decimal odds
    fair_odds1 = 1 / fair_prob1
    fair_odds2 = 1 / fair_prob2
    
    # Determine the chosen side's probability
    chosen_prob = fair_prob1 if side == 1 else fair_prob2
    
    # Calculate expected value of the proposed bet
    ev = expected_value(proposed_odds, chosen_prob)
    return fair_odds1, fair_odds2, fair_prob1, fair_prob2, ev

while True:
    try:
        # Take user inputs
        sharp1_odds = input("Enter sharp1 odds (type 'quit()' to exit): ")
        if sharp1_odds.lower() == 'quit()':
            break
        sharp1_odds = float(sharp1_odds)
        
        sharp2_odds = float(input("Enter sharp2 odds: "))
        proposed_bet_odds = float(input("Enter proposed bet odds: "))
        side = int(input("Choose side (1 for sharp1, 2 for sharp2): "))
        
        # Calculate devigged odds, probabilities, and EV
        fair_odds1, fair_odds2, fair_prob1, fair_prob2, ev = calculate_ev(sharp1_odds, sharp2_odds, proposed_bet_odds, side)
        
        # Output devigged odds and probabilities
        print(f"\nDevigged (Fair) Odds and Probabilities:")
        print(f"Sharp1 Fair Odds: {fair_odds1:.2f}, Fair Probability: {fair_prob1:.2%}")
        print(f"Sharp2 Fair Odds: {fair_odds2:.2f}, Fair Probability: {fair_prob2:.2%}")
        
        # Output expected value
        print(f"\nExpected Value (EV) of the proposed bet: {ev:.2f}\n")
        
    except ValueError:
        print("Invalid input. Please enter numeric values for odds and a valid side (1 or 2).\n")
