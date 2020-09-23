#!/usr/bin/env python
# coding: utf-8

# # Import libraries 

# In[1]:


import requests
from bs4 import BeautifulSoup
from itertools import cycle
import csv 


# # Get Proxies 
def getProxies(inURL):
    
    page = requests.get(inURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    terms = soup.find_all('tr')
    IPs = []

    for x in range(len(terms)):  
        
        term = str(terms[x])        
        
        if '<tr><td>' in str(terms[x]):
            pos1 = term.find('d>') + 2
            pos2 = term.find('</td>')

            pos3 = term.find('</td><td>') + 9
            pos4 = term.find('</td><td>US<')
            
            IP = term[pos1:pos2]
            port = term[pos3:pos4]
            
            if '.' in IP and len(port) < 6:
                IPs.append(IP + ":" + port)
                #print(IP + ":" + port)

    return IPs 


#Cycle through the proxies and get one to use 
proxyURL = "https://www.us-proxy.org/"
pxs = getProxies(proxyURL)
proxyPool = cycle(pxs)


def extractJobListings(url):
    
    page = requests.get(url, proxies = {"http": next(proxyPool)})
    soup = BeautifulSoup(page.text, 'html.parser')

    jobs = soup.find(id='resultsCol')
    job_elems = jobs.find_all('div', class_='jobsearch-SerpJobCard')
    
    #For Excel File 
    rows = []

    for desc in job_elems:

        #Extract only the job title 
        title = desc.find('h2', class_='title').text 

        #Get rid of uncessary whitespace and the word 'new'
        title = title.replace('new', '').replace('\n', '') 

        #Company name 
        company = desc.find('span', class_='company').text
        company = company.replace('\n', '')


        #Not all companies have a rating 
        try:
            rating = desc.find('span', class_='ratingsContent').text
            rating = rating.replace('\n', '')
        except:
            rating = '-'


        #Not all job postings have a listed location
        try:
            location = desc.find('span', class_='location').text
        except:
            location = '-'


        #Details of the job responsibilites 
        summary = desc.find('div', class_='summary').text
        summary = summary.replace('\n', '')


        #Extract direct URL to the job listing 
        rawLink = desc.find('a', class_='jobtitle')
        jobLink = rawLink.get('href')
        jobLink = jobLink[jobLink.find('?') + 1 : ]
        jobLink = ('https://www.indeed.com/viewjob?' + jobLink).replace('\n', '')


        #Some URLs are different 
        if 'jk=' not in jobLink:
            rawLink = str(rawLink.get('href'))
            jobLink = 'https://www.indeed.com/viewjob?cmp=' + company + '&t=' + rawLink[rawLink.find('jobs') + 5 : rawLink.rindex('-')] + '&jk=' + rawLink[rawLink.rindex('-') + 1 : rawLink.find('?')]
            
            
        rows.append([title, company, rating, location, summary, jobLink])
    
    return rows


# In[10]:


#Get the total amount of pages to scrape through for all job listings found 
def getNumListings(url):
    
    page = requests.get(url, proxies = {"http": next(proxyPool)})
    soup = BeautifulSoup(page.text, 'html.parser')

    rawNumJobs = soup.find(id='searchCountPages').text.replace('\n', '')
    numJobs = rawNumJobs[rawNumJobs.find('of') + 3 : rawNumJobs.find('jobs')]
    
    pages = (int(numJobs) // 15) + 1
    return numJobs, pages    


# In[15]:


#Data for each row of the excel file will be stored in this 
csvRows = []

def clean(stng):
    
    #We want to get rid of these characters 
    bad_chars = ['[', ']', '"', ','] 

    for i in bad_chars : 
        stng = stng.replace(i, '') 
        
    return stng

def scrapeListings(position):
    
    position_ = position.replace(' ', '+')
    page = 0
    
    totalJobs, pages = getNumListings('https://www.indeed.com/jobs?q=' + position_ + '&l=New+York%2C+NY')

    print(totalJobs + 'jobs found!', str(pages) + ' pages')
    
    #Go through 10 pages of results 
    for x in range(pages):

        url = 'https://www.indeed.com/jobs?q=' + position_ + '&l=New+York%2C+NY&start=' + str(page) 
        jobInfo = extractJobListings(url)

        csvRows.append(jobInfo)

        page += 10
        
        
    # Column Names in the excel file  
    fields = 'Title, Company, Rating, Location, Summary, Job Link\n' 

    # Name of Excel file  
    fileName = position + " Job Postings.csv"
    
    #Write to excel file 
    MyFile = open(fileName, 'w', encoding="utf-8")

    MyFile.write(fields)
    
    #Append the data to the rows of the file 
    for row in csvRows:
        for job in row:
            MyFile.write(clean(job[0]) + ',' + clean(job[1]) + ',' + clean(job[2]) + ',' + clean(job[3]) + ',' + clean(job[4]) + ',' + clean(job[5]))
            MyFile.write('\n')

    MyFile.close()

    print('\nSaved as ' + fileName)


# In[19]:


position = input("Enter the job position you are searching for: ") 

scrapeListings(position)


# In[ ]:




