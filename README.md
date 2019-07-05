# Wise Log
Surfacing investment opportunities

<!-- TOC -->

- [Wise Log](#wise-log)
    - [1. PROJECT ARTIFACTS](#1-project-artifacts)
    - [2. INTRODUCTION](#2-introduction)
    - [3. DATASETS](#3-datasets)
    - [4. ARCHITECTURE](#4-architecture)
        - [4.1 Environment Setup](#41-environment-setup)
        - [4.2 Data Ingestion](#42-data-ingestion)
        - [4.3 Batch Processing](#43-batch-processing)
        - [4.4 User Interface](#44-user-interface)
    - [5. ENGINEERING CHALLENGES](#5-engineering-challenges)

<!-- /TOC -->


## 1. PROJECT ARTIFACTS 
* [Demostration URL](wiselog.club)
* [Presentation Slide](bit.ly/wiselog_demo)
* Demostration vedio
  
## 2. INTRODUCTION

## 3. DATASETS
[EDGAR Log File Data Set](https://www.sec.gov/dera/data/edgar-log-file-data-set.html)   
EDGAR, the Electronic Data Gathering, Analysis, and Retrieval system, performs automated collection, validation, indexing, acceptance, and forwarding of submissions by companies and others who are required by law to file forms with the U.S. Securities and Exchange Commission (SEC). In 1984, EDGAR began collecting electronic documents to help investors get information.

The EDGAR Log File Data Set contains information in CSV format extracted from Apache log files that record and store user access statistics for the SEC.gov website. The dataset provides information on website traffic for EDGAR filings, which records the log of users’ IP address, requests of company’s documents on the SEC website, covering the period from February 14, 2003 to June 30, 2017. 

With the EDGAR logs, we are able to gain insights of when and how many people requested for specific companies' financial documents as a reference of their investment opportunities on stock market in different areas. However, only the data from January 1, 2016 to December 31, 2016 will be used (around 3GB per day, ~1TB in total) in this project.
## 4. ARCHITECTURE
![Pipeline](./img/workflow.png)
### 4.1 Environment Setup
 For environment configuration and tools setup, please refer to [SETUP.md](./SETUP.md).
### 4.2 Data Ingestion
* Amazon AWS S3      
  AWS S3 is a way for long term storage. The data file was first downloaded and uncompressed to an EC2 instance. Since the every single uncompressed file is almost 3GB, I then gzipped it and stored it in AWS S3 bucket, which compressed into only ~170GB in total and then removed all files in EC2 instance. All the details were located in **ingestion** folder.
### 4.3 Batch Processing
* Apache Spark      
  
* PostgresSQL
### 4.4 User Interface
## 5. ENGINEERING CHALLENGES