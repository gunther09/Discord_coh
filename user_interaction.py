import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
import data_processing as dp
import data_fetching as df
from bot_setup import bot
from team_builder import build_balanced_teams
from itertools import combinations
import messages  # Import the messages module
from winner_view import WinnerView  # Import the WinnerView class

selected_players = []

class PlayerSelectionView(View):
    def __init__(self, players):
        super().__init__(timeout=None)
        self.value = None
        self.buttons = {}

        for player in players:
            if player:
                button = Button(label=player, style=nextcord.ButtonStyle.secondary, custom_id=player)
                button.callback = self.button_callback
                self.buttons[player] = button
                self.add_item(button)
                if len(self.children) == 25:
                    break

    async def button_callback(self, interaction: nextcord.Interaction):
        global selected_players
        player_name = interaction.data["custom_id"]
        if player_name in selected_players:
            selected_players.remove(player_name)
            self.buttons[player_name].style = nextcord.ButtonStyle.secondary
        else:
            selected_players.append(player_name)
            self.buttons[player_name].style = nextcord.ButtonStyle.success
        await interaction.response.edit_message(view=self)

class BuildTeamsView(View):
    def __init__(self, data):
        super().__init__(timeout=None)
        self.data = data
        build_teams_button = Button(label="Build Teams", style=nextcord.ButtonStyle.success, custom_id="build_teams")
        build_teams_button.callback = self.button_callback
        self.add_item(build_teams_button)

    async def button_callback(self, interaction: nextcord.Interaction):
        global selected_players
        if len(selected_players) < 2:
            await interaction.response.send_message("Please select at least 2 players to build teams.", ephemeral=True)
        else:
            players_sorted = sorted(self.data[self.data['Spieler'].isin(selected_players)].to_dict('records'), key=lambda x: int(x['maxELO'].replace(',', '')), reverse=True)
            team_1, team_2 = self.build_balanced_teams(players_sorted)
            sum_team_1 = sum(int(player['MaxAxis'].replace(',', '')) for player in team_1)
            sum_team_2 = sum(int(player['MaxAllies'].replace(',', '')) for player in team_2)

            team_1_message = "\n".join([f"{player['Spieler']:20}: {player['MaxAxis']:>6}" for player in team_1])
            team_2_message = "\n".join([f"{player['Spieler']:20}: {player['MaxAllies']:>6}" for player in team_2])

            team_1_message += f"\n\n{'Total MaxAxis':20}: {sum_team_1:,}"
            team_2_message += f"\n\n{'Total MaxAllies':20}: {sum_team_2:,}"

            table_message = f"```\n{'Team 1 (Axis)':<30} {'Team 2 (Allies)':<30}\n" + "="*60 + "\n"
            team_1_lines = team_1_message.split('\n')
            team_2_lines = team_2_message.split('\n')
            max_lines = max(len(team_1_lines), len(team_2_lines))

            for i in range(max_lines):
                line_1 = team_1_lines[i] if i < len(team_1_lines) else ""
                line_2 = team_2_lines[i] if i < len(team_2_lines) else ""
                table_message += f"{line_1:<30} {line_2:<30}\n"
            table_message += "```"

            team_data = {
                "Axis": team_1,
                "Allies": team_2
            }

            # Send the "Teams built successfully!" message as a new message
            await interaction.channel.send(messages.TEAMS_BUILT_SUCCESS)

            # Send the team table as a new message
            await interaction.channel.send(table_message)

            # Send a new message with OK and Modified buttons
            await interaction.channel.send("Are these teams fine?", view=ConfirmationView(team_data))

            selected_players = []

    def build_balanced_teams(self, players):
        players_sorted = sorted(players, key=lambda x: (int(x['MaxAxis'].replace(',', '')), int(x['MaxAllies'].replace(',', ''))), reverse=True)
        best_diff = float('inf')
        best_team_1 = best_team_2 = None

        for comb in combinations(players_sorted, len(players_sorted) // 2):
            team_1 = list(comb)
            team_2 = [player for player in players_sorted if player not in team_1]
            sum_team_1 = sum(int(player['MaxAxis'].replace(',', '')) for player in team_1)
            sum_team_2 = sum(int(player['MaxAllies'].replace(',', '')) for player in team_2)
            diff = abs(sum_team_1 - sum_team_2)
            if diff < best_diff:
                best_diff = diff
                best_team_1, best_team_2 = team_1, team_2

        return best_team_1, best_team_2

class ConfirmationView(View):
    def __init__(self, team_data):
        super().__init__(timeout=None)
        self.team_data = team_data

        ok_button = Button(label="OK", style=nextcord.ButtonStyle.success, custom_id="ok_button")
        ok_button.callback = self.ok_button_callback
        self.add_item(ok_button)

        modified_button = Button(label="Modified - noch nicht fertig", style=nextcord.ButtonStyle.primary, custom_id="modified_button")
        # Einfach Anders Button (neu hinzugefügt)
        einfach_anders_button = Button(label="Einfach Anders", style=nextcord.ButtonStyle.secondary, custom_id="einfach_anders_button")
        # Noch keine Callback-Funktion implementiert
        self.add_item(einfach_anders_button)
        modified_button.callback = self.modified_button_callback
        self.add_item(modified_button)

    async def ok_button_callback(self, interaction: nextcord.Interaction):
        # Proceed to winner selection view
        await interaction.response.send_message(messages.SELECT_WINNING_TEAM_PROMPT, view=WinnerView(self.team_data))

    async def modified_button_callback(self, interaction: nextcord.Interaction):
        # Handle team adjustment with the modified button
        modified_view = WinnerView(self.team_data)
        await modified_view.modified_callback(interaction)

@bot.command(name="elo")
async def elo(ctx):
    print("Fetching data on command...")
    try:
        global selected_players
        selected_players = []
        data_2v2, data_3v3, data_4v4 = await df.fetch_all_data(ctx)
        data = dp.process_and_display_data(data_2v2, data_3v3, data_4v4)
        message = data.to_string(index=False)
        await ctx.send(f'```\n{message}\n```')
        print("Data sent successfully.")

        player_names = data['Spieler'].dropna().tolist()

        player_views = [PlayerSelectionView(player_names[i:i+25]) for i in range(0, len(player_names), 25)]
        for player_view in player_views:
            await ctx.send(messages.SELECT_PLAYERS_PROMPT, view=player_view)

        build_teams_view = BuildTeamsView(data)
        await ctx.send(messages.BUILD_TEAMS_PROMPT, view=build_teams_view)
    except Exception as e:
        await ctx.send(f"Error occurred: {e}")
        print(f"Error occurred: {e}")
