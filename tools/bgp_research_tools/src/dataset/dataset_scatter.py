import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

def save_3d_scatter(filename_prefix, dataset, x_column, y_column, z_column):
    #Preparing 3D scatter plots
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    #Adding regular
    ax.scatter(dataset.select_where(x_column,'LABEL',0), dataset.select_where(y_column,'LABEL',0), dataset.select_where(z_column,'LABEL',0), marker='o', label='Class 0: Regular', s=10, facecolors='none', edgecolors='tab:blue')
    #Adding anomalous
    ax.scatter(dataset.select_where(x_column,'LABEL',1), dataset.select_where(y_column,'LABEL',1), dataset.select_where(z_column,'LABEL',1), marker='*', label='Class 1: Anomalous', s=10, facecolors='none', edgecolors='tab:orange')

    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_zlabel(z_column)
    # ax.set_xlabel("Number of duplicate announcements", fontsize=8)
    # ax.set_ylabel("Average AS-path length", fontsize=8)
    # ax.set_zlabel("Number of implicit withdraws", fontsize=8)
    
    # ax.view_init(elev, azim, roll)
    # initial values: 30, -60, 0
    # ax.view_init(15, 60, 0)
    
    #Legend
    ax.legend()
    # legend = ax.legend(*[scatter1.legend_elements()[0],['a','b','c','d','e']], 
    #                 title="Legend", loc='upper left')

    #Westrock values
    # ax.axes.set_xlim3d(-5, 15)
    # ax.axes.set_ylim3d(-5, 10)
    # ax.axes.set_zlim3d(-5, 20)
    # ax.set_xticks(range(-5, 20, 5))
    # ax.set_yticks(range(-5, 15, 5))
    # ax.set_zticks(range(-5, 25, 5))
    # ax.invert_xaxis()
    # ax.set_title("Westrock RIPE RRC14 MRTprocessor", fontsize=10)

    # plt.show()
    filename = f"{filename_prefix}_{x_column}_{y_column}_{z_column}.png"
    plt.savefig(filename)

def save_3d_datetime_scatter(filename_prefix, dataset, y_column, z_column):
    #Preparing 3D scatter plots
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    dates_regular = dataset.select_where('DATETIME','LABEL',0)
    dates_regular = [pd.to_datetime(d) for d in dates_regular]
    dates_regular = [d.timestamp() for d in dates_regular]

    dates_anomalous = dataset.select_where('DATETIME','LABEL',1)
    dates_anomalous = [pd.to_datetime(d) for d in dates_anomalous]
    dates_anomalous = [d.timestamp() for d in dates_anomalous]

    # Adding regular
    ax.scatter(dates_regular, dataset.select_where(y_column,'LABEL',0), dataset.select_where(z_column,'LABEL',0), marker='o', label='Class 0: Regular')
    # Adding anomalous
    ax.scatter(dates_anomalous, dataset.select_where(y_column,'LABEL',1), dataset.select_where(z_column,'LABEL',1), marker='+', label='Class 1: Anomalous')

    ax.set_xlabel('datetime')
    ax.set_ylabel(y_column)
    ax.set_zlabel(z_column)

    #Legend
    ax.legend()

    # plt.show()
    filename = f"{filename_prefix}_datetime_{y_column}_{z_column}.png"
    plt.savefig(filename)

def save_plotly_scatter(filename_prefix, dataset, x_column, y_column, z_column):
    fig = px.scatter_3d(dataset.df, x=x_column, y=y_column, z=z_column)
    filename = f"{filename_prefix}_{x_column}_{y_column}_{z_column}.png"
    fig.write_image(filename)
    # fig.show()

def motion_3d_scatter(filename_prefix, dataset, x_column, y_column, z_column):
    #Preparing 3D scatter plots
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    #Adding regular
    ax.scatter(dataset.select_where(x_column,'LABEL',0), dataset.select_where(y_column,'LABEL',0), dataset.select_where(z_column,'LABEL',0), marker='o', label='Class 0: Regular', s=10)
    #Adding anomalous
    ax.scatter(dataset.select_where(x_column,'LABEL',1), dataset.select_where(y_column,'LABEL',1), dataset.select_where(z_column,'LABEL',1), marker='*', label='Class 1: Anomalous', s=10)

    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    ax.set_zlabel(z_column)

    #Legend
    ax.legend()
    # legend = ax.legend(*[scatter1.legend_elements()[0],['a','b','c','d','e']], 
    #                 title="Legend", loc='upper left')

    # Rotate the axes and update
    # for angle in range(0, 360*4 + 1):
    for angle in range(0, 90*4 + 1):
        # Normalize the angle to the range [-180, 180] for display
        angle_norm = (angle + 180) % 360 - 180

        # Cycle through a full rotation of elevation, then azimuth, roll, and all
        elev = azim = roll = 0
        if angle <= 360:
            elev = angle_norm
        elif angle <= 360*2:
            azim = angle_norm
        elif angle <= 360*3:
            roll = angle_norm
        else:
            elev = azim = roll = angle_norm

        # Update the axis view and title
        ax.view_init(elev, azim, roll)
        plt.title('Elevation: %d°, Azimuth: %d°, Roll: %d°' % (elev, azim, roll))

        plt.draw()
        plt.pause(.001)