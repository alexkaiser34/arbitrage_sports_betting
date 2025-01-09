# import requests


# # An api key is emailed to you when you sign up to a plan
# # Get a free API key at https://api.the-odds-api.com/
# API_KEY = '414053fc79db1a33165e95d3ec2c89ce'

# SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

# REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

# MARKETS = 'h2h,spreads' # h2h | spreads | totals. Multiple can be specified if comma delimited

# ODDS_FORMAT = 'american' # decimal | american

# DATE_FORMAT = 'iso' # iso | unix

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# # #
# # # First get a list of in-season sports
# # #   The sport 'key' from the response can be used to get odds in the next request
# # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# # sports_response = requests.get(
# #     'https://api.the-odds-api.com/v4/sports', 
# #     params={
# #         'api_key': API_KEY
# #     }
# # )


# # if sports_response.status_code != 200:
# #     print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

# # else:
# #     print('List of in season sports:', sports_response.json())



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# #
# # Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# # This will deduct from the usage quota
# # The usage quota cost = [number of markets specified] x [number of regions specified]
# # For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
# #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# # odds_response = requests.get(
# #     f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
# #     params={
# #         'api_key': API_KEY,
# #         'regions': REGIONS,
# #         'markets': MARKETS,
# #         'oddsFormat': ODDS_FORMAT,
# #         'dateFormat': DATE_FORMAT,
# #     }
# # )

# # eventId = "03dd880f071a65053e37000d3d826e14"
# # sport = "americanfootball_nfl"
# # markets = 'player_assists,player_defensive_interceptions,player_field_goals,player_kicking_points,player_pass_attempts,player_pass_completions,player_pass_interceptions,player_pass_longest_completion,player_pass_rush_reception_tds,player_pass_rush_reception_yds,player_pass_tds,player_pass_yds,player_pass_yds_q1,player_pats,player_receptions,player_reception_longest,player_reception_tds,player_reception_yds,player_rush_attempts,player_rush_longest,player_rush_reception_tds,player_rush_reception_yds,player_rush_tds,player_rush_yds,player_sacks,player_solo_tackles,player_tackles_assists,player_tds_over,player_1st_td,player_anytime_td,player_last_td,player_assists_alternate,player_field_goals_alternate,player_kicking_points_alternate,player_pass_attempts_alternate,player_pass_completions_alternate,player_pass_interceptions_alternate,player_pass_longest_completion_alternate,player_pass_rush_reception_tds_alternate,player_pass_rush_reception_yds_alternate,player_pass_tds_alternate,player_pass_yds_alternate,player_pats_alternate,player_receptions_alternate,player_reception_longest_alternate,player_reception_tds_alternate,player_reception_yds_alternate,player_rush_attempts_alternate,player_rush_longest_alternate,player_rush_reception_tds_alternate,player_rush_reception_yds_alternate,player_rush_tds_alternate,player_rush_yds_alternate,player_sacks_alternate,player_solo_tackles_alternate,player_tackles_assists_alternate'

# sport = "basketball_nba"
# eventId= "e49c35167662c7e6ea6970b981b018f8"
# markets = 'player_points,player_points_q1,player_rebounds,player_rebounds_q1,player_assists,player_assists_q1,player_threes,player_blocks,player_steals,player_blocks_steals,player_turnovers,player_points_rebounds_assists,player_points_rebounds,player_points_assists,player_rebounds_assists,player_field_goals,player_frees_made,player_frees_attempts,player_first_basket,player_double_double,player_triple_double,player_method_of_first_basket,player_points_alternate,player_rebounds_alternate,player_assists_alternate,player_blocks_alternate,player_steals_alternate,player_threes_alternate,player_points_assists_alternate,player_points_rebounds_alternate,player_rebounds_assists_alternate,player_points_rebounds_assists_alternate'

# # odds_response= requests.get(
# #     'https://api.the-odds-api.com/v4/sports/' + sport + '/events',
# #     params={
# #         'api_key': API_KEY
# #     }
# # )
# #
# odds_response= requests.get(
#     'https://api.the-odds-api.com/v4/sports/' + sport + '/events/'  + eventId + '/odds',
#     params={
#         'api_key': API_KEY,
#         'regions': REGIONS,
#         'markets': markets,
#         'oddsFormat': ODDS_FORMAT
#     }
# )



# if odds_response.status_code != 200:
#     print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

# else:
#     odds_json = odds_response.json()
#     print(odds_json)

from odds_api import OddsAPI


o = OddsAPI('americanfootball_nfl')
o.getUpcomingGames()

