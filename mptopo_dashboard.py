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
import xml.etree.ElementTree as etree
from lxml import etree as lxml_etree

## load the XML files per URL to stay up-to-date when changes occur.

all_data = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml" ## weekly + diff()-Bash 

try:
    response = requests.get(all_data)
    treeFile = etree.fromstring(response.content)
except:
    print('Cell[2]: Tree coulnd\'t be build, is the Website/Database online?\nCheck https://blanco.biomol.uci.edu/mptopo/mptopoTblXml')

