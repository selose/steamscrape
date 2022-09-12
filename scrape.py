# %% [markdown]
# # Final Scrape!
# 
# 
# 

# %% [markdown]
# Here, we started with the original implementation and updated to include more stuff like more tags, all-time player count, etc.

# %%
# Imports
import pandas as pd
import bs4
import urllib.request

# %% [markdown]
# Load list of Steam URLS from our text file (Using v3 of the steam links)

# %%
# Sample URLS in an array for testing
# URL_ARRAY = [ 'https://store.steampowered.com/app/1599340/Lost_Ark/',           
#               'https://store.steampowered.com/app/1366540/Dyson_Sphere_Program/?curator_clanid=4777282&utm_source=SteamDB',
#               'https://store.steampowered.com/app/559100/Phantom_Doctrine/',
#               'https://store.steampowered.com/app/238960/Path_of_Exile/?curator_clanid=4777282',
#               'https://store.steampowered.com/app/1092790/Inscryption/',
#               'https://store.steampowered.com/app/275850/No_Mans_Sky/',
#               'https://store.steampowered.com/app/274170/Hotline_Miami_2_Wrong_Number/',
#              'https://store.steampowered.com/app/597820/BIOMUTANT/',
#              'https://store.steampowered.com/app/1923790/Linelith/',
#              'https://store.steampowered.com/app/1506830/FIFA_22/']


# Actual Arrays for Our Data Collection
# Open up text file
steam_links_from_text_file = open("steam_links_v3.txt","r")
content = steam_links_from_text_file.read()
print(content)
# Split by new line, since every link is on it's own line
URL_ARRAY = content.split("\n")
steam_links_from_text_file.close()



# %%
url_set = set(URL_ARRAY) # Remove duplicates

# %%
len(url_set)

# %% [markdown]
# The 'meat' of this scraper. The Steam Page Scraper, with it's extraction helper methods.

# %%
# Given a <div> tag containing the ORIGINAL price, will extract the numerical value from the div tag
# Input Form : <div class="discount_original_price">$39.99</div> | Output: 39.99
def extract_price(steam_page_price_div, steamed_soup):
  price = -1; # -1 comes up if no price was found

  # If the div-tage is empty...
  if steam_page_price_div == None:
    # ...the price is likely contained in another tag. Look for it and extract the price...
    steam_page_price_div = steamed_soup.find("div", {"class": "discount_original_price"})

  # Making the assumption that div tag has only one item
  for item in steam_page_price_div:
    # print(item)
    price = item.strip()

  return price

# Given a Steam URL (for example, https://store.steampowered.com/app/1092790/Inscryption/)
#   will extract the corresponding app_ID
def extract_app_id(steam_url):
  # Split by '/'
  # https://store.steampowered.com/app/1092790/Inscryption/) <- App ID will be 5th element

  forward_slash = steam_url.split('/')
  return forward_slash[4]

# Given bs4 object of a steam page
#   Returns developer, publisher, genre as string
def extract_info(steamed_soup):
  everything = steamed_soup.find(id = 'genresAndManufacturer')

  #Now here, I realized I could extract genre, Developer, Publisher/

  # Developer
  developer_name = ''
  dev = everything.find('div', {'class' : 'dev_row'}).find('a')
  for developer in dev: # Again, assuming there's only one developer 
    developer_name = developer

  # Publisher
  # Get the list of div-tags of type 'dev_row'. 2nd one in list is publisher
  publisher = everything.find_all('div', {'class' : 'dev_row'})

  publisher_name = '' # Placeholder for publisher name
  i = 0 # When i = 1, that's our location of the publisher
  for item in publisher:
    if i == 1: # Publisher name is the <a> tag in the second 'dev_row' <div> tag
      for a_tag_value in item.find('a'): # Get the publisher a-tag
        publisher_name = a_tag_value #Since each a-tag has only one list of publishers
    i = i + 1 # Increment if i = 0
  
  # Genre
  b_tags = steamed_soup.find('span', {'data-panel' : '{"flow-children":"row"}'}).find('a')
  genre = b_tags.text
  # print("~~~~~~~~~~~~~~~~ NEXT GAME~~~~~~~~~~~~~~~~~~")
  return [developer_name,publisher_name,genre]


  # Given a bs4 object a Steam Page, gets the release date
def extract_date(steamed_soup):
  date = steamed_soup.find('div' , {'class' : 'date'})
  release_date = date.text
  return release_date

# Given a bs4 object of a steam page, gets the tags from'Popular user-defined tags for this product:' 
def extract_user_tags(steamed_soup):
  tag_list = ['']

  # Get list of tags
  tags = steamed_soup.find_all('a', {'class' : 'app_tag'})
  tag_list = [''] * len(tags)  # Make an array for the tags
  i = 0 # indexing for the array
  for tag in tags:
      tag_list[i] = tag.text.strip()
      # print(tag.text.strip())
      i = i + 1

  # print("~~~~~~~~~~~~~~~~ NEXT GAME~~~~~~~~~~~~~~~~~~")
  return tag_list

def extract_all_review_summary(steamed_soup):
  # Not all pages have this rating. Return 'N/A' if so
  try :
      e_a_r_s = steamed_soup.find('span', {'class' : 'game_review_summary positive'})
      # print(e_a_r_s.text)
      return e_a_r_s.text
  except:
    #  print('no rating found')
     return 'N/A'
  # print("~~~~~~~~~~~~~~~~ NEXT GAME~~~~~~~~~~~~~~~~~~")
  return -1

 # Given a bs4 object of a Steam Page, gets the TOTAL review count (not recent)
def extract_review_count(steamed_soup):
  rev_count_tag = steamed_soup.find('meta', attrs={'itemprop': 'reviewCount'})
  return rev_count_tag['content']

 # Given a bs4 object of a Steam Page, gets the current rating of the title
def extract_current_rating(steamed_soup):
  curr_rating = steamed_soup.find('meta', attrs={'itemprop': 'ratingValue'})
  return curr_rating['content']

 # Given a bs4 object of a Steam Page, gets the best rating recieved
def extract_best_rating(steamed_soup):
  best_rating = steamed_soup.find('meta', attrs={'itemprop': 'bestRating'})
  return best_rating['content']

 # Given a bs4 object of a Steam Page, gets the worst rating recieved
def extract_worst_rating(steamed_soup):
  worst_rating = steamed_soup.find('meta', attrs={'itemprop': 'worstRating'})
  return worst_rating['content']


 # Given a bs4 object of a Steam Page, gets the game title
def extract_steam_title(steamed_soup):
  game_name = steamed_soup.find('div', {'id': 'appHubAppName'})
  title = game_name.get_text()
  return title

