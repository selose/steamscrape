# %% [markdown]
# After Generating the data, we now clean it
# 
# First start by loading the dataframe

# %%
import pandas as pd
import numpy as np

# %%
steam_df = pd.read_csv('steam_hardware_data_v5_UNCLEAN.csv')

# %%
unique_titles = steam_df['Title'].unique()

print(len(sorted(unique_titles)))

# %%
steam_df

# %%
# Drop 2nd column as it's a duplicate of the first
column_name = steam_df.columns[0]
print(column_name)

# Drop first column, 'Unnamed: 0'
steam_df = steam_df.drop(columns = column_name)
steam_df


# %% [markdown]
# Then, we remove the 'Best Rating', 'Worst Rating' column. These are features that aren't useful due to the fact that every game has 10 and 1 (respectively) for those features (we hoped that this wasn't the case and could provide more granular data)

# %%
print(steam_df['Best Rating'].unique())

# %%
print(steam_df['Worst Rating'].unique())

# %%
# Drop the 'Best Rating' and 'Worst Rating Columns
steam_df = steam_df.drop(columns = 'Best Rating')
steam_df = steam_df.drop(columns = 'Worst Rating')

# %%
steam_df

# %% [markdown]
# After droping those two columns, we're left with the glaring fact that the features regarding Hardware, for a particular game, will either consist of 1's
# 
# $$ [\text{ Graphics }, \text{ Memory}, \text{ OS}, \text{ Processor}, \text{ Storage}] = [1,1,1,1,1]$$
# 
# or actually consist of legible hardware data ( for example, `Maneater` has the following) :
# 
# $$ [\text{ Graphics }, \text{ Memory}, \text{ OS}, \text{ Processor}, \text{ Storage}] = [\text{ Intel HD 5500 }, \text{ 8 GB RAM}, \text{ Windows 10}, \text{ ProIntel Core i5-5300ucessor}, \text{ 20 GB available space} ]$$
# 
# But the rest of the data (User tags, Rating, Publisher, Review count, etc) is far more intact.
# 
# Thus, we can remove (or keep) the hardware columns depending on if we're going to work on them.
# 
# So at the end, we make csv files of both versions.
# 
# ______________________
# 
# 
# We clean the columns. Starting with price, we see that

# %%
unique_prices = steam_df['Original Price'].unique()

# ['$0.99', '$10.49', '$11.99', '$12.99', '$14.98', '$14.99', '$15.99', '$19.99', '$24.99', '$29.99', '$39.99', '$4.99', '$44.99', '$49.99', '$59.99', '$7.99', '$9.99', 'Free To Play', 'Free demo', 'Free to Play']
print(sorted(unique_prices))

# %% [markdown]
# Now, we strip all the values that reside in the column in the following way:
# 
# * If the game has:
#   * `Free demo`, `Free To Play`, or other  set the price 0
#   * Values like `'Unspottable Demo', 'Venge Demo', 'Worbital: Online Demo', 'Wunderling Demo'`, also get converted to 0
#   * Otherwise, just strip the price from their $ symbol

# %%
# Given a string of form $12.34, returns the dollar amount without the sign as '12.34' in USD
def strip_dollar(dollar):
  if '$' in dollar: 
    # print(dollar)
    stripped = dollar.split('$')
    return stripped[1]
  else: # If the inputted value was a Free To Play/ Free Demo game and dollar was instantiated as 0 (instead of a value w/ a $ in it)
    # print('0000')
    return '0'

#Test
print(strip_dollar('$10.99'))
print(strip_dollar('Unholy Heights Trial Version'))
print(strip_dollar('🐛  PLAY NOW'))

# %%
steam_df['Original Price'] = ['0' if x == 'Free demo' or x == 'Free To Play' else strip_dollar(x) for x in steam_df['Original Price']]


# %%
steam_df

# %%
unique_prices = steam_df['Original Price'].unique()
print(sorted(unique_prices))

# %% [markdown]
# Now we see that the only unique entries is numerical, for the `Original Price` data
# 
# Next, we take a look at the `All Time Reception` column

# %%
steam_df['All Time Reception'].isna().sum()

# %% [markdown]
# We only have 4 entries with 'NaN' in them. Let's remove them.

# %%
# steam_df.dropna(self, axis=1, how="any", thresh=None, subset=None, inplace=False)
steam_df.dropna(axis = 0, how = 'any', inplace = True)

# %%
steam_df

# %% [markdown]
# Next, we look regarding converting the 'Release Date' column to type `Date`, if need be.

# %%
steam_df['Release Date'].dtypes

# %%
# Convert it to DateTime
steam_df['Release Date'] = pd.to_datetime(steam_df['Release Date']) 

# %%
steam_df['Release Date'].dtypes

# %% [markdown]
# Nice. Now, we look thinning out the Memory, Storage, and OS

# %%
# Look at the unique memory values
unique_mem = steam_df['Memory'].unique()
sorted(unique_mem)

# %%
# Look at the unique storage values
unique_stor = steam_df['Storage'].unique()
# print(len(unique_stor)) #17 unique values
print(sorted(unique_stor))

