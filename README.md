# gitlit

This repo is the result of a scraper that scrapes the Github Actions runtimes from the Github API. 

The goal is to get a clear picture of the amount of compute is spent for CI for common open source packages. 
The hope is that we may learn from it and learn how to run code in a more lightweight fashion. 

The data is explorable via a streamlit app shown [here](https://share.streamlit.io/koaning/gitlit/main). 

The data is updated daily, assuming the cronjob doesn't face any bugs. 
