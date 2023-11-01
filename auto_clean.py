from AutoClean import AutoClean
import pandas as pd

df = pd.read_csv("processed/scraped.csv", index_col=0)
pipeline = AutoClean(df)

pipeline.output.to_csv("processed/autocleaned.csv")
