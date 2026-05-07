import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Read the csv files in the team_stats folder and append the data into a dataframe. Also read the playoff results in the playoff_results.csv file and include
# those numbers in the dataframe. Return the resulting dataframe.
def get_and_merge_input_data_and_results(start_year = 2005):   
    end_year = 2026
    dfs = []
    for year in range(start_year,end_year):
        if year != 2005:
            df = pd.read_csv("team_stats/team_stats_year=" + str(year) + ".csv", index_col=0) 
            df["season"] = year
            dfs.append(df)
    data = pd.concat(dfs)
    playoff_df = pd.read_csv("playoff_results.csv")
    data = data.reset_index().rename(columns={"index": "team"})
    data['result'] = 0
    for year in range(start_year, end_year - 1):
        if year != 2005:
            y = year - start_year
            if year > 2005:
                y -= 1
            for t in range(16):
                data.loc[t + 16*y, 'result'] = playoff_df.loc[y + start_year - 1980, 'Rank' + str(t)]
    return data

# Create a random forest model to predict the playoff results for the 16 teams in the playoffs. The model trains on data and results from 2005 to the year
# timesplit - 1 and then predicts the playoff results for the year timesplit by outputing a float between 1 and 4 for each time. The higher the output 
# number, the better the predicted playoff performance. The model returns the predicted results for the year as a list along with the true results derived
# directly from the data.
def timesplit_estimate(data, timesplit):
    X = data.drop(columns=["team", "season", "result", "ranking-2", "ranking-3", "ranking-4", "ranking-5", "ranking-6",
                          "ranking-7", "ranking-8", "ranking-9", "l10Wins", "l10Losses", "l10OTLosses", "otLosses"])
    y = data["result"]
    train_mask = data["season"] < timesplit
    test_mask = data["season"] >= timesplit
    X_train = X[train_mask]
    y_train = y[train_mask]
    X_test = X[test_mask]
    y_test = y[test_mask]
    model = RandomForestRegressor(n_estimators=200, max_depth=6, random_state=23)
    model.fit(X_train, y_train)
    y_pred_test = model.predict(X_test)
    return y_pred_test[:16], y_test[:16].to_list()

# This function takes a list of 16 numbers as inputs representing the strength of each team in the playoff. It returns a list of 4 3s, 4 2s, and 8 1s
# corresponding to the playoff results of each team given their playoff strength reported in the input list. 3 corresponds to a semifinalist or finalist
# 2 corresponds to a second round exit and 1 corresponds to a first round exit.
def recommendation(y):
    recommend = [0]*16
    first_round_winners = [0]*8
    for i in range(8):
        if y[i] > y[i+8]:
            recommend[i+8] = 1
            first_round_winners[i] = i
        else:
            recommend[i] = 1
            first_round_winners[i] = i+8
    for i in range(4):
        if y[first_round_winners[2*i]] > y[first_round_winners[2*i + 1]]:
            recommend[first_round_winners[2*i + 1]] = 2
        else:
            recommend[first_round_winners[2*i]] = 2
    for i, r in enumerate(recommend):
        if r == 0:
            recommend[i] = 3
    return recommend

# get_and_merge_input_data_and_results() reads the input data from the csv files in the team_stats folder from 2005 to 2025 and puts them all into a table. 
# Also in this table are the playoff results from the playoff_results.csv file.
# timesplit_estimate() looks at the data up to the timesplit date. The data pertaining to years before the timesplit date is used to train a random forest
# model. The data on the timesplit date is used to predict the playoff results for that year. y_pred are the model output numbers, the higher the number,
# the higher the expected playoff performance. The true playoff performances for the year are also returned in the y_test variable.
# recommendation() takes a list of numbers and assumes the higher numbers will beat the lower numbers in the playoffs. The function then returns a list with
# 4 3s, 4 2s and 8 1s corresponding to the playoff score given that list.
# rp is the predicted playoff scores based on the model predictions. rt are the true playoff scores that occurred in the given year. rn are the naive
# prediction playoff scores where players who finished higher in the standings are predicted to beat players who finished lower in the standings. rr is a
# random playoff prediction.
# The sum of the squares of the differences between the predicted playoff scores and the true playoff scores gives the errors which are returned.
def generate_model_predictions(start_year):
    perrors = []
    nerrors = []
    rerrors = []
    for timesplit in range(start_year, 2026):
        data = get_and_merge_input_data_and_results()
        y_pred, y_test = timesplit_estimate(data, timesplit)
        y_naive = [4,2,3,2,4,2,3,2,1,1,1,1,1,1,1,1]
        y_rand = np.random.randint(1, 101, size=16)
        rp = recommendation(y_pred)
        rt = recommendation(y_test)
        rn = recommendation(y_naive)
        rr = recommendation(y_rand)
        perrors.append(sum((np.array(rp) - np.array(rt))**2))
        nerrors.append(sum((np.array(rn) - np.array(rt))**2))
        rerrors.append(sum((np.array(rr) - np.array(rt))**2))
    return perrors, nerrors, rerrors

# Generate the pdf plots of the the model prediction errors relative to the naive prediction errors and random prediction errors. The model predicts the
# year y results based off the year y input data and the input data and results for years 2005 to y-1. The naive prediction says the position of a team
# in the standings dictates playoff performance and the random prediction is simply a random prediction of playoff performance.
def generate_performance_plots(perrors, nerrors, rerrors, start_year):
    plt.plot([x for x in range(start_year, 2026)], np.array(perrors) - np.array(nerrors), '.',
             [x for x in range(start_year, 2026)], [0 for x in range(start_year,2026)], 'orange',
             [x for x in range(start_year, 2026)], [8 for x in range(start_year,2026)], 'orange',
             [x for x in range(start_year, 2026)], [-8 for x in range(start_year,2026)], 'orange')
    plt.xlabel('Year')
    plt.ylabel('Prediction-Naive Estimate Score Difference')
    plt.savefig('prediction-naive_estimate_score_difference.pdf')
    plt.figure()
    plt.plot([x for x in range(start_year, 2026)], np.array(perrors) - np.array(rerrors), '.',
             [x for x in range(start_year, 2026)], [0 for x in range(start_year,2026)])
    plt.xlabel('Year')
    plt.ylabel('Prediction-Random Estimate Score Difference')
    plt.savefig('prediction-random_estimate_score_difference.pdf')

# generate_model_predictions constructs a random forest model to predict playoff performance in the years 2007 to 2025. The training data for the the year y
# prediction is the data available from 2005 until year y-1. The model then predicts how each team will do on a score of 1-3 with it predicting 4 3s,
# 4 2s and 8 1s. The sum of the squares of the differences between each team's predicted performance and true performance is saved in the perrors list.
# nerrors is the resulting error from the naive prediction based on how teams finished in the standings and rerrors are random errors resulting from a
# random guess of how the teams will perform.
# generate_performance_plots generates the pdfs available in the repo showing the model performance by plotting the differences in the error lists.
if __name__ == "__main__":
    start_year = 2007
    perrors, nerrors, rerrors = generate_model_predictions(start_year)
    generate_performance_plots(perrors, nerrors, rerrors, start_year)

