# %%
# Look at the unique OS values
unique_os = steam_df['OS'].unique()
# print(len(unique_stor)) #17 unique values
sorted(unique_os)

# %% [markdown]
# Game Plan:
# 
# 1) Convert all RAM requirements in MB into GB using the fact that $1024 \text{ MB } = 1 \text{ GB }$
# 
# 2) Convert all Storage Requirements in MB to GB using the same fact as in (1)
# 
# Since both of these aforementioned features use similar units, we convert everything to GB = 1024 MB
# 
# 3) The hope with the `OS` column was that there'd be a mix of say `Windows`, `Windows/MacOs`, `MacOs/Linux`, etc. But, they're all Windows, and the `Release Date` column provides finer Date info, so we see no reason to keep. So, drop it.
# 
# _______________________________________
# 
# We start by making the functions that will clean the text entries of `Memory` and `Storage` by extracting the information, and converting to GB as needed.

# %%
# Given : A string with storage information in GB or MB
# Returns : The number (as float) representing the giving amount of GB (and converts to GB if amount was in MB)
def clean_space(ram):
  # Optimization note : Could factor out the following code chunk:
      # try:
      # ram_int = actual_ram[0] # Since ram value always starts with number
      # # print(ram_int)
      # convert_units_ram = np.divide(float(ram_int) , 1024.0)#float(ram_int) / 1024.0
      # return convert_units_ram
  
  # Author's Note : While not generalizable, there was so few rare cases that it is
  #   easier to just write them in
  print(ram)
  
  if '以' in ram:
    return 100.0
  if '4g' in ram:
    return 4.0

  if ram == '1':
    return 1 # This means there was no data from the scraping
  elif 'MB' in ram:
    # Convert it to GB, return the value
    actual_ram = ram.strip().split(' ')
    try:
      ram_int = actual_ram[0] # Since ram value always starts with number
      # print(ram_int)
      convert_units_ram = np.divide(float(ram_int) , 1024.0)#float(ram_int) / 1024.0
      return convert_units_ram
    except:
      actual_ram = ram.strip().split('M')
      ram_int = actual_ram[0]
      convert_units_ram = np.divide(float(ram_int) , 1024.0)#float(ram_int) / 1024.0
      return convert_units_ram
      
    print(ram_int)
    convert_units_ram = np.divide(float(ram_int) , 1024.0)#float(ram_int) / 1024.0
    return convert_units_ram
  
  # No conversion needed. Just extract GB amount
  elif 'GB' in ram:
    try:
      actual_ram = ram.strip().split(' ')
      ram_int = float(actual_ram[0]) * 1.0
      return ram_int 
    except:
      actual_ram = ram.strip().split('G')
      ram_int = float(actual_ram[0]) * 1.0
      return ram_int   

  else:
    return -1
  return -1

# %% [markdown]
# Since the function only extracts out the storage capacity (in GB), then, we can use it both on the RAM and the Storage columns to clean it (we print out each input before cleaning, for demonstration)

# %%
steam_df['Memory'] = ['1' if x == '1' or x == 1 else clean_space(x) for x in steam_df['Memory']]

# %%
steam_df['Storage'] = ['1' if x == '1' or x == 1 else clean_space(x) for x in steam_df['Storage']]

# %%
steam_df

# %% [markdown]
# Now, we proceed by removing the 'OS' column entirely (since everything was Windows), and then after we remove any rows with `1` as a value for `Processor` as a means for removing empty hardware data
# 
# Starting with removing `OS`...

# %%
steam_df = steam_df.drop(columns = "OS")

# %%
steam_df

# %% [markdown]
# Now before we remove empty hardware specs, we save two csv's, since they both have potential uses:
# 
# 1) A CSV with empty $[\text{ Graph }, \text{ Memory } ,\text{ Processor } ,\text{ Storage }] = [1,1,1,1]$ but the rest of the features intact
# 
# 2) A CSV without the empty features mentioned in (1)

# %%
# This data is the csv described in (1) (csv with [1,1,1,1]'s)
steam_df.to_csv('Steam Data Clean v5 (Cleaned).csv')

# %% [markdown]
# Then we save the csv with the empty hardware features removed

# %%
# If a 'Processor' cell has 1, then it means that no hardware specs were available for this game
steam_df = steam_df[steam_df.Processor != '1'] # Should keep games like Carto, Let's Build a Zoo, Dishonored: Death of the Outsider, Need for Speed payback

# %%
steam_df

# %% [markdown]
# We still see some items in the Graphics card (`Graphs`) column with 1, so let us remove those

# %%
steam_df = steam_df[steam_df.Graphs != '1'] # Will remove item # 2156 (Idle Big Devil)

# %%
steam_df

# %% [markdown]
# Voila. Now we save to csv and do some interesting data analysis with the 2,000-ish entries leftover

# %%
# This data is the csv described in (2) (csv WITHOUT [1,1,1,1]'s)
steam_df.to_csv('Steam Data Clean V5 (Cleaned - Empty Hardware Data Trimmed).csv')

# %%
unique_titles = steam_df['Title'].unique()

print(len(sorted(unique_titles)))

# %% [markdown]
# We have 2,150 cleaned titles.


