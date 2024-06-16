import requests
from bs4 import BeautifulSoup
import os

# Base URL for appending the href values extracted from the HTML snippet
base_url = "https://www.tsdps.telangana.gov.in/"

# Your HTML snippet here
html_snippet = """
<tr>
    
        <td width="123%" align="left" valign="top" bgcolor="#FFFFFF" ><img src="Rainfall/Deviation.jpg" width="745" height="485" border="0" usemap="#Map" />
        <map name="Map" id="Map">
        <area shape="rect" coords="24,366,86,398" href="mandaldata.jsp?s1=33" />
        <area shape="rect" coords="356,186,443,214" href="mandaldata.jsp?s1=32" />
        <area shape="rect" coords="157,42,210,68" href="mandaldata.jsp?s1=1" />
        <area shape="rect" coords="237,63,333,89" href="mandaldata.jsp?s1=2" />
        <area shape="rect" coords="262,96,337,123" href="mandaldata.jsp?s1=3" />
        <area shape="rect" coords="195,123,245,149" href="mandaldata.jsp?s1=6" />
        <area shape="rect" coords="116,93,191,117" href="mandaldata.jsp?s1=4" />
        <area shape="rect" coords="267,149,316,169" href="mandaldata.jsp?s1=7" />
        <area shape="rect" coords="333,152,420,180" href="mandaldata.jsp?s1=8" />
        <area shape="rect" coords="393,243,467,286" href="mandaldata.jsp?s1=9" />
        <area shape="rect" coords="344,317,410,338" href="mandaldata.jsp?s1=31" />
        <area shape="rect" coords="323,261,373,295" href="mandaldata.jsp?s1=10" />
        <area shape="rect" coords="301,320,340,354" href="mandaldata.jsp?s1=30" />
        <area shape="rect" coords="227,337,291,380" href="mandaldata.jsp?s1=29" />
        <area shape="rect" coords="161,389,222,432" href="mandaldata.jsp?s1=28" />
        <area shape="rect" coords="107,407,152,427" href="mandaldata.jsp?s1=27" />
        <area shape="rect" coords="67,428,109,460" href="mandaldata.jsp?s1=26" />
        <area shape="rect" coords="89,349,151,381" href="mandaldata.jsp?s1=25" />
        <area shape="rect" coords="121,307,183,341" href="mandaldata.jsp?s1=23" />
        <area shape="rect" coords="60,300,106,325" href="mandaldata.jsp?s1=24" />
        <area shape="rect" coords="196,255,247,272" href="mandaldata.jsp?s1=21" />
        <area shape="rect" coords="206,276,239,287" href="mandaldata.jsp?s1=22" />
        <area shape="rect" coords="195,218,243,243" href="mandaldata.jsp?s1=18" />
        <area shape="rect" coords="281,234,330,258" href="mandaldata.jsp?s1=19" />
        <area shape="rect" coords="184,171,230,195" href="mandaldata.jsp?s1=14" />
        <area shape="rect" coords="247,181,293,206" href="mandaldata.jsp?s1=13" />
        <area shape="rect" coords="128,218,176,248" href="mandaldata.jsp?s1=17" />
        <area shape="rect" coords="64,247,117,271" href="mandaldata.jsp?s1=16" />
        <area shape="rect" coords="95,177,153,198" href="mandaldata.jsp?s1=15" />
        <area shape="rect" coords="107,134,174,168" href="mandaldata.jsp?s1=5" />
        <area shape="rect" coords="308,210,345,233" href="mandaldata.jsp?s1=12" />
        <area shape="rect" coords="350,226,380,251" href="mandaldata.jsp?s1=11" />
        <area shape="rect" coords="261,256,292,280" href="mandaldata.jsp?s1=20" />
        </map></td>
</tr>
"""

# Parse the HTML snippet with BeautifulSoup
soup = BeautifulSoup(html_snippet, "html.parser")

# Extract all area tags with href attributes
area_tags = soup.find_all('area', href=True)

# Directory to save images
save_dir = "downloaded_images"
os.makedirs(save_dir, exist_ok=True)

for tag in area_tags:
    href_value = tag['href']
    mandal_id = href_value.split('=')[-1]  # Extract the value after '='
    img_url = base_url + f"Rainfall/{mandal_id}_dev.jpg"
    file_name = os.path.join(save_dir, f"{href_value.replace('?', '_').replace('=', '_')}.jpg")
    
    # Download the image
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_name}")
    else:
        print(f"Failed to download {file_name}")

print("All done.")
