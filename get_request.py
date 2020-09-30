#!/usr/bin/env python
# coding: utf-8
# required library imports

import altair as alt
import pandas as pd 

## pandas options

pd.options.display.max_columns = 60
pd.options.display.min_rows = 20


import requests
import urllib
from urllib.request import urlopen
from xml.etree import ElementTree as xml_etree
from lxml import etree as lxml_etree

def main():
    ## load the XML files per URL to stay up-to-date when changes occur.
    url = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml" ## weekly + diff()-Bash 

    try:
        response = requests.get(url)
        treeFile = xml_etree.fromstring(response.content)
        print(treeFile)
    except:
        print('Cell[2]: Tree coulnd\'t be build, is the Website/Database online?\nCheck https://blanco.biomol.uci.edu/mptopo/mptopoTblXml')

main()