# Given: A url (as string) of a particular page for a steam
# Returns: A LIST consisting of the steam game info, for use with dataframe
# This is the function for scraping ONE single steam page
# If app_ID is -1, then app_ID isn't known
def steam_scrape(steam_url, app_ID):
    # Store specifications in a list
    # For now we have an array of length 6. Adjust this size later when we add more parameters
    spec_list = [1] * ( 18 ) # 6 original arguments, and the 12 extra for the app_ID, original price, etc
    len(spec_list)

    # Get the steam url response from urllib and parse it with BeautifulSoup
    response_steam_page = urllib.request.urlopen(steam_url).read()
    steamed_soup = bs4.BeautifulSoup(response_steam_page, features="html.parser")

    # Get the div tag that stores the minimum requirements
    # ul_minimum = steamed_soup.find('div', {'class': 'game_area_sys_req_leftCol'}).find_all('li')
    ul_min = True # If ul_minimum tag was found
    try: # look for game info
      ul_minimum = steamed_soup.find('div', {'class': 'game_area_sys_req_leftCol'}).find_all('li')
    except: # add NA if nothing found
      ul_min = False
      ul_minimum = ['Error:Error'] * 5 # Since this ul-minimum tag always has 5 items

    # Extract corresponding information from this tag
    # NOTE TO SELF: This could go into it's own function
    for li in ul_minimum:
      if ul_min:
          requirement_pair = li.get_text().split(":")
          # print(requirement_pair)
          if 'OS' in requirement_pair:
              # print(requirement_pair)
              spec_list[3] = requirement_pair[1]
              # specification_dict['OS'] = requirement_pair[1]
          if 'Processor' in requirement_pair:
              # print(requirement_pair)
              spec_list[4] = requirement_pair[1]
              # specification_dict['Processer'] = requirement_pair[1]
          if 'Memory' in requirement_pair:
              spec_list[2] = requirement_pair[1]
              # specification_dict['Memory'] = requirement_pair[1]
          if 'Graphics' in requirement_pair:
              spec_list[1] = requirement_pair[1]
              # specification_dict['Graphics'] = requirement_pair[1]
          if 'Storage' in requirement_pair:
              spec_list[5] = requirement_pair[1]
              # specification_dict['Storage'] = requirement_pair[1]

    # Get the title of the Steam Page
    title = extract_steam_title(steamed_soup)

    # Get the div tag that stores the original price of the game
    # class="discount_original_price"
    div_original_price = steamed_soup.find("div", {"class": "game_purchase_price price"})

    # Not all steam pages will have the div-tag of class 'game_purchase_price price'
    # In such a case, we fall back on finding other possible tags in the steamed_soup
    # Pass a reference to steamed_soup to this function so that we may look for other tags, if needed.
    price = extract_price(div_original_price, steamed_soup)

    # App_ID is -1 if none found. Otherwise, we extract it here
    app_ID = extract_app_id(steam_url)

    # Developer, Publisher, Genre
    developer,publisher,genre = extract_info(steamed_soup)

    # Release Date
    release_date = extract_date(steamed_soup)

    # User Tags
    user_tags = extract_user_tags(steamed_soup)

    # All-Time Review Rating (as string)
    all_time_reception = extract_all_review_summary(steamed_soup)

    # 'Microdata' (Review Count, Current Rating Value, Best Rating, Worst Rating)
    all_review_count = extract_review_count(steamed_soup)

    # Current Rating Value
    current_Rating = extract_current_rating(steamed_soup)

    # Best Rating recieved
    best_rating = extract_best_rating(steamed_soup)

    # Worst Rating recieved
    worst_rating = extract_worst_rating(steamed_soup)

    #________________ Store the scraped info _____________

    # Store the title
    spec_list[0] = title

    # Store the app_id
    spec_list[6] = str(app_ID) # Add the app_ID as string to avoid any Int-String type mismatch issues

    # store price
    spec_list[7] = price

    # Store developer
    spec_list[8] = developer

    # Store Publisher
    spec_list[9] = publisher

    # Store Genre
    spec_list[10] = genre

    # Store release date
    spec_list[11] = release_date

    # User tags
    spec_list [12] = user_tags

    # Store All Time Reception (Mostly Positive, Mixed, etc)
    spec_list[13] = all_time_reception

    # Store 'ALL Review Count'
    spec_list[14] = all_review_count

    # Rating 
    spec_list[15] = current_Rating

    # Best Rating Recieved
    spec_list[16] = best_rating

    # Worst Rating Recieved
    spec_list[17] = worst_rating

    return spec_list

# %% [markdown]
# Run the actual scraping process, with the functions defined above, then store in a df
# 
# We note that not all Steam links are scrapable, so we print out any links that couldn't be scraped. In the full scrape, there wasn't enough unscrapable entries to cause worry. Don't remember the exact figure, but it was around 30-80 entries, which is a very acceptable loss in a data set of ~4,388 entries.

# %%
limit = 50

# Get a list of scrapes from a list of steam pages
list_of_specs = []  # A List of steam page items. Each steam page item is a list containing hardware + other info
# Build the data from list
i = 0
for item in url_set:
    if i > 50:
      break
    
    try:
      steam_page_info = steam_scrape(item, -1) # Just put -1 as a placeholder.
      list_of_specs.append(steam_page_info)
    except:
      print("ERROR FOR URL : "  + str(item))

# Construct our dataframe
hw_df = pd.DataFrame(list_of_specs, columns=["Title", "Graphs", "Memory", "OS", "Processor", "Storage","app_id", "Original Price", "Developer","Publisher","Genre",\
                                             "Release Date", "User Tags", "All Time Reception", "Total Count of Reviews", "Rating", "Best Rating", "Worst Rating"])


# Print to csv
# hw_df.to_csv('steam_hardware_data.csv')

# %%
len(hw_df)

# %%
hw_df

# %% [markdown]
# Then, we save to csv, and clean in another .ipynb

# %%
# v5 means using v3 of steam_links data with v4 of scraping script
hw_df.to_csv('steam_hardware_data_demonstration.csv')


