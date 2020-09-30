## In this file the deployment of the dashboard should take place.
# import all_the_files

import requests
import urllib
from urllib.request import urlopen
import xml.etree.ElementTree as etree
from lxml import etree as lxml_etree


if __name__ == "__main__":
    ## do stuff
    ## dashboard = new Class Dashboard
    ## ... dashboard.serve(someHost)
    ## load the XML files per URL to stay up-to-date when changes occur.

    all_data = "https://blanco.biomol.uci.edu/mpstruc/listAll/mpstrucTblXml" ## weekly + diff()-Bash 

    try:
        response = requests.get(all_data)
        print(response.data)
        treeFile = etree.fromstring(response.content)
    except:
        print('Cell[2]: Tree coulnd\'t be build, is the Website/Database online?\nCheck https://blanco.biomol.uci.edu/mptopo/mptopoTblXml')

main()