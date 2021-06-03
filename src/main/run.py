'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import argparse

# Login data can be retrieved at https://programmablesearchengine.google.com/
parser = argparse.ArgumentParser(description='Simple test for WebChecker')
parser.add_argument('key', type=str, help='Specify the Google API key')
parser.add_argument('cse', type=str, help='Specify SE ID')
args = parser.parse_args()
print(args)

