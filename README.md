# Evaluate Predictability of Daily Returns Based on Crowd Based Sentiment Data

## Quickstart

1.  Install MongoDB (\>=4.2)

2.  Install Python3 (\>=3.8)

3.  Clone the
    repository`git clone git@github.com:marwage/stockprediction.git`

4.  Install Python packages`pip3 install -r requirements.txt`

5.  Get API keys and place them into `crawling/accesstoken`

6.  Run a scripte.g. `python3 twitterv2academic.py`

## Prerequisites

### Code

The repository of the code is hosted on Github. The website[^1] shows
the code and project structure. To clone the git repository and get the
code on the local storage the following command must be executed.

    git clone git@github.com:marwage/stock_prediction.git

### Database

We use MongoDB, because it gives us the flexibility of JSON objects and
the responses for API queries are in the JSON format. How to install
MongoDB, depends on the operating system used. We refer to the
website[^2] for how to install MongoDB on a certain operating system. In
our system, we used the MongoDB version of 4.2. That implies, that to
run the script, one needs to install at least version 4.2. A MongoDB
holds several databases. Each database consists of collections and each
collection consists of documents.

### Python

#### Python interpreter

The code is written in Python 3. Our system uses Python in version 3.8.
To run the code without any issues, Python must be installed in at least
version 3.8. With the Ubuntu operating systems, the following command
must be executed on the shell to install Python 3.8.

    sudo apt install python3.8

#### Python packages

We use many third-party Python packages. The packages and the required
version are stored in the `requirements.txt` file. For instance, we need
to install Tensorflow[^3] or Pymongo[^4]. To install all packages at
once, execute the following command.

    pip3 install -r requirements.txt

## Project structure

The overall structure of the project can be seen in the following tree.

    ├── crawling
    │   ├── access_token
    │   │   ├── alpha_vantage_apikey.json
    │   │   ├── twitter_access_token.json
    │   │   └── twitter_bearer_token.json
    │   ├── check_proxies.py
    │   ├── company_info.py
    │   ├── data
    │   │   ├── finished_companies.json
    │   │   ├── proxy_list.txt
    │   │   ├── sp500_20190918.json
    │   │   ├── sp500_20210125.json
    │   │   ├── sp500_constituents.csv
    │   │   ├── sp500.json
    │   │   └── working_proxies.json
    │   ├── merge_sp500.py
    │   ├── sp500_to_json.py
    │   ├── stock_price.py
    │   ├── stocktwits.py
    │   ├── twitter_v1.py
    │   ├── twitter_v2_academic.py
    │   └── twitter_v2.py
    ├── database
    │   ├── add_date.py
    │   ├── check_companies.py
    │   ├── check_duplicates.py
    │   ├── clean_stock_price_db.py
    │   ├── create_index_date.py
    │   ├── fix_date_attribute.py
    │   ├── reformat_stock_price.py
    │   └── __init__.py
    ├── LICENSE.md
    ├── preprocessing
    │   ├── create_training_data_set.py
    │   ├── create_training_samples.py
    │   ├── create_twitter_three.py
    │   ├── data
    │   │   ├── industries.csv
    │   │   └── sectors.csv
    │   └── get_industry_sector.py
    ├── README.md
    ├── requirements.txt
    ├── stats
    │   ├── count_dataset_entries.py
    │   ├── count_tweets_company.py
    │   ├── count_tweets_day.py
    │   ├── mean_sentiment.py
    │   ├── plot_regression.py
    │   ├── plot_tweets_per_day.py
    │   ├── sample_company_info.py
    │   ├── sample_dates.py
    │   ├── sample_tweets.py
    │   └── sentiment.py
    ├── structure.txt
    ├── training
    │   ├── clean.sh
    │   ├── create_tf_data_set.py
    │   ├── regression.py
    │   ├── start_block_study.sh
    │   ├── start_study.sh
    │   ├── training_blocks.py
    │   └── training.py
    └── util
        ├── read_sp500.py
        └── threads.py

### Crawling

In the directory `crawling` are all scripts and data related to the
gathering of data. The scripts are Python code using access tokens and a
company list.

#### Twitter API v1.1

The script `twitterv1.py` crawls recent tweets using the Twitter API
v1.1[^5]. The search looks for recent tweets containing *\#COMPANY* or
*\$COMPANY*. The tweets are stored in the MongoDB database `twitterdb`
and each company has its collection. Necessary data for the crawling to
work are `accesstoken/twitteraccesstoken.json` and `data/sp500.json`.
`data/sp500.json` is a list of companies that are in the S&P500 index.
`accesstoken/twitteraccesstoken.json` holds the keys for authenticating
to the API. The twitter access token needs to have the values
`consumerkey`, `consumersecret`, `accesstokenkey`, `accesstokensecret`
for API v1.1. One needs to get the values from one's project at Twitter
Developer website[^6]. An example Twitter access token JSON file looks
like the following.

    {
        "consumer_key": "7M6lOy2JhLSsVbLxAMr0aZ2iq",
        "consumer_secret": "I7zcCcHG7QSxm1atPkr5rtEJcMRTC",
        "access_token_key": "11ZK2fVjdruh8Nl1k1CO5XO",
        "access_token_secret": "Ou4m8wKhxwzaHyXZAHuo7t7WlWg"
    }

#### Twitter API v2.0

The script `twitterv2.py` crawls recent tweets using the Twitter API
v2.0. The search looks for recent tweets containing *\#COMPANY* or
*\$COMPANY*. The tweets are stored in the MongoDB database `twitterv2db`
and each company has its collection. Necessary data for the crawling to
work are `accesstoken/twitterbearertoken.json` and `data/sp500.json`.
`data/sp500.json` is a list of companies that are in the S&P500 index.
`accesstoken/twitterbearertoken.json` holds the keys for authenticating
to the API. The Twitter bearer token needs to have the value
`bearertoken` for API v2.0. One needs to get the values from one's
project at Twitter Developer website[^7]. An example Twitter bearer
token JSON file looks like the following.

    {
        "bearer_token": "0nTcAexPEF8u1tWN8lNudRDoav3c4GYpU"
    }

The script `twitterv2academic.py` crawls all tweets in a time window
using the Twitter API v2.0[^8]. The tweets are stored in the MongoDB
database `twitterv2db` and each company has its collection. If we start
the script without arguments, such as

    python3 twitter_v2_academic.py

then the search looks for recent tweets containing *\#COMPANY* or
*\$COMPANY*. If we start the script with the argument `–onlycashtag`,
such as

    python3 twitter_v2_academic.py --onlycashtag

then the search looks for recent tweets only containing *\$COMPANY*.
Inside the code of the script is the variable `firstdate`. The variable
defines from when until now tweets should be crawled. Necessary data for
the crawling to work are `accesstoken/twitterbearertoken.json` and
`data/sp500.json`. `data/sp500.json` is a list of companies that are in
the S&P500 index. `accesstoken/twitterbearertoken.json` holds the keys
for authenticating to the API, as described above with the script
`twitterv2.py`. The file `data/finishedcompanies.json` holds a list of
companies for which the script finished crawling all the tweets. It
helps to avoid crawling all tweets again in the event of an error.

#### Stocktwits

The script `stocktwits.py` crawls recent ideas using the Stocktwits API.
The search looks for recent ideas containing *\$COMPANY*. The ideas are
stored in the MongoDB database `stocktwitsdb` and each company has its
collection. Necessary data for the crawling to work is
`data/sp500.json`. `data/sp500.json` is a list of companies that are in
the S&P500 index. To speed up the crawling of Stocktwits, the script can
be called with the `–threading` argument. In this case, the command
looks like the following.

    python3 stocktwits.py --threading

#### Stock price

