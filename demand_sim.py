'''
TODO: Generate a fixed neighborhood depending on building distribution and rules. Represent neighborhood with a matrix
TODO: Generate sample path (Reflective Brownian Motion) and number of packages to each location (Poisson)
TODO: Return two list [location] and [building]
'''

from math import sqrt
from scipy.stats import norm
import numpy as np
from pylab import plot, show, grid, axis, xlabel, ylabel, title
import pandas as pd
import building_objects

import simpy

def brownian(x0, n, dt, delta = 0.25, out=None):
    """
    Generate an instance of Brownian motion (i.e. the Wiener process):

        X(t) = X(0) + N(0, delta**2 * t; 0, t)

    where N(a,b; t0, t1) is a normally distributed random variable with mean a and
    variance b.  The parameters t0 and t1 make explicit the statistical
    independence of N on different time intervals; that is, if [t0, t1) and
    [t2, t3) are disjoint intervals, then N(a, b; t0, t1) and N(a, b; t2, t3)
    are independent.

    Written as an iteration scheme,

        X(t + dt) = X(t) + N(0, delta**2 * dt; t, t+dt)


    If `x0` is an array (or array-like), each value in `x0` is treated as
    an initial condition, and the value returned is a numpy array with one
    more dimension than `x0`.

    Arguments
    ---------
    x0 : float or numpy array (or something that can be converted to a numpy array
         using numpy.asarray(x0)).
        The initial condition(s) (i.e. position(s)) of the Brownian motion.
    n : int
        The number of steps to take.
    dt : float
        The time step.
    delta : float
        delta determines the "speed" of the Brownian motion.  The random variable
        of the position at time t, X(t), has a normal distribution whose mean is
        the position at time t=0 and whose variance is delta**2*t.
    out : numpy array or None
        If `out` is not None, it specifies the array in which to put the
        result.  If `out` is None, a new numpy array is created and returned.

    Returns
    -------
    A numpy array of floats with shape `x0.shape + (n,)`.

    Note that the initial value `x0` is not included in the returned array.
    """

    x0 = np.asarray(x0)

    # For each element of x0, generate a sample of n numbers from a
    # normal distribution.
    r = norm.rvs(size=x0.shape + (n,), scale=delta * sqrt(dt))

    # If `out` was not given, create an output array.
    if out is None:
        out = np.empty(r.shape)

    # This computes the Brownian motion by forming the cumulative sum of
    # the random samples.
    np.cumsum(r, axis=-1, out=out)

    # Add the initial condition.
    out += np.expand_dims(x0, axis=-1)

    return out

def route_plot(x_coord,y_coord):
    x = []
    x.append(x_coord)
    x.append(y_coord)
    x = np.array(x)

    #x=brownian(x[:,0], N, dt, delta, out=x[:,1:])
    # Plot the 2D trajectory.
    # Plot the 2D trajectory.
    plot(x[0], x[1])

    # Mark the start and end points.
    plot(x[0, 0], x[1, 0], 'go')
    plot(x[0, -1], x[1, -1], 'ro')

    # More plot decorations.
    title('2D Brownian Motion')
    xlabel('x', fontsize=16)
    ylabel('y', fontsize=16)
    axis('equal')
    grid(True)
    show()

def demand(env, num_stops=500, step_size= 1/20, apt=0.4, condo=0.3):
    '''

    Units in miles
    A neighborhood is appr. 1 mi^2
    num_stops = Number of package deliveries
    apt = percentage of apartment buildings over all stops (N)
    condo = percentage of condo complexes over all stops (N)
    step_size= there are 20 blocks per mile; step size = 1 block

    '''

    # The Wiener process parameter.
    delta = 0.25
    # Number of steps.
    N = num_stops
    # Time step size: 20 city blocks in a mile
    dt = step_size
    # Initial values of x:  x0=microhub location starts from x,y = (0,0)
    x = np.empty((2, N + 1))
    x[:, 0] = 0.0

    brownian(x[:,0], N, dt, delta, out=x[:,1:])

    #change to dataframe
    x_coord=x[0]
    y_coord=x[1]
    data_tuples = list(zip(x_coord,y_coord))
    route=pd.DataFrame(data_tuples, columns=['X_coord','Y_coord'])

    idx = pd.DataFrame(np.arange(len(x[0])), columns=["Visit_order"])

    #assign building types according to given percentages
    apt_df=idx.sample(frac=apt)
    idx = idx.drop(apt_df.index)
    apt_df["Building"]="Apartment"
    condo_df=idx.sample(frac=(condo/(1-apt)))
    idx = idx.drop(condo_df.index)
    condo_df["Building"]="Condo"
    res_df=idx.sample(frac=1)
    idx = idx.drop(res_df.index)
    res_df["Building"]="Res"

    df = pd.concat([apt_df, condo_df, res_df])
    df = df.sort_values(by=['Visit_order'])

    route = route.join(df, lsuffix='_caller', rsuffix='_other')

    building = []
    i=0
    for value in route["Building"]:
        if value == "Apartment":
            building.append(building_objects.Apartment(deliver=norm, deliver_params=[180, 1], env=env, num_residents=1,
                                                ))
        elif value == "Condo":
            building.append(
                building_objects.Condo(num_houses=1, deliver=norm, deliver_params=[120, 1], env=env, num_residents=1,
                                       ))
        elif value == "ResidenceBuilding":
            building.append(
                building_objects.ResidenceBuilding(deliver=norm, deliver_params=[60, 1], env=env, num_residents=1,
                                                   ))
        i+=1

    return route, building

def main():
    env = simpy.Environment()
    route, building = demand(env=env, num_stops=500, step_size=1 / 20, apt=0.4, condo=0.3)
    route_plot(route["X_coord"], route["Y_coord"])
    print(route,building)

if __name__ == 'main':
	main()
