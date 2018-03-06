import pandas as pd
def comparator(df1,df2):

    diff = {
        1: [],
        2: [],
        3: []
    }
    try :
        df1 = df1.reset_index().T.to_dict().values()
    except AttributeError :
        pass
    try :
        df2 = df2.reset_index().T.to_dict().values()
        #print "DF2:",df2
    except AttributeError:
        pass
    for i in df1 :
        if i not in df2:
            diff[2].append(i)
        if i in df2 :
            diff[1].append(i)

    for i in df2 :
        if i not in df1 :
            diff[3].append(i)
    return diff
