import re
from datetime import datetime
import spacy
from mrjob.job import MRJob
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from contractions import CONTRACTION_MAP

nlp = spacy.load("en_core_web_sm")
stopword_list = stopwords.words('english')
stopword_list.remove('no')
stopword_list.remove('not')


class MR_Preprocess(MRJob):

    def remove_special_characters(self, text, remove_digits=True):
        pattern = r'[^a-zA-z0-9\s]' if not remove_digits else r'[^a-zA-z\s]'
        text = re.sub(pattern, '', text)
        return text

    def simple_tokenizer(self, text):
        tokens = []
        tokens = text.split()
        tokens = [token.strip() for token in tokens]
        return tokens

    def expand_contractions(self, text, contraction_mapping=CONTRACTION_MAP):
        contractions_pattern = re.compile('({})'.format('|'.join(contraction_mapping.keys())),
                                          flags=re.IGNORECASE | re.DOTALL)

        def expand_match(contraction):
            match = contraction.group(0)
            first_char = match[0]
            expanded_contraction = contraction_mapping.get(match) \
                if contraction_mapping.get(match) \
                else contraction_mapping.get(match.lower())
            expanded_contraction = first_char + expanded_contraction[1:]
            return expanded_contraction

        expanded_text = contractions_pattern.sub(expand_match, text)
        expanded_text = re.sub("'", "", expanded_text)
        return expanded_text

    def remove_repeated_characters(self, tokens):
        repeat_pattern = re.compile(r'(\w*)(\w)\2(\w*)')
        match_substitution = r'\1\2\3'

        def replace(old_word):
            if wn.synsets(old_word):
                return old_word
            new_word = repeat_pattern.sub(match_substitution, old_word)
            return replace(new_word) if new_word != old_word else new_word

        correct_tokens = [replace(word) for word in tokens]
        return correct_tokens

    def remove_stopwords(self, tokens):
        filtered_tokens = [token for token in tokens if token not in stopword_list]
        return filtered_tokens

    def lemmatize_text(self, text):
        text = nlp(text)
        text = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text
                         for word in text])
        return text

    def mapper(self, _, line):
        line = self.expand_contractions(line)
        line = self.remove_special_characters(line)
        line = line.lower()
        line = self.lemmatize_text(line)
        tokens = self.simple_tokenizer(line)
        tokens = self.remove_repeated_characters(tokens)
        tokens = self.remove_stopwords(tokens)
        processed_rev = ' '.join(tokens)

        yield (processed_rev), None


if __name__ == '__main__':
    start_time = datetime.now()
    MR_Preprocess.run()
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print("Total Executing Time : ",elapsed_time)
