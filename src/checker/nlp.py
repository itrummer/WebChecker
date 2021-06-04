'''
Created on Jun 3, 2021

@author: immanueltrummer
'''
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class EntailmentUtil():
    """ Methods for checking entailment. """
    
    def __init__(self):
        """ Initialize models for entailment checks. """
        self.tokenizer = AutoTokenizer.from_pretrained('roberta-large-mnli')
        self.model = AutoModelForSequenceClassification.from_pretrained(
            'roberta-large-mnli')
        
    def entails_hp(self, sentence_1, sentence_2):
        """ Entailment check with high precision. 
        
        Args:
            sentence_1: check if this sentence entails other sentence
            sentence_2: check if this sentence is entailed
            
        Returns:
            True iff first sentence entails second sentence
        """
        e = self.tokenizer(sentence_1 + '. ' + sentence_2, 
                           return_tensors='pt', truncation=True)
        s = torch.softmax(self.model(**e).logits, dim=1).tolist()[0]
        return True if s[2] > 0.5 else False
    
    def entails_lp(self, sentence_1, sentence_2):
        """ Cheap and imprecise entailment check. 
        
        Args:
            sentence_1: check if this sentence entails the other
            sentence_2: check if this sentence is entailed by first
            
        Returns:
            True iff first sentence possibly entails second
        """
        overlap_ctr = 0
        for word_2 in sentence_2.split():
            if word_2 in sentence_1:
                overlap_ctr += 1
        
        nr_words_2 = len(sentence_2.split())
        if overlap_ctr > nr_words_2 * 0.5:
            return True
        else:
            return False
        
    def entails(self, sentence_1, sentence_2, pipeline_id):
        """ Executes a sequence of entailment checks. 
        
        Args:
            sentence_1: check if this sentence entails other
            sentence_2: check if this sentence is entailed
            pipeline_id: describes sequence of checks
            
        Returns:
            True iff all checks succeed
        """
        if pipeline_id == 0:
            return self.entails_hp(sentence_1, sentence_2)
        else:
            if self.entails_lp(sentence_1, sentence_2):
                return self.entails_hp(sentence_1, sentence_2)
            else:
                return False