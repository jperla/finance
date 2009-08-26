import os
import urllib2 as u
import re

os.chdir("C:/Documents and Settings/Admin/My Documents/Python")


#*Define Years of Data Requested:
years = 1



ticker = []


f = open('./myTicker.txt')

for line in f:
	ticker.append(line.replace('\n', ''))

f.close()

#for x in ticker:
x = ticker[0]
base = "http://www.sec.gov"


sitename=r"http://www.sec.gov/cgi-bin/browse-idea?action=getcompany&CIK="+x.replace(".ob","")+"&type=10-K&dateb=&owner=exclude&count=40"
info = []
info.append(x)
sock = u.urlopen(sitename)
source = sock.read()
sock.close()
if (re.search("/Archives/edgar/data/(\d)+/(\d)+/((\d)+-?)*index.idea.htm", source)):
	b = re.split("10-K", source)
	a = []
	for z in b:
		if re.match("/A", z):
			c = 1
		elif not re.search("/Archives/edgar/data", z):
			c = 1
		else:
			a.append(z)
	
	files = []
	for i in range(0,min(years, len(a))):
		link = base + re.search("/Archives/edgar/data/(\d)+/(\d)+/((\d)+-?)*index.idea.htm", a[i]).group()
		fdate = re.search("\>(\d){4}-(\d){2}-(\d){2}\<", a[i]).group().replace("<","").replace(">","")
		sock = u.urlopen(link)
		src = sock.read()
		sock.close()
		temp = re.split("a href=", src)
		temp2 = re.split(">", temp[11])
		mylink = base+temp2[0].replace("\"","")
		files.append([mylink, fdate])
	info.append(files)

#########
scale = 0
#########

allFS = []

for i in range(0,len(info[1])):
	sock = u.urlopen(info[1][i][0])
	source = sock.read()
	sock.close()
	text = re.search("Report(\s)+of(\s)+Independent(\s)+Registered(\s)+Public(\s)+Accounting(\s)+Firm", source, re.I).group()
	a = re.split(text, source)
	text = re.search("Signatures", a[len(a)-1], re.I).group()
	b = re.split(text, a[len(a)-1])
	a = b[0]
	text = re.search("Notes(\s)+to(\s)+Consolidated(\s)+Financial(\s)+Statements[^.]", a, re.I).group()
	gold = re.split(text, a)
	#fs = re.split("See", gold[0])
	fs = gold[0]
	notes = gold[1]
	allFS.append(fs)
	f = open('./Filings/'+x+str(i+1)+'.txt', 'w')
	f.write(fs)
	f.close()
	f = open('./Filings/'+x+str(i+1)+'.html', 'w')
	f.write(fs)
	f.close()




i = 0
sock = u.urlopen(info[1][i][0])
source = sock.read()
sock.close()
text = re.search("Report(\s)+of(\s)+Independent(\s)+Registered(\s)+Public(\s)+Accounting(\s)+Firm", source, re.I).group()
a = re.split(text, source)
text = re.search("Signatures", a[len(a)-1], re.I).group()
b = re.split(text, a[len(a)-1])
a = b[0]
text = re.search("Notes(\s)+to(\s)+Consolidated(\s)+Financial(\s)+Statements[^.]", a, re.I).group()
gold = re.split(text, a)
#fs = re.split("See", gold[0])
fs = gold[0]
notes = gold[1]
allFS.append(fs)
f = open('./Filings/'+x+str(i+1)+'.txt', 'w')
f.write(fs)
f.close()
f = open('./Filings/'+x+str(i+1)+'.html', 'w')
f.write(fs)
f.close()
