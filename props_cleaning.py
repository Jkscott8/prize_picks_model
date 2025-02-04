import csv
import pandas as pd

def extract_columns_from_csv(input_filename, output_filename):
    # Open the input CSV file to read
    with open(input_filename, mode='r') as infile:
        reader = csv.DictReader(infile)

        # Define the output CSV headers
        header = ['League', 'PlayerName', 'Stat', 'PropLine',
                  'Type']

        # Open the output CSV file to write
        with open(output_filename, mode='w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header)
            writer.writeheader()  # Write header to output file

            # Iterate over each row in the input CSV file
            for row in reader:
                # Write the selected attributes to the new file
                writer.writerow({
                    'League': row.get('attributes.league', ''),
                    'PlayerName': row.get('attributes.name', ''),
                    'Stat': row.get('attributes.stat_display_name', ''),
                    'PropLine': row.get('attributes.line_score', ''),
                    'Type': row.get('attributes.odds_type', '')
                })



extract_columns_from_csv("NFL_Prize_picks.csv", 'NFL_PrizeProps.csv')
extract_columns_from_csv("NBA_Prize_picks.csv", 'NBA_PrizeProps.csv')
