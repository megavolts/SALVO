    import os
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib import gridspec
    import numpy as np
    from magnaprobe_toolbox import analysis
    from magnaprobe_toolbox.io import upper_cal, lower_cal
    from cmcrameri import cm

    DATA_DIR = "/mnt/data/UAF-data/working_a/SALVO/"

    LOC = '_line'
    stats_site = {}
    all_site = {}
    for SITE in ['ARM', 'BEO', 'ICE']:
        fn_dict = {}
        for path, subdirs, files in os.walk(DATA_DIR):
            if SITE in path and 'magnaprobe' in path:
                date = path.split('/')[-2].split('-')[0]
                date = pd.to_datetime(date)
                for file in files:
                    if file.endswith('.csv') and  LOC in file and '.a' in file and not file.startswith('.~'):
                        version = int(file.split('.a')[1][:-4])
                        if date not in fn_dict.keys():
                            fn_dict[date] = [version, os.path.join(path, file)]
                        elif version > fn_dict[date][0]:
                            fn_dict[date] = [version, os.path.join(path, file)]
                if date in fn_dict:
                    print(date, fn_dict[date][0], fn_dict[date][-1].split('/')[-1])

        # Define figure subplots
        stats_df = pd.DataFrame()

        FIG_TITLE = SITE
        NCOLS = 1
        NROWS = 4

        colors = cm.davos(np.linspace(0, 1, len(fn_dict.keys())+1))
        colors = colors[::-1]
        colors[-2] = [0, 0, 0, 1]
        colort = colors.copy()
        for ii in range(len(colors)):
            colort[ii][3] = 0.25

        w_fig, h_fig = 8, 11
        fig = plt.figure(figsize=[w_fig, h_fig])
        gs1 = gridspec.GridSpec(NROWS, NCOLS, height_ratios=[1] * NROWS, width_ratios=[1]*NCOLS)
        ax = [[fig.add_subplot(gs1[0, 0])], [fig.add_subplot(gs1[1, 0])], [fig.add_subplot(gs1[2, 0])], [fig.add_subplot(gs1[3, 0])]]

        for ii, date in enumerate(sorted(fn_dict)):
            print(date, SITE)
            data_df = pd.read_csv(fn_dict[date][1])

            # Compute snow depth histogram for
            hs_min = 0
            hs_max = 1.2
            dhs = 0.05
            bins = np.arange(hs_min, hs_max + dhs / 2, dhs)
            hs_df = data_df.loc[data_df['SnowDepth'].notnull(), ['SnowDepth']]
            hs_hist = analysis.statistic.histogram(hs_df, bins)

            # Compute snow depth statistic
            hs_stats = analysis.statistic.basic(data_df['SnowDepth'].to_numpy())

            if stats_df.empty:
                stats_df = pd.DataFrame(hs_stats, index=[date])
            else:
                stats_df = pd.concat([stats_df, pd.DataFrame(hs_stats, index=[date])])

            from magnaprobe_toolbox.io.plot import stat_annotation
            statstr, statbox = stat_annotation(hs_stats)

            # Compute snow depth pdf
            hs_pdf_fit = analysis.statistic.pdf(hs_df)
            hs_x = np.arange(lower_cal, upper_cal, dhs / 10)

            AX_X, AX_Y = 0, 0
            ax[AX_X][AX_Y].plot(data_df.LineLocation, data_df.SnowDepth, color=colors[ii], label = date.dayofyear)
            ax[AX_X][AX_Y].set_xlabel('Distance along the transect (m)')
            ax[AX_X][AX_Y].set_ylabel('Snow Depth (m)')
            #ax[AX_X][AX_Y].set_ylim([-0.1, 1])
            AX_X, AX_Y = 1, 0
            x0 = data_df['Latitude']
            y0 = data_df['Longitude']
            snow_depth_scale = hs_df.max().values - hs_df.min().values
            hs0 = cm.davos(data_df.loc[data_df['SnowDepth'].notnull(), ['SnowDepth']]/snow_depth_scale[0])
            hs0 = hs0[::-1]
            #ax[AX_X][AX_Y].scatter(x0, y0, c=hs0)
            ax[AX_X][AX_Y].scatter(data_df.X, data_df.Y, color=colors[ii], label=date.dayofyear)
            ax[AX_X][AX_Y].legend(loc='upper right', ncol=6)

            AX_X, AX_Y = 2, 0
            ax[AX_X][AX_Y].bar(hs_hist.index, hs_hist['Count'], dhs, edgecolor=colors[ii], color=colort[ii])
            ax[AX_X][AX_Y].plot(hs_x, hs_pdf_fit.pdf(hs_x), color=colors[ii])
            ax[AX_X][AX_Y].set_ylabel('PDF')
            ax[AX_X][AX_Y].set_xlabel('Snow depth (m)')
            ax[AX_X][AX_Y].set_xlim([hs_hist.index.min(), hs_hist.index.max()])
            ax[AX_X][AX_Y].text(0.4++0.2*ii, 0.9, statstr, bbox=statbox, transform=ax[AX_X][AX_Y].transAxes,
                           fontsize=10, verticalalignment='top', color=colors[ii])

            if SITE not in all_site:
                all_site[SITE] = {date: data_df}
            else:
                all_site[SITE][date] = data_df

        AX_X, AX_Y = 3, 0
        ax[AX_X][AX_Y].set_ylabel('Mean snow depth (m)')
        ax[AX_X][AX_Y].set_xlabel('Time')
        ax[AX_X][AX_Y].plot(stats_df.index.dayofyear, stats_df['mean'], label='mean', marker='x', color='k')
        ax[AX_X][AX_Y].plot(stats_df.index.dayofyear, stats_df['mean'], label='mean', marker='o', color='k')
        ax[AX_X][AX_Y].plot(stats_df.index.dayofyear, stats_df['max'], label='max', marker='x', color='b')
        ax[AX_X][AX_Y].plot(stats_df.index.dayofyear, stats_df['min'], label='min', marker='x', color='r')

        y_plus = stats_df['mean'] + stats_df['std']
        y_minus = stats_df['mean'] - stats_df['std']
        ax[AX_X][AX_Y].fill_between(stats_df.index.dayofyear, y_minus, y_plus, color='k', alpha=0.25, label='$\pm$std')
        fig.suptitle(FIG_TITLE)
        plt.savefig(os.path.join('/mnt/data/UAF-data/working_a/SALVO/', SITE + '_' + LOC + '.pdf'))

        plt.show()

        stats_df.to_csv(os.path.join('/mnt/data/UAF-data/working_a/SALVO/', SITE + '_' + LOC + '.csv'))
        stats_site[SITE] = stats_df




    # Melt rate
    from datetime import date
    melt=pd.date_range('2024-05-26', date.today(), freq='D')

    date_bkp = stats_site.copy()

    for site in ['ARM', 'BEO', 'ICE']:
        stats_site[site] = stats_site[site].resample('D').interpolate()
        stats_site[site] = stats_site[site][(melt.min() < stats_site[site].index) &
                                            (stats_site[site].index <= melt.max())]

    FIG_TITLE = SITE
    NCOLS = 1
    NROWS = 1


    w_fig, h_fig = 8, 11
    fig = plt.figure(figsize=[w_fig, h_fig])
    gs1 = gridspec.GridSpec(NROWS, NCOLS, height_ratios=[1] * NROWS, width_ratios=[1]*NCOLS)
    ax = [[fig.add_subplot(gs1[0, 0])]]
    AX_X, AX_Y = 0, 0
    ax[AX_X][AX_Y].plot(stats_site['BEO'].index.dayofyear, stats_site['BEO']['mean'], label='BEO', color='k')
    ax[AX_X][AX_Y].plot(stats_site['ARM'].index.dayofyear, stats_site['ARM']['mean'], label='ARM', color='r')

    for site in ['ARM', 'BEO', 'ICE']:
        for date in date_bkp[site].index:
            ax[AX_X][AX_Y].plot(stats_site[site].loc[stats_site[site].index == date].index.dayofyear,
                                stats_site[site].loc[stats_site[site].index == date, 'mean'], marker='o',  color='k')

    y_plus = stats_site['BEO']['mean'] + stats_site['BEO']['std']
    y_minus = stats_site['BEO']['mean'] - stats_site['BEO']['std']
    ax[AX_X][AX_Y].fill_between(stats_site['BEO'].index.dayofyear, y_minus, y_plus, color='k', alpha=0.1, label='$\\pm$std')

    y_plus = stats_site['ARM']['mean'] + stats_site['ARM']['std']
    y_minus = stats_site['ARM']['mean'] - stats_site['ARM']['std']
    ax[AX_X][AX_Y].fill_between(stats_site['ARM'].index.dayofyear, y_minus, y_plus, color='r', alpha=0.1, )

    ax[AX_X][AX_Y].plot(stats_site['BEO'].index.dayofyear, stats_site['BEO']['min'], label='min', color='k', linestyle=':')
    ax[AX_X][AX_Y].plot(stats_site['ARM'].index.dayofyear, stats_site['ARM']['min'], color='r', linestyle=':')

    ax[AX_X][AX_Y].plot(stats_site['BEO'].index.dayofyear, stats_site['BEO']['max'], label='max', color='k', linestyle='--')
    ax[AX_X][AX_Y].plot(stats_site['ARM'].index.dayofyear, stats_site['ARM']['max'], color='r', linestyle='--')

    ax[AX_X][AX_Y].plot(stats_site['ICE'].index.dayofyear, stats_site['ICE']['mean'], label='ICE', color='b')
    y_plus = stats_site['ICE']['mean'] + stats_site['ICE']['std']
    y_minus = stats_site['ICE']['mean'] - stats_site['ICE']['std']
    ax[AX_X][AX_Y].fill_between(stats_site['ICE'].index.dayofyear, y_minus, y_plus, color='b', alpha=0.1, label='$\\pm$std')
    ax[AX_X][AX_Y].plot(stats_site['ICE'].index.dayofyear, stats_site['ICE']['min'], color='b', linestyle=':')
    ax[AX_X][AX_Y].plot(stats_site['ICE'].index.dayofyear, stats_site['ICE']['max'], color='b', linestyle='--')

    plt.legend()

    plt.savefig(os.path.join('/mnt/data/UAF-data/working_a/SALVO/', 'ARM_BEO.pdf'))
    plt.show()

    # Fraction threshold
    for SITE in ['ARM', 'BEO', 'ICE']:
        data = all_site[SITE]
        start_date = list(all_site[SITE].keys())[4]

        data[start_date]['SnowDepth'].max()
        hs_bin = np.linspace(0, 1, 21)
        hs_dict = {}
        for ii in data[start_date]['LineLocation']:
            for  hs_ii, hs in enumerate(hs_bin):
                print(hs)
                if data[start_date].iloc[ii]['SnowDepth'] < hs:
                    if hs not in hs_dict:
                        hs_dict[hs] = [ii]
                    else:
                        hs_dict[hs].append(ii)
                    break

        mean_ = {}
        for date in data.keys():
            mean_[date] = {}
            for hs in hs_dict:
                mean_[date][hs] = data[date].loc[hs_dict[hs], 'SnowDepth'].mean()



        _mean_df = pd.DataFrame(mean_).transpose()
        NCOLS = 1
        NROWS = 2
        w_fig, h_fig = 8, 11
        fig = plt.figure(figsize=[w_fig, h_fig])
        gs1 = gridspec.GridSpec(NROWS, NCOLS, height_ratios=[1] * NROWS, width_ratios=[1]*NCOLS)
        ax = [[fig.add_subplot(gs1[0, 0])], [fig.add_subplot(gs1[1, 0])], ]
        AX_X, AX_Y = 0, 0
        for col in _mean_df.columns:
            ax[AX_X][AX_Y].plot(_mean_df[col].index.dayofyear, _mean_df[col])

        ax[AX_X][AX_Y].set_xlim([149, 160])
        ax[AX_X][AX_Y].legend()

        AX_X, AX_Y = 1, 0
        for index in data[start_date].index:
            print(index)
            x = []
            y = []
            for date in data.keys():
                x.append(pd.to_datetime(date).dayofyear)
                y.append(data[date].iloc[index]['SnowDepth'])
            ax[AX_X][AX_Y].plot(x, y)

        ax[AX_X][AX_Y].set_xlim([149, 160])

        plt.savefig(os.path.join('/mnt/data/UAF-data/working_a/SALVO/', SITE +'-hs_category.pdf'))
        plt.show()
