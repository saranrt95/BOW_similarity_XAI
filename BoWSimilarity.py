import pandas as pd
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import os

def ProcessRulesets(Ruleset1, Ruleset2, class_labels_dict):
    """ Given the rulesets, finds each rule premise ("Rule") and 
    consequence ("Class") and creates a single dataframe with both rulesets """
    def convert_litteral(classOut, class_labels_dict):
        return class_labels_dict[classOut]
        
    Ruleset1['Rule'] = Ruleset1.apply(lambda x: x[0][x[0].find('IF')+3:x[0].find('THEN')-1], axis=1)
    #Ruleset1['Class'] = Ruleset1.apply(lambda x: x[0][x[0].find('"')+1:x[0].find('"')+2], axis=1)
    Ruleset1['Class'] = Ruleset1.apply(lambda x: x[0].split('"')[1], axis=1)

    Ruleset1.drop(Ruleset1.columns[0] , axis=1, inplace=True)

    Ruleset2['Rule'] = Ruleset2.apply(lambda x: x[0][x[0].find('IF')+3:x[0].find('THEN')-1], axis=1)
    #Ruleset2['Class'] = Ruleset2.apply(lambda x: x[0][x[0].find('"')+1:x[0].find('"')+2], axis=1)
    Ruleset2['Class'] = Ruleset2.apply(lambda x: x[0].split('"')[1], axis=1)
    
    Ruleset2.drop(Ruleset2.columns[0] , axis=1, inplace=True)

    Ruleset_Tot = pd.concat([Ruleset1, Ruleset2], ignore_index=True)
    Ruleset_Tot['Class'] = Ruleset_Tot['Class'].apply(convert_litteral, args=(class_labels_dict,))
    return Ruleset_Tot

def ImportAndProcessRulesets(base_dir, rulefile1, rulefile2, rulesetIDlist, class_labels_dict):
    """ Import IF-THEN rulesets, in csv format;
    inputs:
    base_dir: workfolder with rulesets
    rulefile1, rulefile2: file names of the rulesets
    rulesetIDlist: 2-elements list with rulesets IDs (will fill 'Set' column)
    
    output:
    Dataframe with columns: Set (ruleset IDs), Rule (premise with conditions 
    in logical AND) and Class (output) ; 
    """ 
    # read csv rulesets
    Ruleset1 = pd.read_csv(base_dir+'/'+rulefile1, header=None) 
    Ruleset1['Set'] = rulesetIDlist[0]
    Ruleset2 = pd.read_csv(base_dir+'/'+rulefile2, header=None) 
    Ruleset2['Set'] = rulesetIDlist[1]
    # separate premise and consequence
    Ruleset = ProcessRulesets(Ruleset1, Ruleset2, class_labels_dict)
    return Ruleset


def UniqueConditionOccurrences(Ruleset):
    terms = []
    for index, value in Ruleset.loc[:,'Rule'].items():
        for r in value.split(' AND '):
            if r.find('>')>0:
                terms.append(r[:r.find('>')+2].replace(" ", ""))
            else:
                terms.append(r[:r.find('<')+2].replace(" ", ""))
    # counts unique occurrences
    counter = Counter(terms)
    return counter

def CreateFSandTcolumns(Ruleset, counter):
    # iterate on unique feature plus operator
    for c in counter:
      # index is the row of "Regola" column, value is the rule in the column
      for index, value in Ruleset.loc[:,'Rule'].items():
        # get single conditions of the rule and check the presence of condition c in them
        for r in value.split(' AND '):
          # r condition matches condition c (with operators > or >=)
          if r[:r.find('>')+2].replace(" ", "") == c:
            # set fs column to 1
            Ruleset.loc[index, c] = 1
            # set threshold column value to the threshold contained in r 
            Ruleset.loc[index, c+'Value'] = float(r.split('>')[1].strip())
          # same as above, for < or <= operators
          if r[:r.find('<')+2].replace(" ", "") == c:
            Ruleset.loc[index, c] = 1
            Ruleset.loc[index, c+'Value'] = float(r.split('<=')[1].strip())
    return Ruleset

def NormalizeThresholds(Ruleset, counter):
    for c in counter:
        # for condition c, for the rules in which it is present,
        # get the maximum and minimum threshold values
        MAX = Ruleset.loc[Ruleset[c] == 1, c+'Value'].max()
        MIN = Ruleset.loc[Ruleset[c] == 1, c+'Value'].min()
        denominatore = MAX-MIN
        # iterate over the rules
        for index, value in Ruleset.loc[:,c+'Value'].items():
            # check presence of c in current rule
            if Ruleset.loc[index, c] == 1:
              # max = min
                if denominatore == 0:
                    Ruleset.loc[index, c+'ValueNorm'] = 1
                      # max != min
                else:  
                    Ruleset.loc[index, c+'ValueNorm'] = (Ruleset.loc[index, c+'Value']-MIN)/denominatore
            # c is not present in current rule
            else:
                Ruleset.loc[index, c+'Value'] = 0
    # once completed, delete non normalized values
    for c in counter:
        del Ruleset[c+'Value']
    return Ruleset

def buildBOW(Ruleset, outfilename, save_res = True):
    # get unique set of rules conditions (no repetititions)
    counter = UniqueConditionOccurrences(Ruleset)
    # 1. INITIALIZE BOW MATRIX
    # initialize Ruleset with 3 new zeros columns for each element in counter:
    # - column i with feature plus operator (fs)
    # - fsValue (original threshold value)
    # - fsValueNorm (normalized threshold value)
    for i in counter:
        #print(i)
        Ruleset.loc[:,i]= 0
        Ruleset[i+'Value']=0.0
        Ruleset[i+'ValueNorm']=0.0
   
    # 2. FILL BOW MATRIX (threshold values not normalized)
    Ruleset = CreateFSandTcolumns(Ruleset, counter)
       
    # 3. NORMALIZE THRESHOLDS 
    Ruleset = NormalizeThresholds(Ruleset, counter)
    
    # 4. Save to excel in current path
    if save_res:
        Ruleset.to_excel(outfilename, index=True)
    # 5. Convert FS and T columns in Ruleset from DataFrame to numpy array
    # this is the proper BoW matrix ("Set","Rule" and "Class" are no more considered)
    bow_matrix = Ruleset.iloc[:,3:Ruleset.shape[1]].to_numpy()
    
    return bow_matrix


def BoW_Similarity(bow_matrix, Ruleset, outfilename, save_res=True):  
    BowSim = cosine_similarity(bow_matrix, bow_matrix)
    RuleSimilarities = pd.DataFrame(BowSim,
                       index = Ruleset['Set'] + ' - ' + Ruleset['Class'] + ' - ' + Ruleset['Rule'],
                       columns = Ruleset['Set'] + ' - ' + Ruleset['Class'] + ' - ' + Ruleset['Rule'])
    if save_res:
        RuleSimilarities.to_excel(outfilename, index=True)
    return RuleSimilarities


