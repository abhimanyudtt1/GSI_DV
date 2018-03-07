import pandas as pd
def comparator(df1,df2):

    diff = {
        1: [],
        2: [],
        3: []
    }
    df1 = pd.DataFrame(df1)
    df2 = pd.DataFrame(df2)

    bigDf = pd.concat([df1,df2],axis=0)
    bigDf = bigDf.reset_index(drop=True)
    df_gpby = bigDf.groupby(list(bigDf.columns))
    idx = [x[0] for x in df_gpby.groups.values() if len(x) == 1]
    bigDf = bigDf.reindex(idx)
    print bigDf