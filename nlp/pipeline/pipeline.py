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
from util import timeit, log

class TopicModeller(object):


    def __init__(self, file_name: str = None, df: pd.DataFrame() = None):
        self.data = None
        if file_name is not None:
            self.data = pd.read_csv(file_name)
        if df is not None:
            self.data = df
        if self.data is None:
            raise FileNotFoundError(f'Data not defined!')


    @timeit
    def process(self, clean : bool = True, normalize : bool = True, lemma: str = 'nltk', texts : list = []):
        """
        Cleaning and normalizing.
        :param clean:
        :param normalize:
        :param get_date:
        :return:
        """
        print('Starting processing')
        # cleaning
        if texts == []:
            if clean:
                print('Cleaning')
                self.data.loc[:, 'cleaned_text'] = self.data['text'].apply(
                lambda x: preprocess.clean_text(x, russian_words_only=False, remove_stop=True))
            else:
                self.data.loc[:, 'cleaned_text'] = self.data['text']
    #
            if normalize:
                print('Normalizing')
                normalizer = Normalizer(lemma=lemma)
                self.data.loc[:, 'tokenized_text'] = self.data['cleaned_text'].apply(
                    lambda x: normalizer.normalize(x, return_tokenized=True, simple_tokenize=False))

        else:
            if clean:
                print('Cleaning')
                texts = [preprocess.clean_text(i, russian_words_only=False, remove_stop=True) for i in texts]
            #
            if normalize:
                print('Normalizing')
                normalizer = Normalizer(lemma=lemma)
                texts = [normalizer.normalize(i, return_tokenized=True, simple_tokenize=False) for i in texts]
            return texts


    @timeit
    def prepare_data_gensim(self, dict_path : str, no_below=1, no_above=0.9, keep_n=9999999999):
        """
        Preparing data for modelling.
        :param model_type:
        :param vwpath:
        :return:
        """
        self.dictionary = corpora.Dictionary(self.data['tokenized_text'].values)
        self.doc_term_matrix = [self.dictionary.doc2bow(doc) for doc in self.data['tokenized_text'].values]
        self.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
        if dict_path is not None:
            self.dictionary.save(dict_path)


    @timeit
    def prepare_data_bigartm(self, vwpath: str = 'data/lenta.vw'):
        """
        Preparing data for modelling.
        :param vwpath:
        :return:
        """
        self.data['docID'] = list(range(self.data.shape[0]))
        with open(vwpath, 'w') as fp:
            for text, did in self.data[['tokenized_text', 'docID']].values:
                fp.write('{} |default {}\n'.format(did, ' '.join(text)))

        batches_path = 'data/batches'
        self.batch_vectorizer = artm.BatchVectorizer(data_path=vwpath,
                                                data_format='vowpal_wabbit',
                                                target_folder=batches_path)
        self.dictionary = artm.Dictionary()
        self.dictionary.gather(data_path=batches_path)


    @timeit
    def build_model_gensim(self,
                    params : dict = {'num_topics':17, 'passes':5, 'alpha':'auto', 'eta':None,
                             'random_state':42},
                    print_score : bool = True, model_path : str = 'lda.model'):
        """
        Building model
        :param params:
        :param print_score:
        :return:
        """
        model = LdaModel(self.doc_term_matrix, id2word=self.dictionary, **params)

        if print_score:
            perplexity = model.log_perplexity(self.doc_term_matrix)
            coherence_model_lda = CoherenceModel(model=model, texts=self.data['tokenized_text'].values,
                                                 dictionary=self.dictionary, coherence='c_v')
            coherence_lda = coherence_model_lda.get_coherence()
            print(f'Perplexity: {perplexity}')
            print(f'Coherence Score: {coherence_lda}')

        self.model = model
        if model_path is not None:
            self.model.save(model_path)


    @timeit
    def build_model_bigartm(self, num_topics : int):
        """

        :param num_topics:
        :return:
        """
        model = artm.ARTM(num_topics = num_topics, dictionary = self.dictionary)
        model.scores.add(artm.PerplexityScore(name='perplexity_score',
                                              dictionary=self.dictionary))
        model.fit_offline(batch_vectorizer=self.batch_vectorizer, num_collection_passes=params['passes'])
        self.model = model

    @timeit
    def visualize(self, vis_type : str = 'pyLDAvis', save_file : str = 'vis.html'):
        """

        :param vis_type:
        :param save_file:
        :return:
        """
        if vis_type == 'pyLDAvis':
            panel = pyLDAvis.gensim.prepare(self.model, self.doc_term_matrix, self.dictionary, mds='tsne')
            if save_file is not None:
                pyLDAvis.save_html(panel, save_file)

            return panel

        if vis_type == 'Pygal':
            pgv = visualizer.TopicVisualizerPygal(data, topic_cols, topic_names=topic_names)
            pgv.draw()
            pgv.save(save_file)

    @timeit
    def extract_topics_gensim(self, texts : list = []):
        """
        :param texts:
        :return:
        """
        log(len(texts))
        if texts != []:
            texts = self.process(texts=texts)
            corpus = [self.dictionary.doc2bow(text) for text in texts]
            return [self.model[i] for i in corpus]
        else:
            return [self.model.get_document_topics(i) for i in self.doc_term_matrix]

    @timeit
    def update_gensim_model(self, texts : list = []):
        """

        :param texts:
        :return:
        """
        texts = self.process(texts=texts)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        self.model.update(corpus)

