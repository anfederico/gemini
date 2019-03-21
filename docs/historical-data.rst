.. _historical-data-page:

.. image:: ../media/logo.png
  :width: 100
  :align: center

Historical Data
===============

.. toctree::
   :maxdepth: 3
   :caption: Contents:

.. code-block:: text

     4195.81 ┤                                                                                         
     4161.76 ┤                                   ╭─╮                                                   
     4127.72 ┤                                   │ ╰╮                                                  
     4093.67 ┤                                   │  │                                                  
     4059.62 ┤                ╭╮                 │  ╰╮                                                 
     4025.58 ┤              ╭─╯╰╮╭╮              │   ╰─╮                                               
     3991.53 ┤             ╭╯   ╰╯│        ╭╮╭╮  │     │                                               
     3957.48 ┤             │      ╰╮      ╭╯╰╯│╭╮│     │                                               
     3923.44 ┤             │       │      │   ╰╯╰╯     │                                               
     3889.39 ┤             │       │   ╭╮╭╯            │                     ╭───╮                     
     3855.34 ┤             │       │  ╭╯││             │                     │   ╰─╮                   
     3821.30 ┤       ╭╮    │       ╰──╯ ╰╯             │     ╭╮   ╭╮        ╭╯     ╰╮  ╭╮ ╭╮          ╭
     3787.25 ┤       ││    │                           │╭╮  ╭╯╰╮ ╭╯│        │       │  │╰─╯╰─╮        │
     3753.21 ┤     ╭╮│╰─╮  │                           ││╰╮╭╯  ╰╮│ │╭──╮    │       │ ╭╯     ╰─╮      │
     3719.16 ┤     │╰╯  │╭─╯                           ╰╯ ╰╯    ╰╯ ╰╯  │    │       ╰─╯        │  ╭─╮╭╯
     3685.11 ┤    ╭╯    ╰╯                                             │    │                  ╰──╯ ╰╯ 
     3651.07 ┤    │                                                    │   ╭╯                          
     3617.02 ┤    │                                                    ╰╮╭─╯                           
     3582.97 ┤    │                                                     ╰╯                             
     3548.93 ┤╮  ╭╯                                                                                    
     3514.88 ┼╰╮╭╯                                                                                     
     3480.83 ┤ ╰╯ 

Importing Data
--------------
If you have your own data that has/hasn't been processed, you should conform to the following structure. Basically, load your data into a Pandas dataframe object and be sure to convert the dates to datetime format and include the following lowercase column titles.

.. code-block:: text

                      date         high          low         open        close
    0  2017-07-08 11:00:00  2480.186778  2468.319314  2477.279567  2471.314030  
    1  2017-07-08 11:30:00  2471.314030  2455.014057  2471.202796  2458.073602
    2  2017-07-08 12:00:00  2480.000000  2456.000000  2458.073602  2480.000000 
    3  2017-07-08 12:30:00  2489.004639  2476.334333  2479.402768  2481.481258
    4  2017-07-08 13:00:00  2499.000000  2476.621873  2481.458643  2491.990000 
    5  2017-07-08 13:30:00  2503.503479  2490.314610  2492.440289  2496.005562
    6  2017-07-08 14:00:00  2525.000000  2491.062741  2494.449524  2520.775500
    7  2017-07-08 14:30:00  2521.500036  2510.000000  2520.775500  2518.450645
    8  2017-07-08 15:00:00  2519.817394  2506.054360  2518.451000  2514.484009

Downloading Data
----------------
If you don't have your own data, we've included useful functions for grabbing low and high timeframe historical data from crypto exchanges. These helper functions will automatically resample your datasets to any desired timeframe and return a Gemini-compatible dataframe.

.. code-block:: python

    import data

    # Higher timeframes (>= daily)
    df = data.get_htf_candles("BTC_USD", "Bitfinex", "3-DAY", "2019-01-12 00:00:00", "2019-02-01 00:00:00")

    # Lower timeframes (< daily)
    df = data.get_ltf_candles("USDC_BTC", "30-MIN", "2019-01-12 00:00:00", "2019-02-01 00:00:00")
