#!/usr/bin/env python
from __future__ import absolute_import

import re
import os
import urllib
import datetime
import time
from itertools import izip, cycle, count

import couchdb

import webify
from webify.templates.helpers import html
from webify.controllers import webargs
import markdown

import seclib
import extracttable

app = webify.defaults.app()

def latest_report(ticker):
    return open('SNS1.html', 'r').read()

@app.subapp(path='/')
@webify.urlable()
def index(req, p):
    ticker = req.params.get('ticker', '')
    if ticker == '':
        p(partial_search_box(ticker))
    else:
        webify.http.redirect_page(p, financials.url(ticker))

@app.subapp()
@webargs.RemainingUrlableAppWrapper()
def originals(req, p, ticker):
    number = req.params.get('num')
    url, page = seclib.latest_10k_financials(ticker)
    if number is not None:
        page = highlight_number_in_html(page, number)
    indices = extracttable.tables_start_indices_from_page(page)
    page = insert_anchors_into_html_at_indices(page, indices)
    p(template_originals(ticker, url, page))

def insert_anchors_into_html_at_indices(page, indices):
    for table_number,index in reversed(list(enumerate(indices))):
        attrs = {'name':'table-%s' % table_number}
        page = page[:index] + '\n' + html.a(attrs=attrs) + '\n' + page[index:]
    return page

def highlight_number_in_html(page, number):
    regex = '([^\d])(%s)([^\d])' % ',?'.join(number)
    page = re.sub(regex,
        r'\1<span style="background-color:yellow;font-weight:bold;">\2</span>\3',
        page)
    return page


@webify.template()
def template_originals(t, ticker, url, page):
    with t(html.div()):
        t(html.h1('Originals SEC Financials in 10K for %s' % ticker))
        t(u'Downloaded today from %s' % html.a(url, url))
    t(html.hr())
    t(unicode(page))

    
@app.subapp()
@webargs.RemainingUrlableAppWrapper()
def financials(req, p, ticker):
    try:
        url, page = seclib.latest_10k_financials(ticker)
        #tables = [t for t in tables if len(t) > 0]
    except:
        p(u'Could not find this ticker on SEC website')
    else:
        try:
            tables_html = extracttable.tables_html_from_page(page)
            tables = [extracttable.table_data_from_html(t) for t in tables_html]
        except:
            p(u'Failed to parse financial data from page: %s' % html.a(url, url))
        else:
            p(template_financials(ticker, tables))

@webify.template()
def template_financials(t, ticker, tables):
    t(u'''
        <head>
        <style type="text/css">
            a.num {
                color:black;
                text-decoration:none;
            }
            a.num:hover {
                text-decoration:underline;
            }
        </style>
        <title>Financials for %s</title>
        </head>
    ''' % ticker)
    t(partial_search_box(ticker))
    for table_number, table in enumerate(tables):
        t(partial_linked_financials_table(table, ticker, table_number))
    
def sorted_column_headings_from_table(table):
    columns = list(set([c for line_item, values in table for c in values]))
    return sorted(columns)

@webify.template()
def partial_linked_financials_table(t, table, ticker, table_number):
    column_headings = sorted_column_headings_from_table(table)
    with t(html.table(attrs={'width':'100%'})):
        with t(html.thead()):
            t(html.th(u'&nbsp;'))
            t(html.th(u'&nbsp;'))
            for c in column_headings:
                attrs = {'style':'width:70px;text-align:right;v-align:top;'}
                t(html.th(unicode(c), attrs=attrs))

        colors = cycle(['FFFFFF', 'CCFFFF'])
        for color, (line_item, values) in izip(colors, table):
            with t(html.tr({'style':'background-color:%s;' % color})):
                t(html.td(unicode(line_item), attrs={'style':'width:400px;'}))
                t(html.td(u'&nbsp;'))
                for c in column_headings:
                    if c in values:
                        attrs = {'style':
                                    'width:90px;text-align:right;v-align:top;'}
                        num = values[c]
                        link = html.a(originals.url(ticker) + '?num=%s#table-%s' % (int(num), table_number), number_in_table(num), attrs={'class':'num'})
                        t(html.td(link, attrs=attrs))
                    else:
                        t(html.td(u'&nbsp;'))
import locale
def number_in_table(num, places=0):
    locale.setlocale(locale.LC_ALL, '')
    if num < 0:
        contained = ['(', ')']
        num = -num
    else:
        contained = ['', '']
    with_commas = locale.format('%.*f', (places, num), True)
    return contained[0] + with_commas + contained[1]

@webify.template()
def partial_search_box(t, ticker):
    with t(html.div()):
        with t(html.form(attrs={'action':index.url()})):
            t(html.input_text('ticker', ticker))
            t(html.input_submit())

# Middleware
from webify.middleware import install_middleware, EvalException, SettingsMiddleware

# Server
from webify.http import server
if __name__ == '__main__':
    mail_server = webify.email.LocalMailServer()
    settings = {
                'mail_server': mail_server,
               }
    wsgi_app = webify.wsgify(app,
                                SettingsMiddleware(settings),
                                EvalException,
                            )
    print 'Loading server...'
    server.serve(wsgi_app, host='127.0.0.1', port=8085, reload=True)

