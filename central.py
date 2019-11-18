# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 2019

@author: Arnold
"""

# declarations to import modules to the script
import pic  # import plot module
import funcs as fc  # import functions module
import time  # manage elapsed time
import pickle  # used to save objects

while True:
    print('●'*79)  # line delimiter
    print('Stock Movement analysis - Movigrama')
    print('●'*79)  # line delimiter

    # put values into variables of the SQL query
    # TODO uncomment in future
    parameters = fc.get_params('filial', 'armazem', 'codigo', 'intervalo')

    # get inicial time
    start_time = time.time()
    print('starting aplication at: {}h local'
          .format(time.strftime("%H:%M:%S", time.localtime(start_time))),
          end='\n'*2)

    # Open and read the file as a single buffer
    sqlFile = fc.read_sql_file('DATAFRAME')

    sqlFile = sqlFile.format(**parameters)

    # open database connection
    conn = fc.connect('app_config.ini', 'ERP_SERVER')

    # query the database server
    df = fc.fetch_data(sqlFile, conn, action=False)  # TODO remember change action # analysis:ignore

    # get complements of information to build the chart
    complements = fc.get_complements(conn,
                                     parameters,
                                     'product',
                                     'warehouse',
                                     'last_stock')

    # close the database connection
    conn.close()

    # add the recalculation of Stock Level Column
    df = fc.cumulative_inverse_sum(df, complements['last_stock'])

    # save the dataframe into pickle file
    df.to_pickle('dados.pkl')
    pickle.dump(complements, open("complements.pkl", "wb"))

    # function to plot the graph
    pic.assembly_chart(df, complements)

    # end of application
    elapsed_time = time.time() - start_time
    print('\n', 'application finished (hh:mm:ss): {}'
          .format(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))), sep='', end='\n'+'-'*79+'\n'*2)  # analysis:ignore
