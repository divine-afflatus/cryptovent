# cryptovent
Extraction of Cryptocurrency events from social media.

## The Big Picture
Bitcoin is a kind of currency that uses peer to peer networking to manage transactions without any central authority like banks. It has slowly been gaining popularity and is being used by a growing number of businesses in many countries. We aim to analyze trends in bitcoin prices and correlate these variations to twitter and chat conversations. This analysis can be very useful in extracting events related to bitcoin. Another interesting application of this analysis could be to predict change in bitcoin price by extracting impactful entities and phrases i.e. entities that have a strong correlation with variations in price trends. 

## Data
* Prices from BTC-e cryptoexchange: from August 2011 until today.
* Prices from MtGox cryptoexchange: from July 2010 until today.
* Chat logs from BTC-e cryptoexchange: from April 2013 until today.
    - Pros: Cryptocurrency-specific
    - Cons: Not annotated.
* Annotated (POS, NE, events) Twitter stream: from September 2008 to March 2013.
    - Cons: It is not cryptocurrency-specific.
* Historical timeline of Bitcoin with all significant events since its conception. This can be used for evaluation.

Since twitter and btc-e chat logs are not overlapping in time, we would like to treat them as completely separate datasets. So we will have two datasets, from July 2010 to March 2013 (MtGox and Twitter) and from April 2013 until present (MtGox / BTC-e and BTC-e chat logs).

Next, we might consider cutting the datasets in some proportion to get train and test data. Unfortunately, since both Twitter and Bitcoin were created very recently (2006 and 2008 respectively), the datasets that we have exhibit a lot of variation with time. If we were to cut them in the middle to make training and test sets these sets of data would be very different from one another. Thus we would like to intersperse train and test fragments.

## Approach
Initially, we intend to perform a series of investigative experiments to understand the scope of our data, and how well we can leverage it to perform future event extraction tasks. We have divided this initial phase into 3 parts. 

### Price data analysis
* Convert prices to log-domain and calculate their rate of change. The resulting values will represent relative change in prices over time.
* Ideally we want to learn how to decompose our signal into:
    - Seasonal components (week, month, year).
    - Global trend.
    - Hierarchy of Events. Assuming that price change is usually random, but during events its distribution changes, we can use HMM to predict when this happens.

### Twitter data analysis
* Extract bitcoin related tweets from the annotated twitter dataset, and analyze the variation of frequency of these tweets with respect to time.
* Compare this with trends in bitcoin prices.
* Use a technique like frequent itemset mining to identify sets of entities that co-occur frequently in relevant tweets.
* These entity sets can be used to identify and extract impacting words and phrases that seem to strongly affect the price trends.
* If the above experiments prove successful, we can use the words and phrases extracted to derive more linguistic features to train a classifier that extracts events.
* Investigate whether a similar approach is effective for chat data.

### Sentiment Trends Analysis
* Analyze trends in sentiments of Tweets and Chat data and correlate it to changes in price of Bitcoin.
    - A positive trend of sentiments should ideally coincide with an increase in Bitcoin price
* Correlate magnitude of sentiment change and corresponding change in price.
* Possibly use spiking trends in combination with entities to detect events. 

## Evaluation
For our event extraction, we will use the events from the Bitcoin history website, which contains a timeline of all significant events relating to bitcoin, since its conception. These events can be used as the ground truth to measure precision and recall.

## Work Split
* Price Data Analysis - Alexander Konovalov
* Twitter Data Analysis - Lakshmikanth Kaushik
* Sentiment Trends Analysis - Paranjay Srivastava

## References
1. Richard Socher, Alex Perelygin, Jean Y. Wu, Jason Chuang, Christopher D. Manning, Andrew Y. Ng and Christopher Potts, “Recursive Deep Models for Semantic Compositionality Over a Sentiment Treebank”.
2. Hassan Saif, Yulan He and Harith Alani,”Semantic Sentiment Analysis of Twitter”.
3. Alan Ritter, Evan Wright William Casey and Tom Mitchell, “Weakly Supervised Extraction of Computer Security Events from Twitter”.
4. Alan Ritter, Sam Clark, Mausam, Oren Etzioni, “Named Entity Recognition in Tweets: An Experimental Study”
5. Wayne Xin Zhao, Jing Jiang, Jing He, Yang Song, Palakorn Achananuparp, Ee-Peng Lim, Xiaoming Li “Topical Keyphrase Extraction from Twitter”
6. Edward Benson, Aria Haghighi, and Regina Barzilay “Event Discovery in Social Media Feeds”
