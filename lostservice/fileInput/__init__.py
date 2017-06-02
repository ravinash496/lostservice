
def getxmldatafile():

    #print (r"c:\testpython\first.xml")
    file = open(r"c:\testpython\first.xml","r")
    data = file.read()
    file.close()
    return data