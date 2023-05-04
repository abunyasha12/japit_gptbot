import pandas

df = pandas.read_csv("ru_RU.csv")

inp = input("Перевести: ")
idx = df[df["original"] == inp].index[0]
print(df.at[idx, "ru_RU"])
