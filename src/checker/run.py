'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import argparse
import checker.akb
import checker.nlp
import checker.web


# Login data can be retrieved at https://programmablesearchengine.google.com/
parser = argparse.ArgumentParser(description='Simple test for WebChecker')
parser.add_argument('key', type=str, help='Specify the Google API key')
parser.add_argument('cse', type=str, help='Specify SE ID')
args = parser.parse_args()
print(args)

akb = checker.akb.Access('/Users/immanueltrummer/Papers/WebChecker/akb_numbers.tsv')
entailment = checker.nlp.EntailmentUtil()
matches = []

for i in range(10):
    
    print(f'Iteration number {i}')
    
    triple = akb.next_triple()
    query = triple[0] + ' ' + triple[1] + ' "'+ triple[2] + '"'
    print(f'Checking with query "{query}"')
    web_result = checker.web.gsearch_lines(query, args.key, args.cse)
    
    for l in web_result.loc[:, 'sentence']:
        af = triple[0] + ' ' + triple[1] + ' ' +triple[2]
        if entailment.entails_lp(l, af):
            print(f'Satisfies low-precision check: {l}')
            if entailment.entails_hp(l, af):
                print(f'Entails anti-fact: {l}')
                matches.append((af, l))
            else:
                print(f'Does not entail anti-fact.')
                
print(matches)