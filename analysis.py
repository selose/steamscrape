# %% [markdown]
# # Final Analysis
# After many feature fine tuning, seeing which particular feature can be well-fitted by the data, and many mg of caffiene, we come to the final model
# 
# ### Motivation
# I found the process of finding a linear model that predicts some sort of feature well. Initially, we wanted to predict the 'All-Time Reception' but due to the fact that we could only scrape steam pages that are $\ge \text{Positive}$, and the fact that $\ge 90\%$ of them had a 'All-Time-Reception' score of 0.5, it was in effect adding a constant.
# 
# So, we had to pivot. 
# 
# ### The Pivot
# Long Story short, we found we could pivot the data and produce a linear regression model that predicts how 'passionate' users are for a game.
# 
# Relying on the fact that people tend to make the effort to actually review stuff when they really 'love' or 'hate' a game, then, we can consider the 'Total Amount Of Reviews' as a metric for measuring passion.

# %%
import pandas as pd
import seaborn as sns
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression


# %%
steam_df = pd.read_csv('full_df.csv')

# %%
steam_df = steam_df.drop(columns = steam_df.columns[0])

# %%
steam_df

# %% [markdown]
# We first look at the pairplots and coefficient matrix to observe any linear relations
# 
# A coefficient matrix is just a grid of all the variables in the data frame and their corresponding coefficient which measures their linearity

# %%
steam_df.corr(method = 'pearson', min_periods = 1)

# %% [markdown]
# We then take a look at the pairplot.
# 
# **Note: Ignore app_id, as it isn't numerical data**
# 
# This is a nice corresponding visual to the coefficient matrix, as they both convey the same idea

# %%
sns.pairplot(data = steam_df)

# %% [markdown]
# We look for multicollinearity, and find that `Storage` has the highest correlation coefficients with `Memory` and `Original Price` (with a coefficient of 0.469927, and 0.446873 respectively)
# 
# So, we can remove that variable later on.
# 
# 
# Now, we look at transformations 

# %%
steam_df.hist()

# %% [markdown]
# After doing some experimentation on transformations on the data, we apply the following transformations on them, and remove the outlier from 'Memory'

# %%
steam_df['Memory'].sort_values(ascending = False)

# %%
steam_df.values[1417]

# %%
steam_df.values[1195]

# %%
steam_df = steam_df.drop(labels=[1417,1195], axis=0)

# %%
steam_df['Memory'].sort_values(ascending = False)

# %% [markdown]
# # 👍

# %% [markdown]
# Now we transform and hope for a better outcome
# 
# Behind the scenes: I simply created histograms for a each variable. And in each histogram, we note which mathematical transformation produced the best histogram density plot. It ended up being that cube root, or square root was the best transformation.
# 
# So, I decided to do cube root transformation on all the features that can take such a transformation to begin with.
# 
# Obviously, one-hot variables, wouldn't be able to take transformations
# 
# Variables that have a low range of values (for example, Rating, All-Time-Reception, etC) failed to show any hint of promising transformation
# 

# %%
steam_df['Memory'] = np.cbrt(steam_df['Memory'])

# %%
steam_df['Storage'] = np.cbrt(steam_df['Storage'])

# %%
steam_df['Original Price'] = np.cbrt(steam_df['Original Price'])

# %%
steam_df.hist()

# %% [markdown]
# # Test Model Function
# 
# Just importing for continued analysis

# %%
def test_model(X,y,seed,ts):
  # Split the data into training/testing sets

  # x_test, y_test for testing
  x_tr_val, x_test, y_tr_val, y_test = train_test_split(X,y,test_size = ts, random_state = seed)
  #x_tr_val, y_tr_val for splitting again into training and validation data
  x_train, x_validation, y_train, y_validation = train_test_split(x_tr_val,y_tr_val,test_size = ts, random_state = seed)

  print("x splits")
  print("train: " + str(x_train.shape))
  print("validation: " + str(x_validation.shape)) #
  print("test: " + str(x_test.shape))

  print("\ny splits")
  print("train: " + str(y_train.shape))
  print("validation: " + str(y_validation.shape))#
  print("test: " + str(y_test.shape))

  # Define model
  lm = linear_model.LinearRegression()
  # Train data
  lm.fit(x_train, y_train)
  # Get r^2 metric
  r_sq = lm.score(x_validation,y_validation)
  print("\n R^2 Coeff. = ", r_sq)

  # Coefficients
  print("Intercept: " + str(lm.intercept_) + '\n Coefficients : ' + str(lm.coef_))

  # RMSE 
  print("RMSE: " + str(mean_squared_error(y , lm.predict(X) , squared=False)))

  # Predict
  y_pred_validation = lm.predict(x_validation)
  sns.scatterplot(y_validation,y_pred_validation)
  print('\n')



# %% [markdown]
# # Add One Hot Variables on Genre

# %%
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder()
origin_hot = ohe.fit_transform(steam_df[["Genre"]])
print(origin_hot.toarray())
print(ohe.categories_)
steam_df[ohe.categories_[0]] = origin_hot.toarray()


# %% [markdown]
# # Remove Multicollinearity
# 
# Now that we have more variables, we look for multicollinearity again. Take note the matrix is symmetric along the diagonal, so we only look in the upper (or lower half). The following has high coefficients:
# 
# * Action vs **Adventure** : -0.512090
# 
# * Action vs **Casual** : -0.335881
# 
# * **Total Count of Reviews** vs All Time Player Count : 0.539844
# 
# * All Time Reception vs **Rating** : 0.526120
# 
# So we can exclude the following from our model testing in regards to features as input
# 
# * Remove Action (It has high coefficient values in two instances)
# 
# * Remove All Time Player Count (Even though we went through an effort to find this, it was from a 3rd party source. Different websites had different counts, so, we can use the source from Steam itself and use Review count instead)
# 
# * Remove All-Time Reception since Rating provides a wider range (and thus, finder data)
# 
# 

# %%
test_model(steam_df[['Memory', 'Rating', 'Original Price']].to_numpy(), steam_df['Total Count of Reviews'].to_numpy(), 532231, 0.25)

# %%
steam_df.corr(method = 'pearson', min_periods = 1)

# %% [markdown]
# # Results

# %% [markdown]
# 
# And every technique applied to improve the data is applied to all these models
# * Normalized input 
# * Cube Root Transform on Memory and Original Price
# * Removed Outliers from Memory
# * Add in `All-Time Player Count`, normalize it 
# 
# And now we can try to predict both 'Overall Reception' and 'Review Count', using the same feature input to predict both.

# %% [markdown]
# ### Baseline 

# %%
# R^2 Coeff  0.225458, RMSE 0.130318
# test_model(steam_df[['Memory', 'Rating', 'Original Price']].to_numpy(), steam_df['All Time Reception'].to_numpy(), 532231, 0.25)

# R^2 Coeff  0.073298, RMSE 0.046702
test_model(steam_df[['Memory', 'Rating', 'Original Price']].to_numpy(), steam_df['Total Count of Reviews'].to_numpy(), 532231, 0.25)


# %% [markdown]
# # Adding in OHE (excluding Action)

# %%
# R^2 Coeff. =  0.06988080580879363, RMSE: 0.04656930015830441
test_model(steam_df[['Memory', 'Rating', 'Original Price','Adventure', 'Casual','Free to Play', 'Indie', 'Massively Multiplayer', \
                     'RPG', 'Racing', 'Simulation', 'Sports', 'Strategy']].to_numpy(), steam_df['Total Count of Reviews'].to_numpy(), 532231, 0.25)

# R^2 Coeff. =  0.011597697322164868, RMSE: 0.03851688485907299
# test_model(steam_df[['Memory', 'Original Price','Adventure', 'Casual','Free to Play', 'Indie', 'Massively Multiplayer', \
#                      'RPG', 'Racing', 'Simulation', 'Sports', 'Strategy']].to_numpy(), steam_df['Rating'].to_numpy(), 532231, 0.25)



