from dataclasses import dataclass
import torch
import numpy as np

@dataclass
# 1. We take in a sentence and its tags
# 2. We tokenize the sentence using the tokenizer
# 3. We create a list of tags for each word in the sentence
# 4. We create a list of tags for each token in the sentence
# 5. We create a list of tags for each subtoken in the sentence
# 6. We return a dictionary of the tokenized sentence, the list of tags for each word, and the list of
# tags for each subtoken
class PreDataCollator:
    
    def __init__(self, tokenizer, max_len, tags_to_ids):

        self.tokenizer = tokenizer
        self.max_len = max_len
        self.tags_to_ids = tags_to_ids
        
    
    def __call__(self, batch):
        
        input_ids = []
        attention_mask = []
        labels = []
        
        for sent,tag in zip(batch['tokens'],batch['labels']):  # was sentences before
            
            tokenized = self.tokenize(sent,tag)
            input_ids.append(tokenized['input_ids'])
            attention_mask.append(tokenized['attention_mask'])
            labels.append(tokenized['labels'])
            
        
        
        batch = {'input_ids':input_ids,'attention_mask':attention_mask, 'labels':labels}
        

        return batch

    def tokenize(self, sentence, tags):
        
        # getting the sentences and word tags
        
        #sentence = sentence.strip().split()  
        #word_tags = tags.upper().split() 
        word_tags = tags[:]

        # using tokenizer to encode sentence (includes padding/truncation up to max length)
        # BertTokenizerFast provides "return_offsets_mapping" functionality for individual tokens, so we know the start and end of a token divided into subtokens
        encoding = self.tokenizer(sentence,
                             is_split_into_words=True, 
                             return_offsets_mapping=True, 
                             padding='max_length', 
                             truncation=True, 
                             max_length=self.max_len)

        # creating token tags only for first word pieces of each tokenized word
        tags = [self.tags_to_ids[tag] for tag in word_tags]
        # code based on https://huggingface.co/transformers/custom_datasets.html#tok-ner
        # creating an empty array of -100 of length max_length
        encoded_tags = np.ones(len(encoding["offset_mapping"]), dtype=int) * -100

        # setting only tags whose first offset position is 0 and the second is not 0
        
        i = 0
        for idx, mapping in enumerate(encoding["offset_mapping"]):
            if mapping[0] == 0 and mapping[1] != 0:
                # overwrite the tag
                try:
                    encoded_tags[idx] = tags[i]
                    i += 1
                except:
#                     print(encoding["offset_mapping"])
#                     print(i)
                    print(sentence)
#                     print(len(tags), tags[i])
            

        # turning everything into PyTorch tensors
        item = {key: torch.as_tensor(val) for key, val in encoding.items()}
        item['labels'] = torch.as_tensor(encoded_tags)

        return item
