import pandas as pd
import datetime as dt


# IF YOU WANT TO GET THE NEWEST DATA, EXECUTE THIS:

# filename = "ai_litigation/get_data.py"  

# with open(filename, "r") as file:
#     exec(file.read())

df = pd.read_csv("ai_litigation/data/litigation_ext.csv")

df['Date Action Filed'] = pd.to_datetime(df['Date Action Filed'], errors='coerce')
df['Year Filed'] = df['Date Action Filed'].dt.year


def num_cases(column):
        name = column.name
        counts = column.value_counts()
        freq = counts.reset_index()
        freq.columns = [name, "Frequency"]
        freq = freq.sort_values(by=name, ascending=True)
        freq = freq.reset_index(drop=True)
        return freq

# Make year frequency df
year_freq_df = num_cases(df['Year Filed'])
year_freq_df.columns = ["Year", "Frequency"]

year_freq_df.to_csv("ai_litigation/data/year_fr.csv", encoding='utf-8')

algorithm = df['Algorithm'].str.split(', ')
algorithm = algorithm.dropna()
algo_list = [keyword.strip() for sublist in algorithm for keyword in sublist]

algo_list = pd.Series(algo_list)

value_counts = algo_list.value_counts()
# Identify values that occur only once
single_occurrences = value_counts[value_counts == 1].index
# Replace these values with 'Other' in the original DataFrame
algo_list = algo_list.replace(single_occurrences, 'Other')

# Recalculate value counts
counts = algo_list.value_counts()
algo_freq = counts.reset_index()
algo_freq.columns = ["Algorithm", "Frequency"]
algo_freq = algo_freq.reset_index(drop=True)
algo_freq = algo_freq.sort_values(by='Frequency', ascending=False)

algo_freq.to_csv("ai_litigation/data/algo_fr.csv", encoding='utf-8')



df['Brief Description'] = df['Brief Description'].str.replace("Summary of Facts and Activity to Date", "Summary of Facts and Activity to Date: ")
df['Brief Description'] = df['Brief Description'].str.replace("Summary of Significance", "")
df.to_csv("ai_litigation/data/litigation_ext.csv", encoding="utf-8")
