#%%
# Source: https://github.com/Refinitiv-API-Samples/Example.DataLibrary.Python/blob/main/Tutorials/2.Content/2.2-Pricing/TUT_2.2.01-Pricing-Snapshot.ipynb

import os
import refinitiv.data as rd
from pandas import DataFrame


#%%
# Awaiting credentials... code not tested yet...
os.environ["RD_LIB_CONFIG_PATH"] = "../../../Configuration"

# Open the Default Session
rd.open_session()



#%% 
# One method

# Define our RDP Snapshot Price object
response = rd.content.pricing.Definition(
    ['EUR=', 'GBP=', 'JPY=', 'CAD='],
    fields=['BID', 'ASK']
).get_data()

response.data.df



#%%
# Alternative method

# Define our Streaming Price object
non_streaming = rd.content.pricing.Definition(
    ['EUR=', 'GBP=', 'JPY=', 'CAD='],
    fields=['BID', 'ASK']
).get_stream()

# We want to just snap the current prices, don't need updates
# Open the instrument in non-streaming mode
non_streaming.open(with_updates=False)

# Snapshot the prices at the time of the open() call
non_streaming.get_snapshot()



#%%

rd.close_session()

# %%

