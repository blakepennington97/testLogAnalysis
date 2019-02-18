# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 16:33:08 2019

@author: bpenning
"""


import plotly
import plotly.graph_objs as go
import pandas as pd
import csv
import os
from pprint import pprint
from datetime import datetime

startTime = datetime.now()

testFilePath = 'C:\\Users\\bpenning\\Desktop\\testLogs\\data\\testLog.txt'

#path where output files go
PATH = 'C:\\Users\\bpenning\\Desktop\\testLogs\\data'
#path leading to the Test Log file
txtFilePath = 'C:\\Users\\bpenning\\Desktop\\testLogs\\data\\1287702G1.201707'


failuresFilePath = PATH + '\\FAILURES.csv'
passesFilePath = PATH + '\\PASSES.csv'
allFilePath = PATH + '\\ALL.csv'

testLog = (os.path.basename(txtFilePath)).split('.')[0]

date = ''
time = ''
setNumber = ''
serialNumber = ''
workOrder = ''
testTime = ''

def testStepsToPlot(txtFilePath):

    print 'Plotting test step failures...'
    txtFileObj = open(txtFilePath, 'r')
    txtFile = txtFileObj.read()
    
    #Intialize variables
    lstFile = []
    tempLst = []
    lstFile = txtFile.split('\n')
    lstFile.pop(0)
    testStepsFailed = [' ']
    
    #Parse txtFile
    for row in lstFile:
        tempLst.append(row)
        if 'FAIL' in row:
            for row2 in reversed(tempLst):
                if 'Test Step' in row2:
                    if row2 not in testStepsFailed[-1]:
                        testStepsFailed.append(row2)
                    break
                elif 'Step ' in row2:
                    if row2 not in testStepsFailed[-1]:
                            testStepsFailed.append(row2.split('[')[0] )
                    break
                else:
                    del (tempLst[-1])
                
    #Clear memory
    del(tempLst[:])
    testStepsFailed.pop(0)
    
    #Organize dataframes
    df = pd.DataFrame(testStepsFailed, columns = ['Test Steps Failed'])
    df2 = df.groupby(by = ['Test Steps Failed'], sort = False)['Test Steps Failed'].count().reset_index(name = "count")
    df2 = df2.sort_values(by = 'count', ascending = False)

    #Now plot
    data = [
        go.Bar(x = df2['Test Steps Failed'], y = df2['count'], marker = dict(color='rgb(14,0,140)'))
        ]
    layout = go.Layout(barmode='group', title='Test Step Failures for ' + testLog, xaxis = dict(title = 'Test Steps', showticklabels = False), yaxis = dict(title = 'Count'), margin = go.layout.Margin(l = 200))
    fig = go.Figure(data = data, layout = layout)
    plotly.offline.plot(fig, filename = 'Test_Step_Failures.html', auto_open = True)
    
    txtFileObj.close()            
    return

def testStepRetries(filePath):
    
    print 'Plotting test step retries...'
    txtFileObj = open(filePath, 'r')
    txtFile = txtFileObj.read()
    
    indexEnd = 0
    indexStart = 0
    lstFile = []
    retriesList = []
    retriesList2 = []
    lstFile = txtFile.split('\n')
    lstFile.pop(0)
    type2 = False
    
    #Parse txtFile
    for row in lstFile:
        indexEnd += 1
        row = row.replace('*', '')
        if 'Initialize Unit' in row:
            indexStart = indexEnd
        if 'END TEST:  RESULT = PASS' in row:
            while (indexStart < indexEnd):
                if 'Test Step' in lstFile[indexStart]:
                    if 'Retry Test' in lstFile[indexStart+1]:
                        retriesList.append(lstFile[indexStart])
                elif 'RETRY' in lstFile[indexStart]:
                    retriesList2.append(lstFile[indexStart].split('[')[0] )
                    type2 = True
                indexStart += 1
    
    #Organize dataframes
    if type2 == False:
         df = pd.DataFrame(retriesList, columns = ['Test Steps Retried'])
    else:
        df = pd.DataFrame(retriesList2, columns = ['Test Steps Retried'])
    df2 = df.groupby(by = ['Test Steps Retried'], sort = False)['Test Steps Retried'].count().reset_index(name = "count")
    df2 = df2.sort_values(by = 'count', ascending = False)
    #Now plot
    data = [
        go.Bar(x = df2['Test Steps Retried'], y = df2['count'],  marker = dict(color='rgb(140,77,0)'))
        ]
    layout = go.Layout(barmode='group', title='Test Step Retries for Passed Tests for ' + testLog, xaxis = dict(title = 'Test Steps', showticklabels = False), yaxis = dict(title = 'Count'), margin = go.layout.Margin(l = 200))
    fig = go.Figure(data = data, layout = layout)
    plotly.offline.plot(fig, filename = 'Test_Step_Retries.html', auto_open = True)
    
    txtFileObj.close()         
    return
    
def failuresToCSV(txtFilePath):
    
    print 'Generating failures report...'
    header = ['Date Tested', 'Time Tested', 'Test Set Number', 'Product Serial Number', 'Work Order']

    newCsvFile = open(PATH + '\\FAILURES.csv', 'wb')
    txtFileObj = open(txtFilePath, 'r')
    txtFile = txtFileObj.read()
    writer = csv.writer(newCsvFile)

    
    writer.writerow(header)
    
    lstFile = []
    lstFile = txtFile.split('\n')
    lstFile.pop(0)
    indexStart = 0
    indexEnd = 0
    date = ''
    time = ''
    setNumber = ''
    serialNumber = ''
    workOrder = ''
    
    for row in lstFile:
        indexEnd += 1
        row = row.replace('*', '')
        if 'END TEST:  RESULT = PASS' in row:
            indexStart = indexEnd
            
        if 'END TEST:  RESULT = NO_TEST' in row:
            indexStart = indexEnd
        if 'END TEST:  RESULT = ABORTed' in row:
            indexStart = indexEnd
        if ('END TEST:  RESULT = FAIL' or 'END TEST:  RESULT = *FAIL*') in row:
            while (indexStart <= indexEnd):
                #print lstFile[indexStart]
                #print txtFile[indexStart]
                if 'OPERATOR:' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0]
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'OPERATOR,' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0].rstrip(',')
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'TESTSET:' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'TESTSET,' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'Work order,' in lstFile[indexStart]:
                    workOrderLst = lstFile[indexStart].split(' ')
                    workOrder = workOrderLst[2].rstrip(',')
                    #all necessary tabular data found, so writerow
                    writer.writerow([date, time, setNumber, serialNumber, workOrder])
                    
                indexStart += 1
    txtFileObj.close()            
    newCsvFile.close()
    return

def AllToCsv(txtFilePath):
    
    print 'Generating overall report...'
    header = ['Date Tested', 'Time Tested', 'Test Set Number', 'Product Serial Number', 'Work Order']

    newCsvFile = open(PATH + '\\ALL.csv', 'wb')
    txtFileObj = open(txtFilePath, 'r')
    txtFile = txtFileObj.read()
    writer = csv.writer(newCsvFile)


    writer.writerow(header)
    #writer.writerow('\n')
    
    lstFile = []
    lstFile = txtFile.split('\n')
    lstFile.pop(0)
    indexStart = 0
    indexEnd = 0
    date = ''
    time = ''
    setNumber = ''
    serialNumber = ''
    workOrder = ''
    testTime = ''
    
    for row in lstFile:
        indexEnd += 1
        row = row.replace('*', '')
        if 'END TEST:  RESULT = PASS' in row:
            while (indexStart <= indexEnd):
                if 'OPERATOR:' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0]
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'OPERATOR,' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0].rstrip(',')
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'TESTSET:' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'TESTSET,' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'Work order,' in lstFile[indexStart]:
                    workOrderLst = lstFile[indexStart].split(' ')
                    workOrder = workOrderLst[2].rstrip(',')
                    #all necessary tabular data found, so writerow
                    writer.writerow([date, time, setNumber, serialNumber, workOrder])
                    
                indexStart += 1
            
        if 'END TEST:  RESULT = NO_TEST' in row:
            indexStart = indexEnd
        if 'END TEST:  RESULT = ABORTed' in row:
            indexStart = indexEnd
        if 'END TEST:  RESULT = FAIL' in row:
            while (indexStart <= indexEnd):
                #print lstFile[indexStart]
                #print txtFile[indexStart]
                if 'OPERATOR:' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0]
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'OPERATOR,' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0].rstrip(',')
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'TESTSET:' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'TESTSET,' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'Work order,' in lstFile[indexStart]:
                    workOrderLst = lstFile[indexStart].split(' ')
                    workOrder = workOrderLst[2].rstrip(',')
                    #all necessary tabular data found, so writerow
                    writer.writerow([date, time, setNumber, serialNumber, workOrder])
                    
                indexStart += 1
    txtFileObj.close()            
    newCsvFile.close()
    return



def CSVtoWorkOrderPlot(filePath):
    
    print 'Plotting work order failures...'
    df = pd.read_csv(filePath)
    df2 = pd.read_csv(allFilePath)
    
    df['Work Order'] = df['Work Order'].astype(str).replace(to_replace = '.', value = '_').str.replace('.', '_')
    df2['Work Order'] = df2['Work Order'].astype(str).replace(to_replace = '.', value = '_').str.replace('.', '_')
    
    workOrderTable = df.groupby(by = ['Work Order'], sort = False)['Work Order'].count().reset_index(name = "count")
       
    workOrderTable2 = df2.groupby(by = ['Work Order'], sort = False)['Work Order'].count().reset_index(name = "count")
   
    mergedDF = pd.merge(workOrderTable, workOrderTable2, how = 'outer', on = 'Work Order')

    mergedDF['Fail %'] = (mergedDF['count_x']/ mergedDF['count_y']) * 100
    mergedDF = mergedDF.sort_values(by = 'Fail %', ascending = False).fillna(0)
    text = mergedDF['count_y'].tolist()
    for i in range(len(text)):
        text[i] = 'Tests: ' + str(text[i])
 
    data = [
        go.Bar(x = mergedDF['Work Order'], y = mergedDF['Fail %'], name = 'fdasfas', hovertext = text, marker = dict(color='rgb(140,7,0)'))
        ]
    layout = go.Layout(barmode='group', title='Work Order Failure Percentage for ' + testLog, xaxis = dict(title = 'Work Orders', type = 'category'), yaxis = dict(title = 'Failure %'))
    fig = go.Figure(data = data, layout = layout)
    plotly.offline.plot(fig, filename = 'Work_Order_Failure_Percentage.html', auto_open = True)
    
    return

def CSVtoTestSetPlot(filePath):
    #only accounts for passes/failures, not aborts/no_tests (on purpose)
    print 'Plotting test set failures...'
    
    df = pd.read_csv(filePath)
    df2 = pd.read_csv(allFilePath)
    
    df['Test Set Number'] = df['Test Set Number'].astype(str)
    df2['Test Set Number'] = df2['Test Set Number'].astype(str)
    
    #print df
    testSetTable = df.groupby(by = ['Test Set Number'], sort = False)['Test Set Number'].count().reset_index(name = "count")

    testSetTable2 = df2.groupby(by = ['Test Set Number'], sort = False)['Test Set Number'].count().reset_index(name = "count")
  
    mergedDF = pd.merge(testSetTable, testSetTable2, how = 'outer', on = 'Test Set Number')
       
    mergedDF['Fail %'] = (mergedDF['count_x'] / mergedDF['count_y']) * 100
   
    mergedDF = mergedDF.sort_values(by = 'Fail %', ascending = False).fillna(0)
    #print mergedDF

    xData = mergedDF['Test Set Number'].values.tolist()
    #print xData
    text = mergedDF['count_y'].tolist()
    for i in range(len(text)):
        text[i] = 'Tests: ' + str(text[i])
    
    data = [
        go.Bar(x = xData, y = mergedDF['Fail %'], name = 'fdasfas', hovertext = text, marker = dict(color='rgb(0,114,22)'))
        ]
    layout = go.Layout(barmode='group', title='Test Set Failure Percentage for ' + testLog, xaxis = { 'title': 'Test Sets', 'type' : 'category'}  , yaxis = { 'title': 'Failure %'} )
    fig = go.Figure(data = data, layout = layout)
    plotly.offline.plot(fig, filename = 'Test_Set_Failure_Percentage.html', auto_open = True)
    
    return

def passesToCSV(txtFilePath):
    
    print 'Generating passes report...'
    header = ['Date Tested', 'Time Tested', 'Test Set Number', 'Product Serial Number', 'Work Order', 'Test Time']

    newCsvFile = open(PATH + '\\PASSES.csv', 'wb')
    txtFileObj = open(txtFilePath, 'r')
    txtFile = txtFileObj.read()
    writer = csv.writer(newCsvFile)


    writer.writerow(header)
    #writer.writerow('\n')
    
    lstFile = []
    lstFile = txtFile.split('\n')
    lstFile.pop(0)
    indexStart = 0
    indexEnd = 0
    date = ''
    time = ''
    setNumber = ''
    serialNumber = ''
    workOrder = ''
    testTime = ''
    
    for row in lstFile:
        indexEnd += 1
        row = row.replace('*', '')
        if 'END TEST:  RESULT = FAIL' in row:
            indexStart = indexEnd
        
        if 'END TEST:  RESULT = NO_TEST' in row:
            indexStart = indexEnd
        if 'END TEST:  RESULT = ABORTed' in row:
            indexStart = indexEnd
        if 'END TEST:  RESULT = PASS' in row:
            while (indexStart <= indexEnd):
                #print lstFile[indexStart]
                #print txtFile[indexStart]
                if 'OPERATOR:' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0]
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'OPERATOR,' in lstFile[indexStart]:
                    dateTime = lstFile[indexStart].split(' ')
                    #print dateTime
                    date = dateTime[0].rstrip(',')
                    time = dateTime[1] + ' ' + dateTime[2].rstrip(',')
                if 'TESTSET:' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'TESTSET,' in lstFile[indexStart]:
                    testSet_and_serialNumber = lstFile[indexStart].split(' ')
                    setNumber = testSet_and_serialNumber[1].rstrip(',')
                    serialNumber = testSet_and_serialNumber[-1]
                if 'Work order,' in lstFile[indexStart]:
                    workOrderLst = lstFile[indexStart].split(' ')
                    workOrder = workOrderLst[2].rstrip(',')
                if 'TEST TIME =' in lstFile[indexStart]:
                    testTimeLst = lstFile[indexStart].split(' ')
                    testTime = testTimeLst[-1]
                    if testTime == 'sec.':
                        minutes = int(testTimeLst[4])
                        hour = 0
                        while minutes > 59:
                            minutes -= 60
                            hour += 1   
                        if hour < 24:    
                            testTime = '%02d:%02d:00' % (hour, minutes)
                        else:
                            testTime = ''
                            #print testTime
                    #all necessary tabular data found, so writerow
                    writer.writerow([date, time, setNumber, serialNumber, workOrder, testTime])
                    
                indexStart += 1
                
    txtFileObj.close()            
    newCsvFile.close()
    return

def testSetPassesToTestTime(passesFilePath):
    
    print 'Plotting Test Set test times...'
    df = pd.read_csv(passesFilePath)
    #df2 = pd.read_csv(allFilePath)
    
    df['Test Set Number'] = df['Test Set Number'].astype(str)
    df['Test Time'] =pd.to_datetime(df['Test Time'])
    df['Test Time In Seconds'] = df['Test Time'].dt.hour * 60 + df['Test Time'].dt.minute + df['Test Time'].dt.second/60
    #print df
    testSetTable = df.groupby(by = ['Test Set Number'], sort = False)['Test Time In Seconds'].mean().reset_index(name = 'Avg Test Time(minutes)')
    testSetTable2 = df.groupby(by = ['Test Set Number'], sort = False)['Test Time In Seconds'].median().reset_index(name = 'Median Test Time(minutes)')
  
    mergedDF = pd.merge(testSetTable, testSetTable2, how = 'outer', on = 'Test Set Number')
    mergedDF = mergedDF.sort_values(by = 'Avg Test Time(minutes)', ascending = False)
    #print mergedDF
  
    totalMean = mergedDF['Avg Test Time(minutes)'].mean()
    totalMedian = mergedDF['Median Test Time(minutes)'].mean()
    
    mergedDF.to_csv(PATH + '\\TestTimes.csv', index = False)
    
    csvFile = open(PATH + '\\TestTimes.csv', 'ab+')
    writer = csv.writer(csvFile)
    
    writer.writerow('')
    writer.writerow(['AVERAGE', totalMean, totalMedian])
    
    
    csvFile.close()
    
    data = [
        go.Bar(x = mergedDF['Test Set Number'], y = mergedDF['Avg Test Time(minutes)'], marker = dict(color='rgb(63,0,140)'), name = 'Average Test Time'),
        go.Bar(x = mergedDF['Test Set Number'], y = mergedDF['Median Test Time(minutes)'], marker = dict(color='rgb(140,110,0)'), name = 'Median Test Time')
        ]
    layout = go.Layout(barmode='group', title='Test Set Test Times for ' + testLog, xaxis = { 'title': 'Test Sets', 'type' : 'category'}  , yaxis = { 'title': 'Test Time(minutes)'} )
    fig = go.Figure(data = data, layout = layout)
    plotly.offline.plot(fig, filename = 'Test_Set_Test_Times.html', auto_open = True)
    
    return

def testSetEfficiency(filePath):
    
    print 'Plotting test set efficiency...'
    
    txtFileObj = open(filePath, 'r')
    txtFile = txtFileObj.read()
    
    lstFile = []
    tempLst = []
    setNumberLst = []
    lstFile = txtFile.split('\n')
    lstFile.pop(0)
    
    for row in lstFile:
        row = row.replace('*', '')
        if 'TESTSET:' in row:
            testSet_and_serialNumber = row.split(' ')
            setNumberLst.append(testSet_and_serialNumber[1].rstrip(',') )
        if 'TESTSET,' in row:
            testSet_and_serialNumber = row.split(' ')
            setNumberLst.append(testSet_and_serialNumber[1].rstrip(',') )
        if 'END TEST:  RESULT =' in row:
            tempLst.append(row)
            
    df = pd.DataFrame( {'Test Set': setNumberLst, 'Result': tempLst} )
    df = df.sort_values(by = ['Test Set'])
    #print df
    
    df2 = df.groupby(by = ['Test Set'])['Result'].count().reset_index(name = 'count')
    df3 = df.groupby(by = ['Test Set', 'Result'])['Result'].count().reset_index(name = 'count')
    
    #print df2
    #print df3
    
    mergedDF = pd.merge(df2, df3, how = 'outer', on = 'Test Set')
    
    #print mergedDF
       
    total = 0
    testSet = mergedDF['Test Set'][0]
    mergedDF['Fail %'] = mergedDF['count_x']
    failList = []
    
    mergedDF['Fail %'] = (mergedDF['count_y'] / mergedDF['count_x']) * 100
    
    for i in range(len(mergedDF['Result'])):
        #print testSet
        #print i
        if testSet != mergedDF['Test Set'][i]:
            failList.append(total)
            total = 0
            #print testSet
            testSet = mergedDF['Test Set'][i]
        if mergedDF['Result'][i] == 'END TEST:  RESULT = PASS':
            total += mergedDF['Fail %'][i]
        if mergedDF['Result'][i] == 'END TEST:  RESULT = FAIL':
            total += mergedDF['Fail %'][i]
    failList.append(total)
                
    #pprint (failList)
    index = df2['Test Set'].tolist()
    df4 = pd.DataFrame({'Test Set': index, 'Fail %': failList})
    df4 = df4.sort_values(by = ['Fail %'])
    
    text = df2['count'].tolist()
    for i in range(len(text)):
        text[i] = 'Tests: ' + str(text[i])
    
    data = [
        go.Bar(x = df4['Test Set'], y = df4['Fail %'], hovertext = text, marker = dict(color='rgb(28,237,125)'))
        ]
    layout = go.Layout(barmode='group', title='Test Set Efficiency for ' + testLog, xaxis = { 'title': 'Test Sets', 'type' : 'category'}  , yaxis = { 'title': 'Efficiency %'} )
    fig = go.Figure(data = data, layout = layout)
    plotly.offline.plot(fig, filename = 'Test_Set_Efficiency.html', auto_open = True)
    
    return


failuresToCSV(txtFilePath)
passesToCSV(txtFilePath)
AllToCsv(txtFilePath)
#CSVtoWorkOrderPlot(failuresFilePath)
CSVtoTestSetPlot(failuresFilePath)
#testStepsToPlot(txtFilePath)
#testStepRetries(txtFilePath)
#testSetPassesToTestTime(passesFilePath)
testSetEfficiency(txtFilePath)

print
print 'This script took: ' + str(datetime.now() - startTime) + ' to run.'


