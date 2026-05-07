import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

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

def timesplit_estimate(data, timesplit):
    X = data.drop(columns=["team", "season", "result", "ranking-2", "ranking-3", "ranking-4", "ranking-5", "ranking-6",
                          "ranking-7", "ranking-8", "ranking-9", "l10Wins", "l10Losses", "l10OTLosses", "otLosses"])
    y = data["result"]
    # Time-based split
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

def generate_model_predictions(statr_year):
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

if __name__ == "__main__":
    start_year = 2007
    perrors, nerrors, rerrors = generate_model_predictions(start_year)
    generate_performance_plots(perrors, nerrors, rerrors, start_year)

















