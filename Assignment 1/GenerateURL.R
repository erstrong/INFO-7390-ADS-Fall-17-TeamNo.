#install.packages("XML")
#install.packages("rvest")
#install.packages("xml2")
#install.packages("stringi")
#install.packages("RCurl")
library(XML)
library(xml2)
library(rvest)
library(stringi)
library(RCurl)

#Generate First URL:
cik <- '51143'
acc_no <- '0000051143-13-000007'
acc_short <- paste(substr(acc_no, 1, 10), substr(acc_no, 12, 13), substr(acc_no, 15,20), sep ='')
testurl <- paste('https://www.sec.gov/Archives/edgar/data', cik, acc_short, acc_no, sep='/')
testurl <- paste(testurl, '-index.htm', sep='')

#Parse page for all hrefs
page <- read_html(testurl)
hrefs <- html_attr(html_nodes(page, 'a'), 'href')

#Iterate through hrefs to find 10q URL
for (i in c(hrefs)) {
  if(stri_detect_fixed(i,'10q.htm') == TRUE){
    url10q = paste('https://www.sec.gov', i, sep='')
  }
}

#Extract tables from 10q
URL <- getURL(url10q)
tables <- readHTMLTable(URL, header = TRUE)
tables <- list.clean(tables, fun = is.null, recursive = FALSE)
