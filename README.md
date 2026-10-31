# 📊 Web Log Intelligence and Anomaly Detection Using Hadoop and Machine Learning

[Python](https://img.shields.io/badge/Python-3.x-blue)
[Java](https://img.shields.io/badge/Java-8-orange)
[Hadoop](https://img.shields.io/badge/Apache%20Hadoop-3.2.4-yellow)
[MongoDB](https://img.shields.io/badge/MongoDB-8.x-green) [Machine
Learning](https://img.shields.io/badge/Machine%20Learning-Isolation%20Forest-purple)
[Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)

## 📌 Project Overview

**Web Log Intelligence** is a Big Data Analytics and Machine Learning
project designed to analyze large volumes of web server access logs,
identify unusual client behavior, and generate alerts for potentially
suspicious activities.

Web servers continuously generate access logs containing information
such as client IP addresses, requested resources, timestamps, and HTTP
response status codes. Manually analyzing millions of log records is
time-consuming and inefficient.

This project integrates **Apache Hadoop, MapReduce, Python, Machine
Learning, MongoDB, and Streamlit** to automate historical web log
analysis and demonstrate simulated real-time monitoring.

The project consists of two major components:

1.  **Historical Web Log Analysis:** Processes NASA HTTP access logs
    using Hadoop MapReduce, performs feature engineering, and applies
    the Isolation Forest algorithm to identify potentially anomalous
    clients.
2.  **Simulated Real-Time Monitoring:** Generates normal and anomalous
    web traffic, monitors incoming log entries, detects suspicious
    request patterns, and displays alerts through an interactive
    dashboard.

------------------------------------------------------------------------

## 🎯 Problem Statement

Web servers generate enormous amounts of access log data, making manual
analysis difficult and time-consuming.

Identifying unusual client behavior, excessive request rates, and HTTP
errors from large log datasets requires an efficient and scalable
solution.

The objective is to develop a system that processes large volumes of web
server logs, extracts meaningful client-level information, detects
potentially anomalous behavior using machine learning, and presents the
results through an interactive dashboard.

------------------------------------------------------------------------

## 🎯 Project Objectives

-   Process large-scale web server logs using Hadoop MapReduce.
-   Analyze HTTP response status codes.
-   Calculate request statistics for individual clients.
-   Identify HTTP errors such as 403, 404, 500, and 501.
-   Perform feature engineering to extract meaningful client-level
    features.
-   Apply Isolation Forest for unsupervised anomaly detection.
-   Store analytical results in MongoDB.
-   Develop an interactive dashboard using Streamlit.
-   Implement simulated real-time traffic monitoring.
-   Generate alerts for suspicious request rates and HTTP error
    patterns.

------------------------------------------------------------------------

## ✨ Key Features

### 1. Big Data Processing Using Hadoop

-   Processes historical NASA HTTP access logs.
-   Uses Hadoop Distributed File System (HDFS) for distributed storage.
-   Implements Java-based MapReduce programs.
-   Calculates HTTP status code frequencies.
-   Analyzes individual client request counts.

### 2. HTTP Error Analysis

Identifies selected HTTP error responses:

  HTTP Status   Description
  ------------- -----------------------
  403           Forbidden
  404           Not Found
  500           Internal Server Error
  501           Not Implemented

### 3. Feature Engineering

Extracts client-level statistical features from processed log data.

Features include:

-   Client
-   Total Requests
-   HTTP 403 Count
-   HTTP 404 Count
-   HTTP 500 Count
-   HTTP 501 Count
-   Total Errors
-   Error Rate

### 4. Machine Learning-Based Anomaly Detection

-   Implements the Isolation Forest algorithm.
-   Uses unsupervised machine learning.
-   Identifies unusual client behavior.
-   Classifies clients as Normal or Potential Anomaly.
-   Generates anomaly scores.

### 5. MongoDB Integration

Stores analytical results in MongoDB.

**Database:** `WebLogIntelligence`

**Collections:**

-   `client_statistics`
-   `anomaly_results`
-   `top_clients`

The dashboard retrieves historical analytical results directly from
MongoDB, with CSV fallback support.

### 6. Interactive Streamlit Dashboard

The dashboard contains three main sections.

**Overview**

-   Total unique clients.
-   Total requests.
-   Selected HTTP errors.
-   Potential anomalies.
-   Top clients by request volume.
-   Anomaly classification charts.

**Anomaly Details**

-   Search clients using IP addresses or hostnames.
-   View client request statistics.
-   Analyze HTTP error breakdowns.
-   View anomaly classifications and scores.
-   Inspect matching real-time alerts.

**Live Monitoring**

-   Start and stop the traffic simulator.
-   Select Normal or Anomaly traffic modes.
-   Monitor incoming log entries.
-   View request-rate alerts.
-   View HTTP-error alerts.
-   Visualize monitoring metrics.
-   Download recorded alerts.

------------------------------------------------------------------------

## 🏗️ System Architecture

### Historical Log Analysis Pipeline

``` text
           NASA HTTP Access Logs
                    |
                    v
                Hadoop HDFS
                    |
                    v
             Hadoop MapReduce
                    |
          +---------+---------+
          |                   |
          v                   v
     HTTP Status         Client Request
      Analysis              Analysis
          |                   |
          +---------+---------+
                    |
                    v
             Feature Engineering
                    |
                    v
                ML Features
                    |
                    v
             Isolation Forest
                    |
                    v
              Anomaly Results
                    |
                    v
                  MongoDB
                    |
                    v
             Streamlit Dashboard
```

### Simulated Real-Time Monitoring Pipeline

``` text
              Traffic Simulator
               /            \
              v              v
         Normal Mode      Anomaly Mode
              \              /
               v            v
                Live Log File
                     |
                     v
              Real-Time Monitor
                     |
              +------+------+
              |             |
              v             v
         Request-Rate   HTTP-Error
            Alerts        Alerts
              |             |
              +------+------+
                     |
                     v
                  Alert CSV
                     |
                     v
             Streamlit Dashboard
```

**Note:** Historical machine learning analysis and simulated real-time
monitoring are separate pipelines. The current real-time monitor uses
threshold-based detection rules rather than applying Isolation Forest to
every incoming request.

------------------------------------------------------------------------

## 🛠️ Technologies Used

  Technology            Purpose
  --------------------- -------------------------------------------
  Java                  Hadoop MapReduce implementation
  Apache Hadoop 3.2.4   Big data processing
  HDFS                  Distributed file storage
  Python                Data processing and machine learning
  Pandas                Data manipulation and feature engineering
  NumPy                 Numerical operations
  Scikit-learn          Isolation Forest implementation
  Matplotlib            Data visualization
  MongoDB               NoSQL database
  PyMongo               MongoDB connectivity
  Streamlit             Interactive dashboard
  PowerShell            Windows execution environment

------------------------------------------------------------------------

## 📂 Project Structure

``` text
web-log-project/
│
├── dashboard/
│   └── app.py
│
├── ml/
│   ├── top_clients.py
│   ├── feature_engineering.py
│   └── anomaly_detection.py
│
├── realtime/
│   ├── live_traffic_simulator.py
│   ├── log_generator.py
│   ├── realtime_monitor.py
│   ├── input/
│   └── alerts/
│
├── src/
│   ├── WebLogAnalyzer.java
│   ├── ClientRequestAnalyzer.java
│   └── HTTPErrorAnalyzer.java
│
├── client_requests.txt
├── http_errors.txt
├── .gitignore
└── README.md
```

*Note: Generated outputs, datasets, and additional local files may not
be included in the GitHub repository.*

------------------------------------------------------------------------

## ⚙️ System Requirements

Before running the project, install the following:

  Requirement        Version
  ------------------ --------------------
  Operating System   Windows 10/11
  Python             3.x
  Java JDK           Java 8
  Apache Hadoop      3.2.4
  MongoDB            8.x
  Streamlit          Compatible version
  PyMongo            Compatible version

The original development environment used Windows 11, Java 8, Hadoop
3.2.4, and Python 3.14.

------------------------------------------------------------------------

## 📥 Installation and Setup

### Step 1: Clone the Repository

``` bash
git clone https://github.com/nagendraveer/web-log-project.git
```

Replace the repository URL with the actual clone URL from GitHub.

Navigate to the project directory:

``` bash
cd web-log-project
```

### Step 2: Install Python Dependencies

Create a virtual environment:

``` bash
python -m venv venv
```

Activate it on Windows:

``` powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

``` bash
pip install pandas numpy scikit-learn matplotlib streamlit pymongo
```

### Step 3: Configure Java and Hadoop

Configure the following environment variables according to your
installation directories:

``` text
JAVA_HOME
HADOOP_HOME
```

Add the Java and Hadoop `bin` and `sbin` directories to your system
PATH.

Verify the installations:

``` bash
java -version
hadoop version
```

### Step 4: Start MongoDB

Make sure the MongoDB service is running.

Open MongoDB Shell:

``` bash
mongosh
```

Select the project database:

``` javascript
use WebLogIntelligence
```

The required collections must be populated with the historical
analytical results before using the MongoDB-powered dashboard.

### Step 5: Run the Streamlit Dashboard

From the project root directory, execute:

``` bash
streamlit run dashboard/app.py
```

Open the application in your browser:

``` text
http://localhost:8501
```

------------------------------------------------------------------------

## 🚀 Project Execution Workflow

### Phase 1: Historical Log Processing

1.  Obtain the NASA HTTP access log dataset.
2.  Place the input file in the configured data directory.
3.  Upload the dataset to Hadoop HDFS.
4.  Execute the Java MapReduce programs.
5.  Generate HTTP status statistics.
6.  Generate client request statistics.
7.  Generate HTTP error statistics.

### Phase 2: Feature Engineering

Execute:

``` bash
python ml/feature_engineering.py
```

This generates the client-level machine learning features.

Output:

``` text
output/ml_features.csv
```

### Phase 3: Anomaly Detection

Execute:

``` bash
python ml/anomaly_detection.py
```

The Isolation Forest algorithm analyzes the extracted features and
generates anomaly classifications.

Outputs:

``` text
output/anomaly_results.csv
output/anomaly_detection.png
```

### Phase 4: MongoDB Integration

Import the generated analytical datasets into their respective MongoDB
collections.

The collections store:

-   Client statistics.
-   Anomaly detection results.
-   Top-client records.

Avoid importing the same CSV multiple times without clearing or updating
the existing collection, as this can create duplicate documents.

### Phase 5: Simulated Real-Time Monitoring

Start the monitoring process:

``` bash
python realtime/realtime_monitor.py
```

Open another terminal and start the traffic simulator:

``` bash
python realtime/live_traffic_simulator.py
```

Select the desired mode:

-   `1` -- Normal Traffic
-   `2` -- Anomaly Traffic
-   `3` -- Exit

The simulator generates Apache-style log entries and appends them to the
live input file.

The monitoring process reads incoming records and generates alerts when
configured thresholds are reached.

The simulator can also be controlled through the Streamlit dashboard.

**Important:** Keep `realtime_monitor.py` running independently while
using the dashboard simulator controls.

------------------------------------------------------------------------

## 🧠 Machine Learning Methodology

### Algorithm: Isolation Forest

Isolation Forest is an unsupervised machine learning algorithm used to
identify unusual observations in datasets.

It works by randomly selecting features and split values to isolate
individual observations.

Unusual observations generally require fewer splits to isolate compared
to normal observations.

### Model Configuration

The project uses:

``` python
contamination=0.01
```

The contamination parameter specifies an expected proportion of
anomalies in the dataset.

### Input Features

-   Total Requests
-   HTTP 403 Count
-   HTTP 404 Count
-   HTTP 500 Count
-   HTTP 501 Count
-   Total Errors
-   Error Rate

### Model Output

-   Anomaly Score
-   Anomaly Status

Possible classifications:

-   Normal
-   Potential Anomaly

------------------------------------------------------------------------

## 📊 Project Results

The historical NASA HTTP access log analysis produced the following
results.

### HTTP Status Code Distribution

  HTTP Status   Count
  ------------- -----------
  200           1,698,491
  302           46,545
  304           132,626
  403           54
  404           10,711
  500           62
  501           14

### Client-Level Analysis

  Metric                  Result
  ----------------------- -----------
  Total Client Records    81,982
  Total Client Requests   1,891,700
  Selected HTTP Errors    10,961

### Machine Learning Results

  Classification      Number of Clients
  ------------------- -------------------
  Normal              81,218
  Potential Anomaly   764
  Total               81,982

### MongoDB Storage Results

  Collection          Documents
  ------------------- -----------
  client_statistics   81,982
  anomaly_results     81,982
  top_clients         20

These results demonstrate the integration of big data processing,
machine learning, and database storage.

------------------------------------------------------------------------

## 🗄️ MongoDB Queries

The following queries can be executed using MongoDB Shell.

### Select the Database

``` javascript
use WebLogIntelligence
```

### Display Collections

``` javascript
show collections
```

### Display Client Records

``` javascript
db.client_statistics.find().limit(5)
```

### Count Total Clients

``` javascript
db.client_statistics.countDocuments()
```

### Find Clients with HTTP Errors

``` javascript
db.client_statistics.find({
    Total_Errors: { $gt: 0 }
}).limit(10)
```

### Find Potential Anomalies

``` javascript
db.anomaly_results.find({
    Anomaly_Status: "Potential Anomaly"
}).limit(10)
```

### Count Potential Anomalies

``` javascript
db.anomaly_results.countDocuments({
    Anomaly_Status: "Potential Anomaly"
})
```

### Display Top Clients

``` javascript
db.top_clients.find().limit(10)
```

------------------------------------------------------------------------

## 🚨 Real-Time Anomaly Detection

The simulated monitoring system uses two primary threshold-based
detection rules.

### 1. Request-Rate Detection

Detects clients generating at least 30 requests within a 10-second
observation window.

### 2. HTTP Error Detection

Detects clients generating at least 10 selected HTTP errors.

Selected HTTP codes:

-   403
-   404
-   500
-   501

### Alert Cooldown

A 15-second cooldown is configured per client to prevent alerts from
being generated on every incoming request.

The monitoring system records alerts and metrics in CSV files.

**Note:** An alert indicates potentially unusual activity. It does not
necessarily represent a confirmed security attack.

------------------------------------------------------------------------

## 📸 Dashboard Screenshots

Dashboard screenshots can be added here to demonstrate the application.

Suggested screenshots:

1.  Overview Dashboard
2.  Anomaly Details Page
3.  Live Monitoring -- Normal Traffic
4.  Live Monitoring -- Anomaly Traffic
5.  MongoDB Query Results

------------------------------------------------------------------------

## 🔮 Future Enhancements

-   Integration with live web server access logs.
-   Real-time log streaming using Apache Kafka.
-   Integration of machine learning predictions into real-time
    monitoring.
-   Advanced deep learning-based anomaly detection.
-   Email and SMS alert notifications.
-   User authentication and role-based access control.
-   Docker-based application deployment.
-   Kubernetes-based orchestration.
-   Cloud deployment and scalable infrastructure.
-   Advanced anomaly visualization and reporting.

------------------------------------------------------------------------

## ⚠️ Limitations

-   Historical analysis uses NASA HTTP access logs from July 1995.
-   Real-time traffic is currently simulated rather than collected from
    a production web server.
-   Real-time alerts use threshold-based detection rules.
-   Isolation Forest classifications represent potential anomalies, not
    confirmed malicious activity.
-   The current implementation is designed as an academic project and
    demonstration platform.

------------------------------------------------------------------------

## 📚 Learning Outcomes

Through this project, we explored:

-   Big Data Processing using Hadoop MapReduce.
-   Distributed File Storage using HDFS.
-   Java-based MapReduce programming.
-   Data preprocessing and feature engineering using Python.
-   Unsupervised Machine Learning using Isolation Forest.
-   NoSQL database management using MongoDB.
-   Database integration using PyMongo.
-   Interactive dashboard development using Streamlit.
-   Simulated real-time log monitoring and alert generation.

------------------------------------------------------------------------

## 🤝 Contribution

Contributions, suggestions, and improvements are welcome.

To contribute:

1.  Fork the repository.
2.  Create a new feature branch.
3.  Make your changes.
4.  Commit your changes.
5.  Submit a pull request.

------------------------------------------------------------------------

## 📜 License

This project is developed for academic and educational purposes.

A license has not yet been specified. An appropriate open-source license
can be added if reuse and redistribution are intended.

------------------------------------------------------------------------

## 🙏 Acknowledgements

We acknowledge the NASA HTTP access log dataset and the open-source
communities behind Apache Hadoop, Python, Scikit-learn, MongoDB, and
Streamlit.

------------------------------------------------------------------------

**If you find this project useful, consider giving the repository a ⭐
on GitHub!**
