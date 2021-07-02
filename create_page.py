import praw
import shutil
import webbrowser
import os
import time

# File    : create_page.py
# Author  : Devin Arena
# Date    : 7/1/2021
# Purpose : Grabs images and gifs from specified subreddits and places
#           them on a nicely formatted HTMl document, opening the document
#           in the default web browser.

# proper file extentions to display
img_ext = ["png", "jpg", "jpeg", "gif", "gifv"]

# Initializes the PRAW reddit object for API calls
def init():
    # anonymized, doesn't actually require authentication unless 
    # grabbing from your subscribed subreddits
    reddit = praw.Reddit(
        client_id="",
        client_secret="",
        user_agent="",
        username="",
        password=""
    )
    get_subs(reddit)

# Asks the user to enters the subreddits they wish to generate from.
# If a user enters nothing, it takes from their saved subreddits.
# Also asks the user how many posts they wish to grab from each subreddit.
def get_subs(reddit):
    print("Please enter the subreddits you wish to download from seperated by commas (,)")
    print("If you wish to use your subscribed subreddits, simply enter nothing.")
    subList = input("Subreddits > ")
    print("Now enter the number of posts you wish to grab from the hot section.")
    print("Warning: a lot of posts can take a decent time to grab.")
    np = input("# posts > ")
    # wait for a number to be entered
    while not np.isnumeric():
        print("Please enter a number!")
        np = input("# posts > ")
    num_posts = int(np)
    posts = []
    progress = 0
    # iterate over all entered subs and grab hottest 10 posts
    if len(subList) > 0:
        total = len(subList.split(","))
        for subName in subList.split(","):
            try:
                sub = reddit.subreddits.search_by_name(subName, exact=True)
                posts.extend(list(sub[0].hot(limit=num_posts)))
                progress += 1
                print(
                    f"Grabbed {num_posts} posts from {subName} ({progress * 100 / total}%)")
            except:
                print("Subreddit does not exist! Skipping...")
    # Nothing was entered, instead use joined subreddits
    else:
        total = len(list(reddit.user.subreddits()))
        for sub in reddit.user.subreddits():
            posts.extend(sub.hot(limit=num_posts))
            progress += 1
            print(
                f"Grabbed {num_posts} posts from {sub.display_name} ({progress * 100 / total}%)")
    create_open_html(reddit, posts)

# Grabs links for all grabbed posts and adds them
# to the generated HTML file as anchor and image tags.
def create_open_html(reddit, posts):
    # copy the template
    shutil.copy("./template.html", "./generated.html")
    # open the file
    file = open("./generated.html", 'a')
    # loop over all grabbed posts
    for post in posts:
        url = str(post.url)
        for e in img_ext:
            if url.endswith(e):
                # convert gifv to gif
                click_url = reddit.config.reddit_url + post.permalink
                if url.endswith("gifv"):
                    click_url = url
                    url = url[0:-1]
                # some very ugly formatted strings to make the html file look nice
                # not necessary but looks nice
                file.write(
                    f"\n\t<div class=\"pic\">\n\t\t<a href=\"{click_url}\" target=\"_blank\"><img src=\"{url}\" /></a>\n\t\t<h1>{post.title}</h1>\n\t</div>")
                print(f"Generated image for {url}")
                break
    # finish the html file
    file.write("\n</body>\n\n</html>")
    print("File created, opening in default browser...")
    # opens the HTML page in the user's default browser.
    webbrowser.open_new(f"file://{os.path.realpath('./generated.html')}")


# main entry point, calls init function, also tracks how long the process takes (for fun)
if __name__ == "__main__":
    start = time.time()
    init()
    print(f"Process completed, only took {time.time() - start} seconds.")
