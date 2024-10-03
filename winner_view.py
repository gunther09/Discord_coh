import nextcord
from nextcord.ui import Button, View
from nextcord.ext import commands
from firebase import firebase_config
from bot_setup import bot

class WinnerView(View):
    def __init__(self, team_data):
        super().__init__(timeout=None)
        self.team_data = team_data
        self.winner = None
        self.axis_won_button = Button(label="Axis won", style=nextcord.ButtonStyle.primary, custom_id="axis_won")
        self.axis_won_button.callback = self.axis_won_callback
        self.allies_won_button = Button(label="Allies won", style=nextcord.ButtonStyle.primary, custom_id="allies_won")
        self.allies_won_button.callback = self.allies_won_callback

        self.add_item(self.axis_won_button)
        self.add_item(self.allies_won_button)

    async def axis_won_callback(self, interaction: nextcord.Interaction):
        self.winner = "Axis"
        await interaction.channel.send("Axis won selected. Do you want to save the result to the database? (Y/N)")
        self.disable_buttons()
        await interaction.message.edit(view=self)
        bot.add_listener(self.confirm_save, "on_message")

    async def allies_won_callback(self, interaction: nextcord.Interaction):
        self.winner = "Allies"
        await interaction.channel.send("Allies won selected. Do you want to save the result to the database? (Y/N)")
        self.disable_buttons()
        await interaction.message.edit(view=self)
        bot.add_listener(self.confirm_save, "on_message")

    def disable_buttons(self):
        self.axis_won_button.disabled = True
        self.allies_won_button.disabled = True

    async def confirm_save(self, message: nextcord.Message):
        if message.content.lower() == 'y':
            self.record_winner(self.winner, self.team_data)
            await message.channel.send(f"Winner recorded: {self.winner}\n\nUm neue Teams zu bauen gib !elo als Nachricht ein.")
        elif message.content.lower() == 'n':
            await message.channel.send("Result not saved. To build new teams, type !elo.")
        bot.remove_listener(self.confirm_save, "on_message")

    def record_winner(self, winner, team_data):
        db = firebase_config.db
        formatted_team_data = self.format_team_data(winner, team_data)
        data = {
            'winner': winner,
            'teams': formatted_team_data,
            'timestamp': nextcord.utils.utcnow()
        }
        db.collection('game_results').add(data)
        print(f"Winner recorded: {winner}")
        print("Formatted Team Data:")
        for team, players in formatted_team_data.items():
            print(f"Team: {team}")
            for player in players:
                print(f"  Alias: {player['Alias']}, MaxELO: {player['MaxELO']}")

    def format_team_data(self, winner, team_data):
        formatted_data = {
            "Axis": [],
            "Allies": []
        }
        for team, players in team_data.items():
            for player in players:
                player_data = {
                    "Alias": player['Spieler'],
                    "MaxELO": player['MaxAxis'] if team == "Axis" else player['MaxAllies']
                }
                formatted_data[team].append(player_data)
        return formatted_data

    async def modified_callback(self, interaction: nextcord.Interaction):
        # Fetch players from Firebase and adjust ratings
        db = firebase_config.db
        player_docs = db.collection('players').stream()
        adjusted_team_data = self.adjust_player_ratings(player_docs, self.team_data)

        # Send adjusted teams
        await interaction.channel.send("Teams have been modified based on previous results:")
        for team, players in adjusted_team_data.items():
            team_message = f"Team: {team}\n" + "\n".join([f"Alias: {player['Alias']}, Adjusted MaxELO: {player['MaxELO']} (Change: {player['ELO Change']})" for player in players])
            await interaction.channel.send(team_message)

    def adjust_player_ratings(self, player_docs, team_data):
        adjustment_base = 50  # Base adjustment factor for each win or loss
        player_dict = {doc.to_dict().get('alias'): doc.to_dict() for doc in player_docs}

        adjusted_team_data = {
            "Axis": [],
            "Allies": []
        }

        db = firebase_config.db

        for team, players in team_data.items():
            for player in players:
                alias = player['Spieler']
                if alias in player_dict:
                    player_info = player_dict[alias]

                    # Fetch player stats from Firebase
                    games_won = 0
                    games_lost = 0

                    game_results_ref = db.collection('game_results')
                    games = game_results_ref.stream()

                    # Calculate wins and losses
                    for game in games:
                        game_data = game.to_dict()
                        teams = game_data.get('teams', {})
                        winner = game_data.get('winner', '')

                        for team_name, team_players in teams.items():
                            for team_player in team_players:
                                if team_player['Alias'] == alias:
                                    if team_name == winner:
                                        games_won += 1
                                    else:
                                        games_lost += 1

                    # Adjust the rating based on previous results
                    max_elo_key = 'MaxAxis' if team == "Axis" else 'MaxAllies'
                    original_elo = player[max_elo_key].replace(',', '')  # Remove comma from ELO value
                    adjustment = (games_won - games_lost) * adjustment_base

                    # Calculate new ELO and append to adjusted data
                    try:
                        new_elo = int(original_elo) + adjustment
                    except ValueError:
                        new_elo = int(float(original_elo)) + adjustment

                    adjusted_team_data[team].append({
                        "Alias": alias,
                        "MaxELO": new_elo,
                        "ELO Change": adjustment
                    })

        return adjusted_team_data
