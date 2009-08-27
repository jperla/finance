#!/usr/bin/env python
import re
import sys

from pyquery import PyQuery as pq



def main():
    filename = 'SNS1.html' if len(sys.argv) <= 1 else sys.argv[1]
    html = open(filename, 'r').read()
    tables = [table_data_from_html(t) for t in tables_html_from_page(html)]
    print tables

def tables_html_from_page(html):
    doc = pq(html)
    tables = doc('table')
    return [table for table in tables]
    
def table_data_from_html(table_html):
    head, body = split_head_and_body(table_html)
    head_rows =  split_head(head)
    body_rows =  split_body(body)
    columns = significant_columns(body_rows)
    table = table_data(body_rows, columns, head_rows)
    return table

def table_data(body_rows, columns, head_rows):
    table = []
    for row in body_rows:
        d = row_data(row, columns, head_rows)
        for key in d:
            table.append((key, d[key]))
    return table

def key_from_head_rows(head_rows, index):
    key = '---'.join([r[index] for r in head_rows])
    key = ''
    for row in head_rows:
        if row[index].startswith('20') or row[index].startswith('19'):
            key = row[index][0:4]
    return normalize_heading(key)

def row_data(row, significant_columns, head_rows):
    assert(len(row) == len(significant_columns))
    if len(row) == 0:
        return {}
    else:
        name = normalize_heading(row[0])
        data = {}
        for i,significant in enumerate(significant_columns):
            if significant:
                key = key_from_head_rows(head_rows, i)
                value = num_from_cell(row[i])
                if key is not None and value is not None:
                    data[key] = value
        if name == '' or data == {}:
            return {}
        else:
            return {name:data}

def normalize_heading(text):
    return re.sub('\s+', ' ', text)

def num_from_cell(cell):
    if len(cell) == 0:
        return None
    if cell[0] == '(':
        cell = '-' + cell[1:]
    cell = cell.replace(',', '')
    try:
        return float(cell)
    except:
        # cell parsing here
        return None

def significant_columns(body_rows):
    assert(all_equal([len(r) for r in body_rows]))
    if len(body_rows) == 0:
        return []
    else:
        row_length = len(body_rows[0])
        columns = [False] * row_length
        for i in range(row_length):
            column = [row[i] for row in body_rows]
            if any([num_from_cell(c) is not None for c in column]):
                columns[i] = True
        return columns

def split_body(body_html):
    return rows_from_table_html(body_html)

def split_head(head_html):
    rows = []
    head_doc = pq(head_html)
    trs = head_doc('tr')
    for tr_element in trs:
        tr = pq(tr_element)
        row = []
        for td in tr('td'):
            td_doc = pq(td)
            colspan = td_doc.attr('colspan')
            row += [td_doc.text()] * (1 if colspan is None else int(colspan))
        rows.append(row)
    return rows
    
def all_equal(a):
    if len(a) == 0:
        return True
    return all([a[0] == e for e in a])

def remove_empty_columns(table):
    lengths = [len(r) for r in table]
    assert(all_equal(lengths))
    columns = [True] * lengths[0]
    for i,_ in enumerate(columns):
        if all([u'' == row[i] for row in table]):
            columns[i] = False
    new_table = []
    for row in table:
        new_row = [e for i,e in enumerate(row) if columns[i]]
        new_table.append(new_row)
    assert(all_equal([len(r) for r in new_table]))
    return new_table

def split_head_and_body(table_html):
    table_rows = rows_from_table_html(table_html)
    max_length = max([len(row) for row in table_rows])

    table_doc = pq(table_html)

    head, body = [], []
    in_head = True
    for tr_element in table_doc('tr'):
        tr_doc = pq(tr_element)
        cells = [pq(td).text() for td in tr_doc('td')]

        if in_head and len(cells) < max_length:
            head.append(tr_doc.html())
        else:
            in_head = False
            body.append(tr_doc.html())
    head = '<tr>' + ('</tr><tr>'.join(head))+ '</tr>'
    body = '<tr>' + ('</tr><tr>'.join(body)) + '</tr>'
    return head, body

def rows_from_table_html(table_element):
    rows = []
    table = pq(table_element)
    trs = table('tr')
    for tr_element in trs:
        tr = pq(tr_element)
        cells = [pq(td).text() for td in tr('td')]
        rows.append(cells)
    return rows

if __name__ == '__main__':
    main()
