ea = eastlake.sample(frac=.8, replace = False)

#microhub location = (47.63880, -122.3256)

first_loc = eastlake.sample(1)
print(first_loc)

from shapely.geometry import Point

def distance(shape1, shape2): #x,y x,y
    p1 = Point(shape1)
    p2 = Point(shape2)
    dist = p1.distance(p2)
    return dist * 69.05422334

for index, row in df.iterrows():
    df.distance[index, 'dist_1'] =  Dist(row['lat'], row['lon'], row['lat1'], row['lon1'])

eastlake['dist'] = distance([first_loc["LAT"],first_loc["LON"]], [eastlake['LAT'], eastlake['LON']])


s.apply(distance)

df['Building'] = 'ResidenceBuilding'
    df['Building'][(df['PREUSE_DESC'] in "Apartment" ) or (df['PREUSE_DESC'] in "4-Plex")] = 'ResidenceBuilding'
    df['Building'][df['PREUSE_DESC'] in "Condo" ] = 'Condo'
    df['Building'][(df['PREUSE_DESC'] in "Duplex" ) or (df['PREUSE_DESC'] in "4-Plex")] = 'ResidenceBuilding'


    df['Building'][df['PREUSE_DESC'] in "Apartment"] = 'LowRise'
    df['Building'][df['KCA_ZONING'] in "NC"] = 'NeighborhoodCommercial'
    df['Building'][df['KCA_ZONING'] in "P"] = 'PedestrianDesignated'

    df['weight'] = 'LowRise'
    df['Building'][df['KCA_ZONING'] in "LR"] = 'LowRise'
    df['Building'][(df['KCA_ZONING'] in "SF" ) or (df['KCA_ZONING'] in "RS")] = 'SingleFamily'
    df['Building'][df['KCA_ZONING'] in "NC"] = 'NeighborhoodCommercial'
    df['Building'][df['KCA_ZONING'] in "P"] = 'PedestrianDesignated'




sampledf = df.sample(weights = df.freq)


eastlake['LAT'] = np.radians(eastlake['LAT'])
eastlake['LON'] = np.radians(eastlake['LON'])

#create a distance matrix
dist = DistanceMetric.get_metric('manhattan')
eastlake[['LAT','LON']].to_numpy()
ea=pd.DataFrame(dist.pairwise(eastlake [['LAT','LON']].to_numpy())*3798) #convert to miles
#print(ea)
demand = ea.sample(frac=0.5, replace = False)
first_loc = np.random.randint(low=0, high=675, size=1)
print(ea[first_loc])

#pd.DataFrame(dist.pairwise(eastlake [['LAT','LON']].to_numpy())*3798,  columns=eastlake.PIN.unique(), index=eastlake.PIN.unique())

df['weight'] = np.where(df.Building.str.contains("Apartment"), ,
                                           np.where(df.PREUSE_DES.str.contains("Condo"), "Condo",
                                                       np.where(df.PREUSE_DES.str.contains("Duplex|Single|Townhouse|Triplex"), "ResidenceBuilding",
                                                       "other")))



temp=pd.DataFrame(dist_matrix.drop(first_loc_idx)) #drop rows

d=len(dist_matrix)
a=[]
idx=first_loc_idx
print(temp[idx])
print(temp[idx].min().index)

#for i in range(d):
idx_min = temp[idx].min().index.values

a.append(idx_min)
#print(temp)
#print(idx_min, idx)
#temp = temp.drop(idx_min, axis=0)
#print(len(temp))

    #dist_matrix = dist_matrix.drop(idx_min)
#print(type(first_loc_idx), type(idx), type(idx_min))




#distance = pd.DataFrame(dist_matrix[first_loc_idx])

#add distance from 1st loc. to df
#df = df.join(distance, lsuffix='_caller', rsuffix='_other')
#print(dist_matrix)



#dist_matrix.sort_values(by=["first_loc_idx"], inplace=True)


#join = gpd.sjoin(parcels, kc, op='intersects', how='left')

#df["distance"]
#print(first_loc_idx)

num_rows=sqrt(neighborhood_size)
num_cols=num_rows

SYMBOL = '.'
grid = []

for x in range(num_rows):
    grid.append([])
    for y in range(num_cols):
        grid[x].append(SYMBOL)
