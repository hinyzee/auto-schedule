from urllib.request import urlopen
from bs4 import BeautifulSoup

months = ["january",'february','march','april','may','june','july','august','september','october','november','december']
quarters = ["fall", "winter", "spring", "summer 1", "summer 2"]

# returns yyyy-mm-dd
def get_dates(theTime):

    data = theTime.split(" ",1)
    data[1] = data[1].lower()
    if len(data) != 2 or data[0].isalpha() or not data[1] in quarters:
        raise ValueError("Please check the dates again. The options are *year *(Fall/Winter/Spring/Summer 1/Summer 2)")

    year, quarter = data
    if quarter != "fall":
        year = str(int(year)-1)
    url = "https://blink.ucsd.edu/instructors/resources/academic/calendars/"+year+".html"
    if quarter != "fall":
        year = str(int(year)+1)
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')

    quarterind = quarters.index(quarter)
    quartercur = 0
    rows = soup.find("table", {"class":"styled"}).find("tbody").find_all("tr")
    startDate = endDate = ""
    for row in rows:

        tds = row.find_all("td")
        if len(tds) != 2:
            continue

        if tds[0].get_text() == "Instruction begins":
            if quartercur == quarterind:
                hihi = tds[1].get_text().split()
                mm = str(months.index(hihi[1].lower())+1)
                if len(mm) == 1:
                    mm = "0" + mm
                dd = hihi[2]
                if len(dd) == 1:
                    dd = "0" + dd
                startDate = "-".join([year, mm, dd])
            continue

        if tds[0].get_text() == "Instruction ends":
            if quartercur == quarterind:
                hihi = tds[1].get_text().split()
                mm = str(months.index(hihi[1].lower())+1)
                if len(mm) == 1:
                    mm = "0" + mm
                dd = hihi[2]
                if len(dd) == 1:
                    dd = "0" + dd
                endDate = "-".join([year, mm, dd])
                break
            quartercur += 1

    return (startDate, endDate)