The script `stockprice.py` crawls all stock prices in a time window
using the Alpha Vantage API[^9]. The stock prices for each day are
stored in the MongoDB database `stockpricedb` and each company has its
collection. Inside the code of the script is the variable `startdate`.
The variable defines from when until now stock prices should be crawled.
Necessary data for the crawling to work are
`accesstoken/alphavantageapikey.json` and `data/sp500.json`.
`data/sp500.json` is a list of companies that are in the S&P500 index.
`accesstoken/alphavantageapikey.json` holds the keys for authenticating
to the API. One needs to get the values from the support of Alpha
Vantage[^10]. An example Alpha Vantage access token JSON file looks like
the following.

    {
        "apikey": "NDIFD7VBDNVUZEGDI335"
    }

#### Helpers

The other scripts in `crawling` are helpers to support the crawling. The
script `mergesp500.py` merges two S&P500 lists, which because the S&P500
index is dynamic and changes over time. `sp500tojson.py` takes a list of
S&P500 that are not in a JSON format and converts it into the JSON
format.

### Database

In the directory `database` are all the scripts that keep the database
cleaned and consistent.

The script `adddate.py` adds a date attribute to each tweet and idea. To
add a date, the script parses the `createdat` string of the tweet or
idea and converts it into the correct data type for MongoDB. This
functionality is built into the crawling scripts and should not be
necessary anymore.

The `checkcompanies.py` script looks into databases and checks whether
there is a collection for each company in the S&P500 index. The
databases to check are defined in the variable `databasenames`. An
example for list of databases is the following.

        database_names = ["stocktwitsdb", "twitterdb"]

The script `fixdateattribute.py` checks if the attribute `date` exists
and whether it is the correct data type. In addition, the wrong dates
are corrected so that the database is consistent again. The argument
`–threading` start the script with multiple threads and speeds up the
verification and correction.

To find out if there are duplicates in the databases, we use the script
`checkduplicates.py`. If duplicates should be deleted, then the script
must be called with the `–delete` argument.

        python3 check_duplicates.py --delete

The script `cleanstockpricedb.py` cleans up the stock price database.
The cleanup consists of one check. For each company and day, the script
checks if the attribute `date` exits. If it does not exist the whole day
gets deleted.

For faster queries, there is the script `createindexdate.py`. For each
database in the list of variable `databasenames` an index on the
attribute date gets created. Afterwards, if queries are done that
include the date attribute, they will be faster.

To reformat the entries in the stock price database, there is the script
`reformatstockprice.py`. The script takes existing entries and reformats
those so that it is easier for us to work with. This functionality is
included in the crawling of stock prices and should not be necessary
anymore.

### Preprocessing

In `preprocessing` are all the scripts that take the raw data crawled
from Twitter, Stocktwits, etc. and creates training datasets. The
training datasets are needed for the training of the neural network.

#### Sentiment only

The script `createtrainingsamples.py` creates a dataset with days as
samples. Each day holds a list of sentiments and a relative price
difference. The list of sentiments is constructed by using the sentiment
analysis of TextBlob[^11]. The source for the sentiment analysis is the
text of tweets and the body of ideas. We get the relative price
difference by crawling the opening price of today and yesterday from the
stock price database. The days are stored in the `learning` database for
each company individually. A drawing of the day is shown in figure
_dataset_sentiment_only_.

    ┌─────────────────────────────────┐
    │                                 │
    │ ┌───────────┐ ┌───────────┐     │        ┌──────────────────┐
    │ │ sentiment │ │ sentiment │ ... │ ─────► │ price difference │
    │ └───────────┘ └───────────┘     │        └──────────────────┘
    │                                 │
    └─────────────────────────────────┘

#### Twitter three

