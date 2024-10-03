from nextcord import Interaction
import firebase.firebase_config  # Importiere Firebase-Konfiguration
from datetime import datetime

def register_stats_commands(bot, guild_id):
    @bot.slash_command(name="stats", description="View game statistics", guild_ids=[guild_id])
    async def stats(interaction: Interaction):
        pass

    @stats.subcommand(name="sums", description="Show all game results")
    async def stats_sums(interaction: Interaction):
        db = firebase.firebase_config.db
        game_results_ref = db.collection('game_results')
        docs = game_results_ref.stream()

        # Dictionary to store win and loss counts
        player_stats = {}

        for doc in docs:
            data = doc.to_dict()
            winner = data.get('winner', 'Unknown')
            teams = data.get('teams', {})

            for team, players in teams.items():
                for player in players:
                    alias = player['Alias']
                    if alias not in player_stats:
                        player_stats[alias] = {'Axis Wins': 0, 'Axis Losses': 0, 'Allies Wins': 0, 'Allies Losses': 0}
                    
                    if winner == team:
                        if team == 'Axis':
                            player_stats[alias]['Axis Wins'] += 1
                        else:
                            player_stats[alias]['Allies Wins'] += 1
                    else:
                        if team == 'Axis':
                            player_stats[alias]['Axis Losses'] += 1
                        else:
                            player_stats[alias]['Allies Losses'] += 1

        if player_stats:
            # Format the results into a table
            table_header = f"{'Player':<20}{'Axis Wins':<10}{'Axis Losses':<12}{'Allies Wins':<12}{'Allies Losses':<13}\n"
            table_rows = [
                f"{alias:<20}{stats['Axis Wins']:<10}{stats['Axis Losses']:<12}{stats['Allies Wins']:<12}{stats['Allies Losses']:<13}"
                for alias, stats in player_stats.items()
            ]
            results_message = table_header + "\n".join(table_rows)
            await interaction.response.send_message(f"Game Results:\n```\n{results_message}\n```")
        else:
            await interaction.response.send_message("No game results found.")

    @stats.subcommand(name="timeline", description="Show game results in a timeline")
    async def stats_timeline(interaction: Interaction):
        db = firebase.firebase_config.db
        game_results_ref = db.collection('game_results')
        docs = game_results_ref.order_by("timestamp").stream()

        # Convert the stream to a list and get the last 10 entries
        docs_list = list(docs)[-10:]

        results = []
        for doc in docs_list:
            data = doc.to_dict()
            timestamp = data.get('timestamp', 'Unknown')
            winner = data.get('winner', 'Unknown')
            teams = data.get('teams', {})

            # Convert timestamp to readable format if it's not 'Unknown'
            if timestamp != 'Unknown':
                timestamp = datetime.fromtimestamp(timestamp.timestamp()).strftime('%Y-%m-%d %H:%M:%S')

            axis_players = [player['Alias'][:10] for player in teams.get('Axis', [])]
            allies_players = [player['Alias'][:10] for player in teams.get('Allies', [])]

            axis_str = ", ".join(axis_players)
            allies_str = ", ".join(allies_players)

            results.append(f"{timestamp:<20} | {'Axis':<6} | {axis_str:<40} | {winner}")
            results.append(f"{'':<20} | {'Allies':<6} | {allies_str:<40} |")

        if results:
            # Format the results into a table
            table_header = f"{'Date':<20} | {'Team':<6} | {'Players':<40} | {'Winner'}\n"
            results_message = table_header + "\n" + "\n".join(results)
            await interaction.response.send_message(f"Game Timeline (Last 10 Results):\n```\n{results_message}\n```")
        else:
            await interaction.response.send_message("No game results found.")
