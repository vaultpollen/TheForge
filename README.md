TheForge is meant to be an all-in-one dashboard with which a user can play around with functions pertaining to sports analytics, sports betting and daily fantasy. It contains scripts that scrape statistics, sportsbook odds, daily fantasy projections, and news to perform tasks and calculations that include but are not limited to: Monte Carlo simulations, Poisson distributions, fantasy lineup optimization and building, expected value calculations, streak calculators, and some more miscellaneous fun tools like pulling ESPN's top stories and converting the text to speech. I've also set some of the scripts to run remotely from a phone, using SSH and iOS shortcuts, and email the output of the script to the user. 

Simple to use. Type 'help' to see a list of available commands. Each command is a script with the function fire(), and you would simply type command_name.fire() to run it.

I am slowly repurposing what was at first proprietary code to be open source. Proving to be kind of difficult because many of these scripts work in tandem with custom Google Sheets pages. Thinking about changing it to work with Excel or just stop being lazy and do all the data manipulation through Pandas. 

Will add in depth instructions on how to use the packages and functions once it is fleshed out. This is all hardcore arcane spaghetti code. 
Fair warning. I am not a classically trained developer. 