The script `createtwitterthree.py` creates a dataset with days as
samples. Each day holds a list of tuples sentiment, followers, retweets.
Additionally, each day holds a relative price difference. The sentiments
are evaluated by using the sentiment analysis of TextBlob[^12]. The
source for the sentiment analysis is the text of tweets. We get the
relative price difference by crawling the opening price of today and
yesterday from the stock price database. The days are stored in the
`twitterthree` database for each company individually. The
`twitterthree` database only uses the `twitterdb` database as the source
because the feature set between tweets and ideas is different. A
visualisation of the day is shown in figure _dataset_twitter_three_.

    ┌─────────────────────────────────┐
    │                                 │
    │ ┌───────────┐ ┌───────────┐     │
    │ │ sentiment │ │ sentiment │     │
    │ │           │ │           │     │        ┌──────────────────┐
    │ │ followers │ │ followers │ ... │ ─────► │ price difference │
    │ │           │ │           │     │        └──────────────────┘
    │ │ retweets  │ │ retweets  │     │
    │ └───────────┘ └───────────┘     │
    │                                 │
    └─────────────────────────────────┘


### Ava

The script `createtrainingdataset.py` creates a dataset with days as
samples. Each day holds a list of tweets, ideas and company information.
Additionally, each day holds a relative price difference. The sentiments
are evaluated by using the sentiment analysis of TextBlob[^13]. We get
the relative price difference by crawling the opening price of today and
yesterday from the stock price database. The days are stored in the
`trainingdatasetdb` database in the collection `Ava`. To speed up
generating of the dataset, the script can be called with the
`–threading` argument. Because the input features for the training must
be floats, the script `getindustrysector.py` maps the sectors and
industries from strings to floats. A visualisation of the day is shown
in figure _dataset_Ava_.

    ┌────────────────────────────────────────┐
    │                                        │
    │              ┌───────────┐             │
    │              │ sentiment │             │
    │              │           │             │
    │              │ followers │             │
    │              │           │             │
    │              │ retweets  │             │
    │       tweets │           │             │
    │              │ favorites │             │
    │              │           │             │
    │              │ ...       │             │
    │              │           │             │
    │              └───────────┘             │
    │                                        │
    │              ┌────────────┐            │
    │              │            │            │
    │              │ sentiment  │            │
    │              │            │            │
    │              │ followers  │            │
    │              │            │            │        ┌──────────────────┐
    │        ideas │ likes      │            │ ─────► │ price difference │
    │              │            │            │        └──────────────────┘
    │              │ like_count │            │
    │              │            │            │
    │              │ ...        │            │
    │              │            │            │
    │              └────────────┘            │
    │                                        │
    │              ┌───────────────────────┐ │
    │              │                       │ │
    │              │ book value            │ │
    │              │                       │ │
    │              │ EBITDA                │ │
    │              │                       │ │
    │ company info │ dividend              │ │
    │              │                       │ │
    │              │ market capitalisation │ │
    │              │                       │ │
    │              │ ...                   │ │
    │              │                       │ │
    │              └───────────────────────┘ │
    │                                        │
    └────────────────────────────────────────┘


### Training

To predict the relative price difference on new data, we must train a
model. The model is a neural network consisting of recurrent neural
networks and fully connected or dense layers.

#### Ava

The dataset `Ava` is stored in the MongoDB. To save time and only create
the dataset once in the correct Tensorflow[^14] format, there is the
script `createtfdataset.py`. When the script finished, there will be a
directory `dataset/Ava` holding the Tensorflow dataset.
`createtfdataset.py` must be executed before `startblockstudy.sh`.

To do training with the Ava dataset, we must run the script
`trainingblocks.py`. During the training, a parameters search is
executed. In the parameter search, the best parameters for learning
rate, hidden dimensionality and batch size are sought to be found. Since
there are many possible arguments, there is the shell script
`startblockstudy.sh` for which the arguments are already set. The
arguments can be changed. To run the training, execute the following
command.

        ./start_block_study.sh

After the run, there will be the directory `checkpoint` that stores all
checkpoints for each model during the parameters search. In the
directory `tensorboardlog` there will be all training stats which can be
viewed with Tensorboard[^15]. Inside the directory will be the file
`teststats.txt` which holds the training stats such as $R^2$, mean
squared error, etc. In the `training` directory is, after the training,
the file `studyargs.txt` which logs the arguments passed to the script.
For the parameter search, we use Optuna[^16]. The findings of Optuna are
in the file `study.csv`. It has a table with the loss and parameters
chosen for a specific study.

