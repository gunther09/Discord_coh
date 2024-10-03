import pandas as pd

# Function to process and display the data
def process_and_display_data(data_2v2, data_3v3, data_4v4):
    # Combine data
    if not data_2v2.empty and not data_3v3.empty:
        data = data_2v2.merge(data_3v3, on=["relic_id", "alias"], suffixes=("_2v2", "_3v3"))
        if not data_4v4.empty:
            data = data.merge(data_4v4, on=["relic_id", "alias"], suffixes=("", "_4v4"))
    elif not data_2v2.empty:
        data = data_2v2
    elif not data_3v3.empty:
        data = data_3v3
    else:
        raise Exception("No data available.")

    # List of columns to calculate max ELOs
    max_elo_columns = ['2v2_axis_elo', '2v2_allies_elo', '3v3_axis_elo', '3v3_allies_elo']
    if '4v4_axis_elo' in data.columns and '4v4_allies_elo' in data.columns:
        max_elo_columns.extend(['4v4_axis_elo', '4v4_allies_elo'])

    # Process the data (e.g., calculating max values)
    data['maxElo'] = data[max_elo_columns].max(axis=1)

    german_elo_columns = ['german_2v2_elo', 'german_3v3_elo']
    if 'german_4v4_elo' in data.columns:
        german_elo_columns.append('german_4v4_elo')
    data['maxGerman'] = data[german_elo_columns].max(axis=1)

    british_elo_columns = ['british_2v2_elo', 'british_3v3_elo']
    if 'british_4v4_elo' in data.columns:
        british_elo_columns.append('british_4v4_elo')
    data['maxBritish'] = data[british_elo_columns].max(axis=1)

    american_elo_columns = ['american_2v2_elo', 'american_3v3_elo']
    if 'american_4v4_elo' in data.columns:
        american_elo_columns.append('american_4v4_elo')
    data['maxAmerican'] = data[american_elo_columns].max(axis=1)

    dak_elo_columns = ['dak_2v2_elo', 'dak_3v3_elo']
    if 'dak_4v4_elo' in data.columns:
        dak_elo_columns.append('dak_4v4_elo')
    data['maxDak'] = data[dak_elo_columns].max(axis=1)

    # Max Allies and Max Axis calculations
    data['MaxAllies'] = data[['maxBritish', 'maxAmerican']].max(axis=1)
    data['MaxAxis'] = data[['maxDak', 'maxGerman']].max(axis=1)

    # Select the relevant columns for display
    display_data = data[['alias', 'maxElo', 'maxGerman', 'maxBritish', 'maxAmerican', 'maxDak', 'MaxAllies', 'MaxAxis']]

    # Rename columns for better readability
    display_data.columns = ['Spieler', 'maxELO', 'Wehr', 'Brits', 'USF', 'DAK', 'MaxAllies', 'MaxAxis']

    # Sort data by maxELO in descending order
    display_data = display_data.sort_values(by='maxELO', ascending=False)

    # Format numbers with thousand separator
    display_data_formatted = display_data.copy()
    for col in ['maxELO', 'Wehr', 'Brits', 'USF', 'DAK', 'MaxAllies', 'MaxAxis']:
        display_data_formatted[col] = display_data[col].map(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)

    # Group data by hundreds
    grouped_data = []
    current_group = None
    for index, row in display_data_formatted.iterrows():
        maxELO = int(row['maxELO'].replace(',', ''))
        group = maxELO // 100 * 100
        if current_group != group:
            if current_group is not None:
                grouped_data.append(pd.Series([""] * len(row), index=row.index))
            current_group = group
        grouped_data.append(row)

    grouped_data_df = pd.DataFrame(grouped_data)

    print("Data fetched and processed successfully.")
    return grouped_data_df
