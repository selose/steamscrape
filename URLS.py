# %% [markdown]
# # Steam Links Again
# 
# Here, `steam_links_v2.txt` is a result of that bot, and we simply clean out the tracking info from v2 to create the final clean version `steam_links_v3.txt`

# %%
# Open up v2 text file
steam_links_from_text_file = open("steam_links_v2.txt","r")
content = steam_links_from_text_file.read()
print(content)
# Split by new line, since every link is on it's own line
URL_ARRAY = content.split("\n")
steam_links_from_text_file.close()

# %%
url_set = set(URL_ARRAY) # Remove duplicates

# %%
clean_url_set = [] # Prepare for cleaning of trackers

# %%
# Removes the tracking info from the url
# Given : https://store.steampowered.com/app/367520/Hollow_Knight/?snr=1_7_7_230_150_3 as string
# Returns : https://store.steampowered.com/app/367520/Hollow_Knight/ as string 
def clean_url(url):
  url_split = url.split('?')
  # print(url_split[0])
  return url_split[0]

clean_url("https://store.steampowered.com/app/367520/Hollow_Knight/?snr=1_7_7_230_150_3") 

# %%
# Clean each url with a tracker
for url in url_set:
  print(clean_url(url))
  clean_url_set.append(clean_url(url))

# %% [markdown]
# We get 4388 entries to start our cleaning (of the data, not links) process.

# %%
len(clean_url_set)

# %% [markdown]
# Now we store for v3 of the links, postfixing a `\n` at the end of entry for easy conversion between text file and python list

# %%
with open('steam_links_v3.txt', 'w') as txtfile:
    for url_link in clean_url_set:
        txtfile.write(url_link + '\n')