#### Twitter Three

To do training with the `twitterthree` dataset, we must run the script
`training.py`. During the training, a parameters search is executed. In
the parameter search, the best parameters for learning rate, hidden
dimensionality and batch size are sought to be found. Since there are
many possible arguments, there is the shell script `startstudy.sh` for
which the arguments are already set. The arguments can be changed. To
run the training, execute the following command.

        ./start_study.sh

After the run, there will be the directory `checkpoint` that stores all
checkpoints for each model during the parameters search. In the
directory `tensorboardlog` there will be all training stats which can be
viewed with Tensorboard[^17]. Inside the directory will be the file
`teststats.txt` which holds the training stats such as $R^2$, mean
squared error, etc. In the `training` directory is, after the training,
the file `studyargs.txt` which logs the arguments passed to the script.
For the parameter search, we use Optuna[^18]. The findings of Optuna are
in the file `study.csv`. It has a table with the loss and parameters
chosen for a specific study.

#### Regression

To get a basic idea between sentiment and the relative stock price
difference, we do a regression with the mean sentiment during one day
and company. To run `regression.py`, one must run `sentiment.py` in th
directory `stats` first. That is because `sentiment.py` generates files
that `regression.py` needs as input. The script generates a JSON file
`output/regression.json` that holds the stats. The regression happens
individually for each company and each data source Twitter and
Stocktwits. We use ridge, bayesian and SVM regression. The stats include
the coefficients, standard error, t-value, p-value and $R^2$.

### Stats

#### Sampling

To see how a document in a dataset looks like, we have a script that
samples ten entries from the dataset. The samples will be stored in the
directory `output`. The output files are in the JSON file format.

Executing the script `sampletweets.py` samples ten tweets and ten ideas.
The company can be chosen by setting the variable `company`. Currently,
the company is set to *AAPL*.

The script `samplecompanyinfo.py` samples the company information for
ten companies. The ten companies are selected randomly.

To get samples from the Ava dataset, one must execute the script
`sampledates.py`. After executing, there are going to be ten days with
the price difference, tweets, etc.

#### Sentiment

After creating the dataset Ava, we have companies, days and the
sentiment. To generate a table for each company with the day, sentiment
and other stats, run `sentiment.py`. In the `output` directory will be
comma-separated value files for each company. The tables include the
following.

-   tweets sentiment polarity sum

-   tweets sentiment subjectivity sum

-   tweets sentiment polarity mean

-   tweets sentiment subjectivity mean

-   tweets count

-   ideas sentiment polarity sum

-   ideas sentiment subjectivity sum

-   ideas sentiment polarity mean

-   ideas sentiment subjectivity mean

-   ideas count

-   price difference

#### Regression

The script `plotregression.py` draws a graph that shows the result from
`sentiment.py`. That implies that the script `sentiment.py` must be run
before. After the execution, there will be two graphs in the directory
`output`. Both show the mean sentiment of all companies on the x-axis
and the relative price difference on the y-axis. But one graph shows the
sentiment for Twitter and the other graph shows the sentiment for
Stocktwits.

#### Count

To get stats about the databases, we count entries and filter entries
based on certain attributes.

The script `countdatasetentries.py` uses the dataset with only a list of
sentiments. It counts for each company the number of tweets and number
of tweets with sentiment equal to zero. For all companies combined, the
statistics include the number of tweets, number of tweets with sentiment
equal to zero, number of days and number of companies. Additionally, the
script draws a graph with the tweet distribution per hour for each
company. The graph shows at which hour the people are most active. The
output of the script will be in the directory `output`.

When executing `counttweetsday.py`, it counts the tweets per day. The
script does it for each database `twitterdb` and `stocktwitsdb` and for
each company in S&P500. After finishing, there will be a csv table for
each company in the `output` directory. To speed up the count, start the
script with the `–threading` arguments, such as the following.

        python3 count_tweets_day.py --threading

