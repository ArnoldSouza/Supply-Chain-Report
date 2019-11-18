#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 10 20:11:27 2018

@author: arnold
"""

from bokeh.models import (HoverTool,  # present details in the plot
                          ColumnDataSource,  # specify source
                          Title,  # add title and subtitles
                          Span,  # add horizontal line
                          Band,  # create a band inside the chart
                          FactorRange,  # create factors to colorize
                          LabelSet,  # used to compound label
                          BoxAnnotation,  # used in shadding
                          DatetimeTickFormatter)  # format datetime axis
from bokeh.palettes import Category20_20  # used in factor mapping
from bokeh.transform import factor_cmap  # used in factor mapping
from bokeh.core.properties import value  # used in labels
from bokeh.layouts import column
import pandas as pd  # manage dataframe
from bokeh.io import show, output_file, reset_output  # bokeh imports
from bokeh.plotting import figure  # bokeh imports
import numpy as np  # necessary to round up the results


def assembly_chart(df, complements):
    """function to assembly the chart"""
    print('starting the plot...')

    # specify the output file name
    output_file("movigrama_chart.html")
    # force to show only one plot when multiples executions of the code occur
    # otherwise the plots will append each time one new calling is done
    reset_output()

    # create ColumnDataSource objects directly from Pandas data frames
    source = ColumnDataSource(df)

    # use the column DT as index
    df.set_index('DT', inplace=True)

    ###########################################################################
    #
    #  Movigrama Plot
    #
    ###########################################################################

    # build figure of the plot
    p = figure(x_axis_type='datetime',
               x_axis_label='days of moviment',
               y_axis_label='unities movimented',
               plot_width=1230,
               plot_height=500,
               active_scroll='wheel_zoom')

    # TODO Specify X range (not all plots have 365 days of moviment)

    # build the Stock Level bar
    r1 = p.vbar(x='DT',
                bottom=0,
                top='STOCK',
                width=pd.Timedelta(days=1),
                fill_alpha=0.4,
                color='paleturquoise',
                source=source)

    # build the OUT bar
    p.vbar(x='DT',
           bottom=0,
           top='SOMA_SAI',
           width=pd.Timedelta(days=1),
           fill_alpha=0.8,
           color='crimson',
           source=source)

    # build the IN bar
    p.vbar(x='DT',
           bottom=0,
           top='SOMA_ENTRA',
           width=pd.Timedelta(days=1),
           fill_alpha=0.8,
           color='seagreen',
           source=source)

    # edit title
    # adds warehouse title
    p.add_layout(Title(text=complements['warehouse'],
                       text_font='helvetica',
                       text_font_size='10pt',
                       text_color='orangered',
                       text_alpha=0.5,
                       align='center',
                       text_font_style="italic"), 'above')
    # adds product title
    p.add_layout(Title(text=complements['product'],
                       text_font='helvetica',
                       text_font_size='10pt',
                       text_color='orangered',
                       text_alpha=0.5,
                       align='center',
                       text_font_style="italic"), 'above')
    # adds main title
    p.add_layout(Title(text='Movigrama Endicon',
                       text_font='helvetica',
                       text_font_size='16pt',
                       text_color='orangered',
                       text_alpha=0.9,
                       align='center',
                       text_font_style="bold"), 'above')

    # adds horizontal line
    hline = Span(location=0,
                 line_alpha=0.4,
                 dimension='width',
                 line_color='gray',
                 line_width=3)
    p.renderers.extend([hline])

    # adapt the range to the plot
    p.x_range.range_padding = 0.1
    p.y_range.range_padding = 0.1

    # format the plot's outline
    p.outline_line_width = 4
    p.outline_line_alpha = 0.1
    p.outline_line_color = 'orangered'

    # format major labels
    p.axis.major_label_text_color = 'gray'
    p.axis.major_label_text_font_style = 'bold'

    # format labels
    p.axis.axis_label_text_color = 'gray'
    p.axis.axis_label_text_font_style = 'bold'

#    p.xgrid.grid_line_color = None  # disable vertical bars
#    p.ygrid.grid_line_color = None  # disable horizontal bars

    # change placement of minor and major ticks in the plot
    p.axis.major_tick_out = 10
    p.axis.minor_tick_in = -3
    p.axis.minor_tick_out = 6
    p.axis.minor_tick_line_color = 'gray'

    # format properly the X datetime axis
    p.xaxis.formatter = DatetimeTickFormatter(
                days=['%d/%m'],
                months=['%m/%Y'],
                years=['%Y'])

    # iniciate hover object
    hover = HoverTool()
    hover.mode = "vline"  # activate hover by vertical line
    hover.tooltips = [("SUM-IN", "@SOMA_ENTRA"),
                      ("SUM-OUT", "@SOMA_SAI"),
                      ("COUNT-IN", "@TRANSACT_ENTRA"),
                      ("COUNT-OUT", "@TRANSACT_SAI"),
                      ("STOCK", "@STOCK"),
                      ("DT", "@DT{%d/%m/%Y}")]
    # use 'datetime' formatter for 'DT' field
    hover.formatters = {"DT": 'datetime'}
    hover.renderers = [r1]  # display tolltip only to one render
    p.add_tools(hover)

    ###########################################################################
    #
    #  Demand analysis
    #
    ###########################################################################

    # change to positive values
    df['out_invert'] = df['SOMA_SAI']*-1
    # moving average with n=30 days
    df['MA30'] = df['out_invert'].rolling(30).mean().round(0)
    # moving standard deviation with n=30 days
    df['MA30_std'] = df['out_invert'].rolling(30).std().round(0)
    # lower control limit for 1 sigma deviation
    df['lcl_1sigma'] = (df['MA30'] - df['MA30_std'])
    # upper control limit for 1 sigma deviation
    df['ucl_1sigma'] = (df['MA30'] + df['MA30_std'])

    source = ColumnDataSource(df)

    p1 = figure(plot_width=1230,
                plot_height=500,
                x_range=p.x_range,
                x_axis_type="datetime",
                active_scroll='wheel_zoom')

    # build the Sum_out bar
    r1 = p1.vbar(x='DT',
                 top='out_invert',
                 width=pd.Timedelta(days=1),
                 color='darkred',
                 line_color='salmon',
                 fill_alpha=0.4,
                 source=source)

    # build the moving average line
    p1.line(x='DT',
            y='MA30',
            source=source)

    # build the confidence interval
    band = Band(base='DT',
                lower='lcl_1sigma',
                upper='ucl_1sigma',
                source=source,
                level='underlay',
                fill_alpha=1.0,
                line_width=1,
                line_color='black')
    p1.renderers.extend([band])

    # adds title
    p1.add_layout(Title(text='Demand Variability',
                        text_font='helvetica',
                        text_font_size='16pt',
                        text_color='orangered',
                        text_alpha=0.5,
                        align='center',
                        text_font_style="bold"), 'above')

    # adds horizontal line
    hline = Span(location=0,
                 line_alpha=0.4,
                 dimension='width',
                 line_color='gray',
                 line_width=3)
    p1.renderers.extend([hline])

    # format the plot's outline
    p1.outline_line_width = 4
    p1.outline_line_alpha = 0.1
    p1.outline_line_color = 'orangered'

    # format major labels
    p1.axis.major_label_text_color = 'gray'
    p1.axis.major_label_text_font_style = 'bold'

    # format labels
    p1.axis.axis_label_text_color = 'gray'
    p1.axis.axis_label_text_font_style = 'bold'

    # change placement of minor and major ticks in the plot
    p1.axis.major_tick_out = 10
    p1.axis.minor_tick_in = -3
    p1.axis.minor_tick_out = 6
    p1.axis.minor_tick_line_color = 'gray'

    # format properly the X datetime axis
    p1.xaxis.formatter = DatetimeTickFormatter(days=['%d/%m'],
                                               months=['%m/%Y'],
                                               years=['%Y'])

    # iniciate hover object
    hover = HoverTool()
    hover.mode = "vline"  # activate hover by vertical line
    hover.tooltips = [("DEMAND", '@out_invert'),
                      ("UCL 1σ", "@ucl_1sigma"),
                      ("LCL 1σ", "@lcl_1sigma"),
                      ("M AVG 30d", "@MA30"),
                      ("DT", "@DT{%d/%m/%Y}")]
    # use 'datetime' formatter for 'DT' field
    hover.formatters = {"DT": 'datetime'}
    hover.renderers = [r1]  # display tolltip only to one render
    p1.add_tools(hover)

    ###########################################################################
    #
    #  Demand groupped by month
    #
    ###########################################################################

    resample_M = df.iloc[:, 0:6].resample('M').sum()  # resample to month
    # create column date as string
    resample_M['date'] = resample_M.index.strftime('%b/%y').values
    # moving average with n=3 months
    resample_M['MA3'] = resample_M['out_invert'].rolling(3).mean()

    resample_M['MA3'] = np.ceil(resample_M.MA3)  # round up the column MA3
    # resample to month with mean
    resample_M['mean'] = np.ceil(resample_M['out_invert'].mean())
    # resample to month with standard deviation
    resample_M['std'] = np.ceil(resample_M['out_invert'].std())
    # moving standard deviation with n=30 days
    resample_M['MA3_std'] = np.ceil(resample_M['out_invert'].rolling(3).std())
    # lower control limit for 1 sigma deviation
    resample_M['lcl_1sigma'] = resample_M['MA3'] - resample_M['MA3_std']
    # upper control limit for 1 sigma deviation
    resample_M['ucl_1sigma'] = resample_M['MA3'] + resample_M['MA3_std']

    source = ColumnDataSource(resample_M)

    p2 = figure(plot_width=1230,
                plot_height=500,
                x_range=FactorRange(factors=list(resample_M.date)),
                title='demand groupped by month')

    colors = factor_cmap('date',
                         palette=Category20_20,
                         factors=list(resample_M.date))

    p2.vbar(x='date',
            top='out_invert',
            width=0.8,
            fill_color=colors,
            fill_alpha=0.8,
            source=source,
            legend=value('OUT'))

    p2.line(x='date',
            y='MA3',
            color='red',
            line_width=3,
            line_dash='dotted',
            source=source,
            legend=value('MA3'))

    p2.line(x='date',
            y='mean',
            color='blue',
            line_width=3,
            line_dash='dotted',
            source=source,
            legend=value('mean'))

    band = Band(base='date',
                lower='lcl_1sigma',
                upper='ucl_1sigma',
                source=source,
                level='underlay',
                fill_alpha=1.0,
                line_width=1,
                line_color='black')

    labels1 = LabelSet(x='date',
                       y='MA3',
                       text='MA3',
                       level='glyph',
                       y_offset=5,
                       source=source,
                       render_mode='canvas',
                       text_font_size="8pt",
                       text_color='darkred')

    labels2 = LabelSet(x='date',
                       y='out_invert',
                       text='out_invert',
                       level='glyph',
                       y_offset=5,
                       source=source,
                       render_mode='canvas',
                       text_font_size="8pt",
                       text_color='gray')

    low_box = BoxAnnotation(top=resample_M['mean'].iloc[0]-resample_M['std'].iloc[0],  # analysis:ignore
                            fill_alpha=0.1,
                            fill_color='red')
    mid_box = BoxAnnotation(bottom=resample_M['mean'].iloc[0]-resample_M['std'].iloc[0],  # analysis:ignore
                            top=resample_M['mean'].iloc[0]+resample_M['std'].iloc[0],  # analysis:ignore
                            fill_alpha=0.1, fill_color='green')
    high_box = BoxAnnotation(bottom=resample_M['mean'].iloc[0]+resample_M['std'].iloc[0],  # analysis:ignore
                             fill_alpha=0.1,
                             fill_color='red')

    p2.renderers.extend([band, labels1, labels2, low_box, mid_box, high_box])
    p2.legend.click_policy = "hide"
    p2.legend.background_fill_alpha = 0.4

    p2.add_layout(Title(text='Demand Grouped by Month',
                        text_font='helvetica',
                        text_font_size='16pt',
                        text_color='orangered',
                        text_alpha=0.5,
                        align='center',
                        text_font_style="bold"), 'above')

    # adds horizontal line
    hline = Span(location=0,
                 line_alpha=0.4,
                 dimension='width',
                 line_color='gray',
                 line_width=3)
    p2.renderers.extend([hline])

    # format the plot's outline
    p2.outline_line_width = 4
    p2.outline_line_alpha = 0.1
    p2.outline_line_color = 'orangered'

    # format major labels
    p2.axis.major_label_text_color = 'gray'
    p2.axis.major_label_text_font_style = 'bold'

    # format labels
    p2.axis.axis_label_text_color = 'gray'
    p2.axis.axis_label_text_font_style = 'bold'

    # change placement of minor and major ticks in the plot
    p2.axis.major_tick_out = 10
    p2.axis.minor_tick_in = -3
    p2.axis.minor_tick_out = 6
    p2.axis.minor_tick_line_color = 'gray'

    # iniciate hover object
    # TODO develop hoverTool
#    hover = HoverTool()
#    hover.mode = "vline"  # activate hover by vertical line
#    hover.tooltips = [("SUM-IN", "@SOMA_ENTRA"),
#                      ("SUM-OUT", "@SOMA_SAI"),
#                      ("COUNT-IN", "@TRANSACT_ENTRA"),
#                      ("COUNT-OUT", "@TRANSACT_SAI"),
#                      ("STOCK", "@STOCK")]
#    hover.renderers = [r1]  # display tolltip only to one render
#    p2.add_tools(hover)

    ###########################################################################
    #
    #  Plot figures
    #
    ###########################################################################

    # put the results in a column and show
    show(column(p, p1, p2))

    # show(p)  # plot action

    print('plot finished')
