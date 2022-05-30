def parseProperty(PropValue):
    # Parses the value of the "Cobol Data in USING statement" property 
    # attached to a CALL USING link or a Procedure Division
    # Output: a table with one item per Cobol Data item listed in the property
    PropValue=PropValue.replace('BY ','')
    PropValueTable=PropValue.splitlines()

    line0=PropValueTable[0].strip().split()
    line0size=len(line0)
    
    if line0size < 4:
        print ("Error: first item has wrong size: "+PropValueTable[0])
        return []
    if line0[0]!='1':
        print ("Error: first item has wrong level (should be 1): "+PropValueTable[0])
        return []
    
    ParsedPropValueTable=[]
    for line in PropValueTable:
        line=line.strip().split()
        linelen=len(line)
        if linelen < 4:
            print ("Error: item has wrong size: "+' '.join(line))
            return []
        if line[linelen-1] not in ['REFERENCE','CONTENT','VALUE']:
            print ('Error: item has syntax problem (only BY REFERENCE, CONTENT or VALUE allowed): '+' '.join(line))
            return []
        ParsedPropValueTable.append([line[0],line[2]])
    return ParsedPropValueTable

def getChildCount(ParsedProperty,position):
    # Counts the number of child Cobol Data artifacts under the one specified
    PropertyLen=len(ParsedProperty)    
    if position+1 > PropertyLen or position < 0:
        # out of range
        return -1
    if position+1 == PropertyLen:
        # we are on last item of list
        return 0   
    
    startlevel=int(ParsedProperty[position][0])
    subleveltocount=int(ParsedProperty[position+1][0])
    
    samesublevel=True
    sublevelcount=0
    
    while samesublevel:
        position+=1
        if position > PropertyLen-1:
            break
        curlevel=int(ParsedProperty[position][0])
        if curlevel < startlevel or curlevel==1 or curlevel == startlevel:
            break
        if curlevel == subleveltocount:
            sublevelcount+=1
        else:
            samesublevel=False        
    return sublevelcount

def matchProperties(idclr, idcle, PropValueClr, PropValueCle):
    # Scans the USING property from the CALL USING Link on one side 
    # and from the called Procedure Division on the other side
    # and tries to find a cross-match for each items 
    # Output: table with matching items    
     
    ParsedPropertyClr=parseProperty(PropValueClr)
    ParsedPropertyCle=parseProperty(PropValueCle)
    
    if ParsedPropertyClr==[] or ParsedPropertyCle==[]:
        print ('General parsing error:')
        print (ParsedPropertyClr)
        print (ParsedPropertyCle)
        return []
    
    matcheditems=[]
    curclrpos=0
    curclepos=0
    curclrlevel=1
    curclelevel=1
    prevclrlevel=1
    prevclelevel=1    
    ResumeLevel=100000
    
    lenParsedPropertyClr=len(ParsedPropertyClr)
    lenParsedPropertyCle=len(ParsedPropertyCle)
    
    fnameclrprefixtab=[]
    fnamecleprefixtab=[]
    
    prevclrname=''
    prevclename=''
            
    while curclepos < lenParsedPropertyCle and curclrpos < lenParsedPropertyClr:
    
        prevclrlevel=curclrlevel
        prevclelevel=curclelevel
        
        clrname=ParsedPropertyClr[curclrpos][1]
        clename=ParsedPropertyCle[curclepos][1]
        
        curclrlevel=int(ParsedPropertyClr[curclrpos][0])
        curclelevel=int(ParsedPropertyCle[curclepos][0])
                
        if curclrlevel>prevclrlevel and prevclrname!='':
            fnameclrprefixtab.append(prevclrname)
        if curclelevel>prevclelevel and prevclename!='':
            fnamecleprefixtab.append(prevclename)
            
        if curclrlevel<prevclrlevel:
            fnameclrprefixtab=fnameclrprefixtab[:curclrlevel-prevclrlevel]
        if curclelevel<prevclelevel:
            fnamecleprefixtab=fnamecleprefixtab[:curclelevel-prevclelevel]        
           
        NbChildCle=getChildCount(ParsedPropertyCle,curclepos)
        NbChildClr=getChildCount(ParsedPropertyClr,curclrpos)

        if NbChildCle!=NbChildClr:
            ResumeLevel=curclelevel
        else:
            if ResumeLevel>=curclelevel and ResumeLevel>=curclrlevel:
                ResumeLevel=100000   
                
        if curclelevel==curclrlevel:
            
            if ResumeLevel>=curclelevel:
                
                clrfname='.'.join(fnameclrprefixtab)
                clefname='.'.join(fnamecleprefixtab)
                
                if clrfname=='':
                    clrfname=clrname
                else:
                    clrfname=clrfname+'.'+clrname 
                      
                if clefname=='':
                    clefname=clename
                else:
                    clefname=clefname+'.'+clename
                matcheditems.append([idclr,idcle,clrname,clename,clrfname,clefname])
            
            curclepos+=1
            curclrpos+=1
 
        elif curclelevel<curclrlevel:
            curclrpos+=1

        elif curclelevel>curclrlevel:
            curclepos+=1
        
        prevclrname=clrname
        prevclename=clename
          
    return matcheditems

    
    
# PropValueClr="""1 01 PAP-FE BY REFERENCE
# 2 10 PAP-FE-PMID X(16) BY REFERENCE
# 2 10 PAP-FE-NR-SECTION XXX BY REFERENCE
# """
# PropValueCle="""1 01 M-FE BYY REFERENCE
# 2 10 M-FE-PMID X(16) BY REFERENCE
# 2 10 M-FE-NR BY REFERENCE
# 3 15 M-FE-NR-SECTION XXX BY REFERENCE
# 4 88 M-FE-NR-SECTION-A00 BY REFERENCE
# 4 88 M-FE-NR-SECTION-B00 BY REFERENCE
# 4 88 M-FE-NR-SECTION-B10 BY REFERENCE
#"""

# matcheditems=matchProperties(375,392,PropValueClr,PropValueCle)
# cpt=0
# for line in matcheditems: 
#     print(matcheditems[cpt])
#     cpt+=1    