The script `counttweetscompany.py` uses the output of
`counttweetsday.py`. It sums up the number of tweets and it sums up the
number of ideas. So that we have the total number of tweets and ideas.

### Utilities

In the directory `util` are scripts that are needed by most of the other
submodules. `readsp500.py` reads the JSON file with the S&P500 companies
and returns a Python list. The file `threads.py` helps to start scripts
with threading. It is mostly needed when one starts a script with the
`–threading` argument.

## S&P500 index

In the following table are the symbols of companies we crawl tweets and
ideas for.

  ------- ------- ------- ------ ------ ------
  A       CELG    F       KHC    OMC    TIF
  AAL     CERN    FANG    KIM    ORCL   TJX
  AAP     CF      FAST    KLAC   ORLY   TMO
  AAPL    CFG     FB      KMB    OTIS   TMUS
  ABBV    CHD     FBHS    KMI    OXY    TPR
  ABC     CHK     FCX     KMX    PAYC   TRIP
  ABMD    CHRW    FDX     KO     PAYX   TRMB
  ABT     CHTR    FE      KR     PBCT   TROW
  ACN     CI      FFIV    KSS    PCAR   TRV
  ADBE    CINF    FIS     KSU    PCG    TSCO
  ADI     CL      FISV    L      PCLN   TSLA
  ADM     CLX     FITB    LB     PDCO   TSN
  ADP     CMA     FL      LDOS   PEAK   TSS
  ADS     CMCSA   FLIR    LEG    PEAK   TT
  ADSK    CME     FLR     LEN    PEG    TTWO
  AEE     CMG     FLS     LH     PEP    TWTR
  AEP     CMI     FLT     LHX    PFE    TWX
  AES     CMS     FMC     LIN    PFG    TXN
  AFL     CNC     FOX     LKQ    PG     TXT
  AGN     CNP     FOXA    LLL    PGR    TYL
  AIG     COF     FRC     LLY    PH     UA
  AIV     COG     FRT     LMT    PHM    UAA
  AIZ     COH     FTI     LNC    PKG    UAL
  AJG     COL     FTNT    LNT    PKI    UDR
  AKAM    COO     FTV     LOW    PLD    UHS
  ALB     COP     GD      LRCX   PM     ULTA
  ALGN    COST    GE      LUK    PNC    UNH
  ALK     COTY    GGP     LUMN   PNR    UNM
  ALL     CPB     GILD    LUV    PNW    UNP
  ALLE    CPRI    GIS     LVLT   POOL   UPS
  ALXN    CPRT    GL      LVS    PPG    URI
  AMAT    CRM     GL      LW     PPL    USB
  AMCR    CSCO    GLW     LYB    PRGO   UTX
  AMD     CSRA    GM      LYV    PRU    V
  AME     CSX     GOOG    M      PSA    VAR
  AMG     CTAS    GOOGL   MA     PSX    VFC
  AMGN    CTLT    GPC     MAA    PVH    VIAB
  AMP     CTSH    GPN     MAC    PWR    VIAC
  AMT     CTVA    GPS     MAR    PX     VLO
  AMZN    CTXS    GRMN    MAS    PXD    VMC
  ANDV    CVS     GS      MAT    PYPL   VNO
  ANET    CVX     GT      MCD    QCOM   VNT
  ANSS    CXO     GWW     MCHP   QRVO   VRSK
  ANTM    D       HAL     MCK    RCL    VRSN
  AON     DAL     HAS     MCO    RE     VRTX
  AOS     DD      HBAN    MDLZ   REG    VTR
  APA     DD      HBI     MDT    REGN   VTRS
  APC     DE      HCA     MET    RF     VZ
  APD     DFS     HCN     MGM    RHI    WAB
  APH     DG      HD      MHK    RHT    WAT
  APTV    DGX     HES     MKC    RJF    WBA
  ARE     DHI     HFC     MKTX   RL     WDC
  ARNC    DHR     HIG     MLM    RMD    WEC
  ATO     DIS     HII     MMC    ROK    WELL
  ATVI    DISCA   HLT     MMM    ROL    WFC
  AVB     DISCK   HOG     MNST   ROP    WHR
  AVGO    DISH    HOLX    MO     ROST   WLTW
  AVY     DLPH    HON     MON    RRC    WM
  AWK     DLR     HP      MOS    RSG    WMB
  AXP     DLTR    HPE     MPC    RTN    WMT
  AYI     DOV     HPQ     MRK    RTX    WRB
  AZO     DOW     HRB     MRO    SBAC   WRK
  BA      DPS     HRL     MS     SBUX   WST
  BAC     DPZ     HSIC    MSCI   SCG    WU
  BAX     DRE     HST     MSFT   SCHW   WY
  BBY     DRI     HSY     MSI    SEE    WYN
  BCR     DTE     HUM     MTB    SHW    WYNN
  BDX     DUK     HWM     MTD    SIG    XEC
  BEN     DVA     IBM     MU     SIVB   XEL
  BF.B    DVN     ICE     MXIM   SJM    XL
  BHF     DXC     IDXX    MYL    SLB    XLNX
  BIIB    DXCM    IEX     NAVI   SLG    XOM
  BIO     EA      IFF     NBL    SNA    XRAY
  BK      EBAY    ILMN    NCLH   SNI    XRX
  BKNG    ECL     INCY    NDAQ   SNPS   XYL
  BKR     ED      INFO    NEE    SO     YUM
  BKR     EFX     INTC    NEM    SPG    ZBH
  BLK     EIX     INTU    NFLX   SPGI   ZBRA
  BLL     EL      IP      NFX    SPLS   ZION
  BMY     EMN     IPG     NI     SRCL   ZTS
  BR      EMR     IPGP    NKE    SRE    
  BRK.B   ENPH    IQV     NLOK   STE    
  BSX     EOG     IR      NLOK   STI    
  BWA     EQIX    IRM     NLSN   STT    
  BXP     EQR     ISRG    NOC    STX    
  C       EQT     IT      NOV    STZ    
  CA      ES      ITW     NOW    SWK    
  CAG     ESRX    IVZ     NRG    SWKS   
  CAH     ESS     J       NSC    SYF    
  CARR    ETFC    J       NTAP   SYK    
  CAT     ETN     JBHT    NTRS   SYY    
  CB      ETR     JCI     NUE    T      
  CBG     ETSY    JKHY    NVDA   TAP    
  CBOE    EVHC    JNJ     NVR    TDG    
  CBRE    EVRG    JNPR    NWL    TDY    
  CCI     EW      JPM     NWS    TEL    
  CCL     EXC     JWN     NWSA   TER    
  CDNS    EXPD    K       O      TFC    
  CDW     EXPE    KEY     ODFL   TFX    
  CE      EXR     KEYS    OKE    TGT    
  ------- ------- ------- ------ ------ ------

[^1]: <https://github.com/marwage/stock_prediction>

[^2]: <https://docs.mongodb.com/manual/administration/install-community>

[^3]: <https://www.tensorflow.org/api_docs/python/tf>

[^4]: <https://pymongo.readthedocs.io/en/stable/index.html>

[^5]: <https://developer.twitter.com/en/docs/twitter-api/v1>

[^6]: <https://developer.twitter.com/en>

[^7]: <https://developer.twitter.com/en>

[^8]: <https://developer.twitter.com/en/docs/twitter-api/early-access>

[^9]: <https://www.alphavantage.co/documentation/>

[^10]: <https://www.alphavantage.co/support/#api-key>

[^11]: <https://textblob.readthedocs.io/en/dev/>

[^12]: <https://textblob.readthedocs.io/en/dev/>

[^13]: <https://textblob.readthedocs.io/en/dev/>

[^14]: <https://www.tensorflow.org/api_docs/python/tf>

[^15]: <https://www.tensorflow.org/tensorboard/>

[^16]: <https://optuna.org>

[^17]: <https://www.tensorflow.org/tensorboard/>

[^18]: <https://optuna.org>
