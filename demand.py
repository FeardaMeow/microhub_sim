import pandas as pd
import numpy as np
from sklearn.neighbors import DistanceMetric

eastlake = pd.read_csv("/Users/seyma/Documents/GitHub/microhub_sim/input_data/eastlake.csv")
cap = pd.read_csv("/Users/seyma/Documents/GitHub/microhub_sim/input_data/cap.csv")

def demand(df):

    df['Building'] = np.where(df.PREUSE_DES.str.contains("Apartment|4-Plex"), "Apartment",
                                               np.where(df.PREUSE_DES.str.contains("Condo"), "Condo",
                                                           np.where(df.PREUSE_DES.str.contains("Duplex|Single|Townhouse|Triplex"), "ResidenceBuilding",
                                                           "other")))

    apt_0=df[df['Building']=="Apartment"].sample(frac=0.77, random_state=1)
    df = df.drop(apt_0.index)
    apt_0["DeliveryFreq"]=0
    apt_1=df[df['Building']=="Apartment"].sample(frac=0.20/0.23, random_state=1)
    df = df.drop(apt_1.index)
    apt_1["DeliveryFreq"]=1
    apt_2=df[df['Building']=="Apartment"].sample(frac=0.90, random_state=1)
    df = df.drop(apt_2.index)
    apt_2["DeliveryFreq"]=2
    apt_3=df[df['Building']=="Apartment"].sample(frac=1, random_state=1)
    apt_3["DeliveryFreq"]=3

    con_0=df[df['Building']=="Condo"].sample(frac=0.96, random_state=1)
    df = df.drop(con_0.index)
    con_0["DeliveryFreq"]=0
    con_1=df[df['Building']=="Condo"].sample(frac=0.03/0.04, random_state=1)
    df = df.drop(con_1.index)
    con_1["DeliveryFreq"]=1
    con_2=df[df['Building']=="Condo"].sample(frac=1, random_state=1)
    con_2["DeliveryFreq"]=2

    res_0=df[df['Building']=="ResidenceBuilding"].sample(frac=0.67, random_state=1)
    df = df.drop(res_0.index)
    res_0["DeliveryFreq"]=0
    res_1=df[df['Building']=="ResidenceBuilding"].sample(frac=0.28/0.33, random_state=1)
    df = df.drop(res_1.index)
    con_1["DeliveryFreq"]=1
    res_2=df[df['Building']=="ResidenceBuilding"].sample(frac=0.9, random_state=1)
    df = df.drop(res_2.index)
    con_2["DeliveryFreq"]=2
    res_3=df[df['Building']=="ResidenceBuilding"].sample(frac=1, random_state=1)
    res_3["DeliveryFreq"]=3

    #rbind data
    df = pd.concat([apt_0, apt_1, apt_2, apt_3, con_0, con_1, con_2, res_0, res_1, res_2, res_3])

    df = df.dropna(subset = ["DeliveryFreq"])

    #reshape data, replicate as much as delivery frequency
    df = pd.DataFrame(df.values.repeat(df.DeliveryFreq, axis=0), columns=df.columns)

    #convert lat, lon to radians
    df['LAT'] = np.radians(df['LAT'].astype(float))
    df['LON'] = np.radians(df['LON'].astype(float))

    #create a distance matrix
    dist = DistanceMetric.get_metric('manhattan')
    df[['LAT','LON']].to_numpy()

    dist_matrix=pd.DataFrame(dist.pairwise(df[['LAT','LON']].to_numpy())*3798) #convert to miles
    long_form = dist_matrix.unstack()
    # rename columns and turn into a dataframe
    long_form.index.rename(['Stop_A', 'Stop_B'], inplace=True)
    long_form = long_form.to_frame('miles_distance').reset_index()

    #randomly pick 1st location
    first_loc_idx = np.random.randint(low=0, high=len(dist_matrix), size=1)

    idx=first_loc_idx[0]
    locations=[]
    distances=[]
    locations.append(idx)
    distances.append(0) #distance from microhub

    for k in range(40):
        subset = long_form[long_form["Stop_A"] == idx]
        near = subset[~subset.Stop_B.isin(locations)]
        #near = subset[(subset.Stop_A != subset.Stop_B)] #kendisi olamaz
        near = near[near.miles_distance == near.miles_distance.min()]

        z = ([near["Stop_B"].values.tolist(), near["miles_distance"].tolist()])

        for i in range(len(z[0])):
            locations.append(z[0][i])
            if i==0:
                distances.append(z[1][i])
            else:
                distances.append(0)

        idx=z[0][i]


    locations=pd.DataFrame(locations)
    locations.columns=["Location_ID"]

    distances=pd.DataFrame(distances)
    distances.columns=["Distance(mi)"]

    loc = df[['LAT','LON']]
    locations = pd.concat([locations, distances], axis=1, sort=False)
    join = locations.join(loc, lsuffix='_caller', rsuffix='_other')
    return(join)

print(demand(eastlake))
demand(cap)









