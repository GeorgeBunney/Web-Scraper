# Web-Scraper

##Objectives 
to create a program that can look through lists of Audible audiobooks and compile information about the authors.

##Method
first a selenium webdriver is used to load the page and compile a list of urls of authors information pages. This list of urls is then passed to another function that iterates through the list and and loads the author pages and downloads their information. The author information is then uploaded to AWS servers, RDS for tabular data and S3 for images. All of this can be run from an EC2 instance as a docker file.
