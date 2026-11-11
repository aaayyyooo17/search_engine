import json
import numpy as np
from scipy import sparse 


#dictonary aller verlinkungen
outLinks = None
#anzahl an sich verlinkender seiten = len(outLinks)
num = None
#google konstante
m = 0.15
#m/num
n = None

def calculatePageRank():
    global  outLinks
    global num
    global n
    
    outLinks = readLinks()
    num = len(outLinks)
    n = m/num

    A = createMatrix()
    x = calculateEV(A)
    ranks = {str(i+1):x[i] for i in range(num)}

    pageRank = dict(sorted(ranks.items(), key=lambda item: item[1],reverse = True))

    writeEV(pageRank)
    #writeEV(ranks)



def readLinks():

  with open("links.json", "r", encoding="utf-8") as f:
      daten = json.load(f)

  return daten



   
def createMatrix():

  values = []
  row = []
  col = []

  for i in range(num):

    try: 
      values += [1/len(outLinks[str(i+1)])]*len( outLinks[str(i+1)])
      col += [i]*len( outLinks[str(i+1)])
      for s in outLinks[str(i+1)]:
        row.append(s-1) 
    except ZeroDivisionError:
      #if there are no links going out
      print("catched")
      values+= [1/num]*num
      col += [i]*num
      row.extend(range(num))
   

  matrixA = sparse.coo_matrix((values, (row, col)), shape=(num, num))
  return matrixA


def calculateEV(matrixM):

  x =  np.ones(num)/num

   # M = (1−m)A + m/N B
  for i in range(1000):
      y = x
      x = (1-m)*(matrixM @ x) 
      x += n*np.sum(x)
      x = x/np.sum(x)

      if np.linalg.norm(x - y, ord=1) < 10**-8:
              print("breaked at iteration:",i)
              break
  
  return x/np.sum(x)


def writeEV(ev):
   with open("ranks.json", "w", encoding="utf-8") as f:
    
        json.dump(ev, f, ensure_ascii=False, indent = 4)

if __name__ == "__main__":
  calculatePageRank()
