import pandas as pd
import preprocess
from normalizer import Normalizer
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.models import CoherenceModel, LdaMulticore
import pyLDAvis.gensim
from gensim.models.phrases import Phrases, Phraser
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
# from visualizer import TopicVisualizer
#import artm
import scipy.sparse as ss
from corextopic import corextopic as ct
from corextopic import vis_topic as vt
import pickle
from util import timeit, log

class TopicModeller(object):


    def __init__(self, file_name: str = None, df: pd.DataFrame() = None):
        """
        Init.

        You can pass a csv file name to read it with pandas or a prepared
        pandas DataFrame

        """
        self.data = None
        if file_name is not None:
            self.data = pd.read_csv(file_name)
        if df is not None:
            self.data = df
        if self.data is None:
            raise FileNotFoundError('Data not defined!')


    @timeit
    def process(self, clean : bool = True, normalize : bool = True, lemma: str = 'nltk', texts : list = [],
                ngram : int = 1):
        """
        Cleaning and normalizing data.

        Can process DataFrame which was defined earlier or a list of texts.

        :param clean: clean text or not
        :param normalize: normalize text or not
        :param lemma: lemmatizator. Currently 'nltk', 'pymorphy' and 'mystem' are supported.
        :param texts: can be passed to be processed instead of DataFrame.
        :param ngram: if > 1 creates ngrams.

        :return: processed texts if texts were passed
        """
        print('Starting processing')

        if texts == []:
            if clean:
                print('Cleaning')
                self.data.loc[:, 'cleaned_text'] = self.data['text'].apply(
                lambda x: preprocess.clean_text(x, russian_words_only=True, remove_stop=True))
            else:
                self.data.loc[:, 'cleaned_text'] = self.data['text']
    #
            if ngram > 1:
                self.ngrams = []
                print('Creating ngrams')
                text_list = self.data.loc[:, 'cleaned_text'].values.copy()
                for i in range(ngram):
                    text_list, ngram = self.generate_ngram(text_list)
                    self.ngrams.append(ngram)

                self.data.loc[:, 'cleaned_text'] = text_list

            if normalize:
                print('Normalizing')
                normalizer = Normalizer(lemma=lemma)
                self.data.loc[:, 'tokenized_text'] = self.data['cleaned_text'].apply(
                    lambda x: normalizer.normalize(x, return_tokenized=True, simple_tokenize=False))

        else:
            if clean:
                print('Cleaning')
                texts = [preprocess.clean_text(i, russian_words_only=True, remove_stop=True) for i in texts]

            if ngram > 1:
                print('Creating ngrams')
                for ngram_func in self.ngrams:
                    texts = [ngram_func[line] for line in texts]

            if normalize:
                print('Normalizing')
                normalizer = Normalizer(lemma=lemma)
                texts = [normalizer.normalize(i, return_tokenized=True, simple_tokenize=False) for i in texts]
            return texts


    @timeit
    def prepare_data_gensim(self, dict_path : str = '', no_below=1, no_above=0.9, keep_n=9999999999):
        """
        Preparing data for modelling with gensim.

        """
        self.dictionary = corpora.Dictionary(self.data['tokenized_text'].values)
        self.doc_term_matrix = [self.dictionary.doc2bow(doc) for doc in self.data['tokenized_text'].values]
        self.dictionary.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
        if dict_path is not None:
            self.dictionary.save(dict_path)


    @timeit
    def prepare_data_bigartm(self, vwpath: str = 'data/lenta.vw'):
        """
        Preparing data for modelling with bigartm.
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
    def prepare_data_corex(self, dict_path : str = '', no_below=1, no_above=0.9, keep_n=9999999999):
        """
        Preparing data for modelling with corex.

        """
        self.data['text_join'] = self.data['tokenized_text'].apply(lambda x: ' '.join(x))
        vectorizer = CountVectorizer()
        doc_word = vectorizer.fit_transform(self.data.text_join)

        # делаем спарс-матрцу
        doc_word = ss.csr_matrix(doc_word)
        words = list(np.asarray(vectorizer.get_feature_names()))
        self.corex_words = words
        self.doc_word = doc_word


    @timeit
    def build_model_gensim(self,
                    params : dict = {},
                    print_score : bool = True, model_path : str = 'lda.model'):
        """
        Building gensim model.

        :param params: model params
        :param print_score: print scores or not
        :param model_path: save model in this path
        :return:
        """
        if params == {}:
            params = {'num_topics': 17, 'passes': 5, 'alpha': 'auto', 'eta': None,
                             'random_state': 42}

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
        Building bigartm model.

        :param num_topics:
        :return:
        """
        model = artm.ARTM(num_topics = num_topics, dictionary = self.dictionary)
        model.scores.add(artm.PerplexityScore(name='perplexity_score',
                                              dictionary=self.dictionary))
        model.fit_offline(batch_vectorizer=self.batch_vectorizer, num_collection_passes=params['passes'])
        self.model = model


    @timeit
    def build_model_corex(self, num_topics : int):
        """
        Build model with corex
        :param num_topics:
        :return:
        """
        model = ct.Corex(n_hidden=num_topics,
                               words=self.corex_words,
                               max_iter=33,
                               verbose=0,
                               seed=1)
        model.fit(self.doc_word, words=self.corex_words)
        self.model = model

    @timeit
    def visualize(self, vis_type : str = 'pyLDAvis', save_file : str = 'vis.html'):
        """
        Visualizations.

        :param vis_type: type of visualization.
        :param save_file: save model in this file
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
            if save_file is not None:
                pgv.save(save_file)

    @timeit
    def extract_topics_gensim(self, texts : list = [], load_dict : str = '', doc_term_matrix = None):
        """
        Extract topics from the texts.

        Pass texts and extract topics from them using gensim model.

        :param texts: pass texts. Or you can pass doc_term_matrix
        :param load_dict: if string is passed, load dictionary with this filename
        :return:
        """
        if load_dict != '':
            self.dictionary = Dictionary.load('dict.dictionary')

        log(len(texts))
        if texts != []:
            texts = self.process(texts=texts)
            corpus = [self.dictionary.doc2bow(text) for text in texts]
            return [self.model[i] for i in corpus]
        elif doc_term_matrix:
            return [self.model.get_document_topics(i) for i in doc_term_matrix]
        else:
            return [self.model.get_document_topics(i) for i in self.doc_term_matrix]

    @timeit
    def update_gensim_model(self, texts : list = []):
        """
        Train gensim model on additional texts.

        :param texts:
        :return:
        """
        texts = self.process(texts=texts)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        self.model.update(corpus)


    @timeit
    def generate_ngram(self, text_list):
        """
        Generate ngram using gensim Phreses
        :param text_list:
        :return:
        """
        ngram = Phrases(text_list, min_count=5, threshold=10.0,
                        max_vocab_size=40000000, delimiter=b'_',
                        progress_per=10000, scoring='default',
                        common_terms=frozenset())
        ngrammed = [ngram[line] for line in text_list]
        return ngrammed, ngram