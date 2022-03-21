import pandas as pd
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import os

from BoWSimilarity import *

# FATIGUE APPLICATION
# input parameters for fatigue application
# work directory
base_dir = os.getcwd()
# names of the rulesets; CSV files should be rules in if-then format and without covering/error stats
rulefile1 = 'over40_shortened_rules.csv'
rulefile2 = 'under40_shortened_rules.csv'
# couple of IDs for the considered rulesets
rulesetIDlist = ['Over 40', 'Under 40']
# dict to associate, if needed, class labels as appear in the rules with more self-explicatory names
# if it is not needed, set key = value for each class
class_labels_dict = {"1":"Fatigued", "0":"Non fatigued"} # FISSO
# output files (if save_res is True, see later)
outputBoW="BagOfWords_fatica_fromshell.xlsx"# possono automatizzarsi in base agli id
outputRuleSim="BoWSimilarity_fatica_fromshell.xlsx"

# START (similarity between 2 rulesets)
# 	import and pre-process the rulesets before building the BoW matrix
Ruleset = ImportAndProcessRulesets(base_dir, rulefile1, rulefile2, rulesetIDlist, class_labels_dict)
print(Ruleset)
# compute BoW matrix
BoW_matrix = buildBOW(Ruleset, outputBoW, save_res = True)
# compute rule similarity
rulesimilarity = BoW_Similarity(BoW_matrix, Ruleset, outputRuleSim, save_res=True)

# PLATOONING APPLICATION
# input parameters for platooning
# work directory
base_dir = os.getcwd()
# names of the rulesets; CSV files should be rules in if-then format and without covering/error stats
rulefile1 = 'PERhigh_rules.csv'
rulefile2 = 'PERlow_rules.csv'
rulesetIDlist = ['PER high', 'PER low']

# dict to associate, if needed, class labels as appear in the rules with more self-explicatory names
# if it is not needed, set key = value for each class
class_labels_dict = {"1 collision":"Collision", "0 safe":"Non Collision"}# fisso per ogni coppia; 

# output files (if save_res is True, see later)
outputBoW="BagOfWords_plato_fromshell.xlsx"# possono automatizzarsi in base agli id
outputRuleSim="BoWSimilarity_plato_fromshell.xlsx"

# START (similarity between 2 rulesets)
# 	import and pre-process the rulesets before building the BoW matrix
Ruleset = ImportAndProcessRulesets(base_dir, rulefile1, rulefile2, rulesetIDlist, class_labels_dict)
print(Ruleset)
# compute BoW matrix
BoW_matrix = buildBOW(Ruleset, outputBoW, save_res = True)
# compute rule similarity
rulesimilarity = BoW_Similarity(BoW_matrix, Ruleset, outputRuleSim, save_res=True)