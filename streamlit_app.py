import streamlit as st
import pandas as pd
import datetime
import time
from textblob import TextBlob
import textwrap
import feedparser
import networkx as nx
import matplotlib.pyplot as plt

# Function to analyze sentiment
def analyze_sentiment(s):
    blob = TextBlob(s)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"

# Function to extract source and target companies from a string
def extract_companies(s, companies):
    pairs = [(source, target) for source in companies for target in companies if source != target and source.lower() in s.lower() and target.lower() in s.lower()]
    return pairs

# Fetch and parse RSS feeds
def fetch_feeds(selected_feeds, relevant_date, companies):
    partnerships = []
    for feed in selected_feeds:
        st.write("Parsing feed:", feed)
        entries = feedparser.parse(feed)['entries']
        for entry in entries:
            published = entry['published_parsed']
            published_datetime = datetime.datetime.fromtimestamp(time.mktime(published))
            if published_datetime >= relevant_date:
                title = entry['title']
                summary = entry['summary']

                # Wrap the summary to 100 characters
                summary = textwrap.fill(summary, width=100)

                # Extract source-target pairs
                pairs = extract_companies(title + summary, companies)

                # If any pairs were found, add the partnership to the list
                for source, target in pairs:
                    st.write("Found partnership:", source, target)
                    relationship = analyze_sentiment(title + summary)
                    st.write("Analyzing sentiment of partnership:", relationship)
                    partnership = {
                        'Source': source,
                        'Target': target,
                        'Relationship': relationship,
                        'Headline': title,
                        'Date': published_datetime.strftime('%Y%d%m')
                    }
                    partnerships.append(partnership)
    return partnerships

def draw_graph(df):
    G = nx.from_pandas_edgelist(df, 'Source', 'Target', edge_attr=True)
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 10))
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=1500, edge_cmap=plt.cm.Blues, pos=pos)
    plt.show()

def main():
    st.title("Partnerships Analysis")

    # Ask the user for input
    days = st.number_input("Enter how many days back you want to look (0 for today): ", min_value=0, value=0, step=1)

    # Calculate the relevant date
    relevant_date = datetime.datetime.today() - datetime.timedelta(days=days)
    st.write("Looking at entries from:", relevant_date)

    # List of RSS feeds to check
    all_feeds = [
        'http://feeds.reuters.com/reuters/businessNews',
        'http://feeds.bbci.co.uk/news/business/rss.xml',
        'https://www.theverge.com/rss/latest',
        'https://techcrunch.com/feed/',
        'https://9to5google.com/feed/',
        'https://www.macrumors.com/rss/',
        'https://arstechnica.com/feeds/all/',
        'https://www.wired.com/feed/',
        'https://www.technologyreview.com/feed/',
        'https://newatlas.com/feed/',
        'https://www.bbc.com/news/technology/rss',
        'https://edition.cnn.com/tech/rss.xml'
    ]
    st.write("Available feeds:")
    for i, feed in enumerate(all_feeds, start=1):
        st.write(i, feed)

    selected_feed_numbers = st.text_input("Enter the numbers of the feeds you want to use, separated by commas, or 'A' to use all feeds: ")

    # Parse the user's selection
    if selected_feed_numbers.upper() == 'A':
        selected_feeds = all_feeds
    else:
        selected_feeds = [all_feeds[int(i)-1] for i in selected_feed_numbers.split(',') if i]

    # List of companies to check
    companies = ['Apple', 'Microsoft', 'Google', 'Amazon', 'Nvidia', 'Tesla', 'TSMC']
    st.write("Companies to check:", companies)

    partnerships = fetch_feeds(selected_feeds, relevant_date, companies)

    # Convert partnerships to a dataframe
    df = pd.DataFrame(partnerships)

    # Print the dataframe
    st.write("Generated DataFrame:")
    st.dataframe(df)

    # Draw the graph
    draw_graph(df)

if __name__ == "__main__":
    main()
