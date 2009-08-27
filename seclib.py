from __future__ import with_statement
import os
import re
import urllib
import urllib2
from pyquery import PyQuery as pq

def download_url(url):
    return urllib2.urlopen(url).read()

def download_url(url):
    cache_path = os.path.join('page_cache', urllib.quote_plus(url))
    if os.path.exists(cache_path):
        return open(cache_path, 'r').read()
    else:
        page = urllib2.urlopen(url).read()
        with open(cache_path, 'w') as f:
            f.write(page)
        return page

base_url = 'http://www.sec.gov%s'

def list_of_10k_filing_urls(ticker):
    url_10k = 'http://www.sec.gov/cgi-bin/browse-edgar?owner=exclude&action=getcompany&type=10-K&CIK=%s'
    page = download_url(url_10k % ticker)

    all_rows = [pq(tr) for tr in pq(page)('tr')]
    real_rows = [tr for tr in all_rows if len(tr('td')) >= 2 and tr('td').eq(0).text() == '10-K']
    url = real_rows[0]('td a').eq(0).attr('href')
    return [base_url % url]

def latest_10k_url(ticker):
    urls = list_of_10k_filing_urls(ticker)
    latest = urls[0]
    all_filings_page = download_url(latest)
    all_rows = [pq(tr) for tr in pq(all_filings_page)('tr')]
    real_rows = [tr for tr in all_rows if len(tr('td')) >= 4 and tr('td').eq(3).text() == '10-K']
    url = real_rows[0]('td a').eq(0).attr('href')
    return base_url % url
 
def latest_10k(ticker):
    url = latest_10k_url(ticker)
    return url, download_url(url)

def financials_from_10k(html):
    regex = 'Report\s+of\s+Independent\s+Registered\s+Public\s+Accounting\s+Firm(.*?)Notes\s+to\s+Consolidated\s+Financial\s+Statements(.*?)Signatures'
    match = re.search(regex, html, re.S | re.I)
    if match is not None:
        statements, notes = match.group(1), match.group(2)
        return statements, notes

def latest_10k_financials(ticker):
    url, html = latest_10k(ticker)
    fs = financials_from_10k(html)[0]
    return url, fs

ticker = 'SNS'
url, html = latest_10k(ticker)
a,b = financials_from_10k(html)
print a[:200], b[:200]

