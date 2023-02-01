#!/usr/bin/python3

# SPDX-FileCopyrightText: © 2023 Tom Kunze <mail@tomabrafix.de>
# SPDX-License-Identifier: MIT

import sys
import pandas as pd
import matplotlib.pyplot as plt

from config import *


# Column names in csv file
col_dnload = 'download_bandwidth_value'
col_upload = 'upload_bandwidth_value'
col_type = 'type'

type_ipv4 = 'IP-ETH-IPV4'
type_ipv6 = 'IP-ETH-IPV6'


def ax_plot(ax, data, plot, down=True, ipv4=True):
    # Data
    d = data[col_dnload]
    u = data[col_upload]
    rd = data['rolling_' + col_dnload]
    ru = data['rolling_' + col_upload]
    t4 = data[col_type] == type_ipv4
    t6 = data[col_type] == type_ipv6

    t = t4 if ipv4 else t6
    x = data.index[t]
    y = d[t] if down else u[t]
    ry = rd[t] if down else ru[t]

    cmin = DN_MIN if down else UP_MIN
    cnrm = DN_NRM if down else UP_NRM
    cmax = DN_MAX if down else UP_MAX

    if plot == 'boxplot':
        # Boxplots
        ax.boxplot(y, labels=[''])
    elif plot == 'hist':
        # Histogram
        ax.hist(y, 100, orientation='horizontal')
    elif plot == 'timeline':
        # Plot data
        ax.fill_between(x, 0, y, alpha=0.5)

        # Plot mean
        ax.plot(x, ry)

        # Min and normal bandwidth according to contract
        ax.plot(x, y*0+cmin, ls='--')
        ax.plot(x, y*0+cnrm, ls='--')
        ax.plot(x, y*0+cmax, ls='--')

    # Labels
    if down:
        if ipv4:
            ax.set_title('IPv4')
        else:
            ax.set_title('IPv6')
        ax.set(ylabel='Bandbreite Download [mbit/s]')
    else:
        ax.set(ylabel='Bandbreite Upload [mbit/s]')

    # y axis starts at 0
    ax.set_ylim(0)

    # Rotate xlabels
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

    # Hide x labels and tick labels for top plots and y ticks for right plots.
    ax.label_outer()


def main():
    if len(sys.argv) <= 1:
        print(f'Usage: {sys.argv[0]} <csv-file>', file=sys.stderr)
        sys.exit(1)

    # Parse data
    data = pd.read_csv(sys.argv[1], index_col=0, parse_dates=True)

    # Convert bandwidth to mbit/s
    data[col_dnload] = data[col_dnload] * 8 / 1000 / 1000
    data[col_upload] = data[col_upload] * 8 / 1000 / 1000

    # Calculate 24h moving average
    data['rolling_' + col_dnload] = data[col_dnload].rolling(24).mean()
    data['rolling_' + col_upload] = data[col_upload].rolling(24).mean()

    for plot in ['timeline', 'boxplot', 'hist']:
        fig = plt.figure()

        gs = fig.add_gridspec(2, 2, hspace=0, wspace=0)
        axs = gs.subplots(sharex=True, sharey='row')

        ax_plot(axs[0, 0], data, plot, True, True)
        ax_plot(axs[0, 1], data, plot, True, False)
        ax_plot(axs[1, 0], data, plot, False, True)
        ax_plot(axs[1, 1], data, plot, False, False)

        plt.show()


if __name__ == '__main__':
    main()
