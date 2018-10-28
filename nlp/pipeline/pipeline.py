import pandas as pd
import preprocess
from normalizer import Normalizer
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.models import CoherenceModel, LdaMulticore
import pyLDAvis.gensim
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from visualizer import TopicVisualizer
#import artm

class TopicModeller(object):

    def __init__(self, file_name: str):
        self.data = pd.read_csv(file_name)

    def process(self, clean : bool = True, normalize : bool = True, get_date : bool = True, lemma: str = 'nltk'):
        """
        Cleaning and normalizing.
        :param clean:
        :param normalize:
        :param get_date:
        :return:
        """

        # cleaning
        if clean:
            print('Cleaning')
            self.data.loc[:, 'cleaned_text'] = self.data['text'].apply(
            lambda x: preprocess.clean_text(x, russian_words_only=False, remove_stop=True))
#
        if normalize:
            print('Normalizing')
            normalizer = Normalizer(lemma=lemma)
            #normalized_text = normalizer.normalize(list(self.data['cleaned_text'].values), return_tokenized=True)
            #self.data.loc[:, 'tokenized_text'] = normalized_text
            self.data.loc[:, 'tokenized_text'] = self.data['text'].apply(
                lambda x: normalizer.normalize(x, return_tokenized=True))

        # Извлечение даты из текста ссылки
        if get_date:
            self.data['date'] = self.data['url'].apply(lambda x: pd.to_datetime('-'.join(x.split('/')[4:7])))
            self.data['year_month'] = self.data['date'].values.astype('datetime64[M]')

    def prepare_data(self, model_type : str = 'gensim_lda', vwpath : str = 'data/lenta.vw'):
        """
        Preparing data for modelling.
        :param model_type:
        :param vwpath:
        :return:
        """

        if model_type == 'gensim_lda':
            self.dictionary = corpora.Dictionary(self.data['tokenized_text'].values)
            self.doc_term_matrix = [self.dictionary.doc2bow(doc) for doc in self.data['tokenized_text'].values]

        elif model_type == 'sklearn_lda':
            tf_vectorizer = CountVectorizer()
            self.doc_term_matrix = tf_vectorizer.fit_transform(self.data['tokenized_text'].values)

        #　should work, but didn't test
        # elif model_type == 'BigARTM':
        #     self.data['docID'] = list(range(self.data.shape[0]))
        #     with open(vwpath, 'w') as fp:
        #         for text, did in self.data[['tokenized_text', 'docID']].values:
        #             fp.write('{} |default {}\n'.format(did, ' '.join(text)))
        #
        #     batches_path = 'data/batches'
        #     self.batch_vectorizer = artm.BatchVectorizer(data_path=vwpath,
        #                                             data_format='vowpal_wabbit',
        #                                             target_folder=batches_path)
        #     self.dictionary = artm.Dictionary()
        #     self.dictionary.gather(data_path=batches_path)

        self.model_type = model_type


    def build_model(self,
                    params : dict = {'num_topics':17, 'passes':5, 'alpha':'auto', 'eta':None,
                             'random_state':42},
                    print_score : bool = True):
        """
        Building model
        :param params:
        :param print_score:
        :return:
        """

        if self.model_type == 'gensim_lda':
            model = LdaModel(self.doc_term_matrix, id2word=self.dictionary, **params)

        elif self.model_type == 'sklearn_lda':
            # parameters which were in the notebook
            # lda = LatentDirichletAllocation(
            #     n_components=30,
            #     max_iter=7,
            #     learning_method='online',
            #     random_state=42)
            model = LatentDirichletAllocation(**params)

            model.fit_transform(self.doc_term_matrix)

        # elif self.model_type == 'BigARTM':
        #     model = artm.ARTM(num_topics=params['num_topics'], dictionary=self.dictionary)
        #     model.scores.add(artm.PerplexityScore(name='perplexity_score',
        #                                           dictionary=self.dictionary))
        #     model.fit_offline(batch_vectorizer=self.batch_vectorizer, num_collection_passes=params['passes'])

        if print_score & (self.model_type == 'gensim_lda'):
            perplexity = model.log_perplexity(self.doc_term_matrix)
            coherence_model_lda = CoherenceModel(model=model, texts=self.data['tokenized_text'].values,
                                                 dictionary=self.dictionary, coherence='c_v')
            coherence_lda = coherence_model_lda.get_coherence()
            print(f'Perplexity: {perplexity}')
            print(f'Coherence Score: {coherence_lda}')

        elif print_score & (self.model_type == 'sklearn_lda'):
            # Log Likelyhood: Higher the better
            print("Log Likelihood: ", model.score(self.doc_term_matrix))
            # Perplexity: Lower the better. Perplexity = exp(-1. * log-likelihood per word)
            print("Perplexity: ", model.perplexity(self.doc_term_matrix))

        self.model = model

    def visualize(self, vis_type : str = 'pyLDAvis', save_file : str = 'vis.html'):

        if vis_type == 'pyLDAvis':
            panel = pyLDAvis.gensim.prepare(self.model, self.doc_term_matrix, self.dictionary, mds='tsne')
            if save_file is not None:
                pyLDAvis.save_html(panel, save_file)

            return panel

        # if vis_type == 'Pygal':
        #     pgv = visualizer.TopicVisualizerPygal(data, topic_cols, topic_names=topic_names)
        #     pgv.draw()
        #     pgv.save(save_file)

    """
    Возможность вывести частотные графики
    
    """