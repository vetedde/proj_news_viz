import pandas as pd
import preprocess
from normalizer import Normalizer
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.models import CoherenceModel
import pyLDAvis.gensim
from gensim.models.phrases import Phrases, Phraser
from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
# from visualizer import TopicVisualizer
#import artm
import scipy.sparse as ss
# from corextopic import corextopic as ct
# from corextopic import vis_topic as vt
import pickle
from util import timeit, log
import tm_functions
import matplotlib.pyplot as plt
from flashtext import KeywordProcessor

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
                ngram : int = 1, clean_ner : bool = False):
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
        stopwords = []
        with open('stopwords.txt', 'r', encoding='utf-8') as f:
            for w in f.readlines():
                stopwords.append(w.strip())

        if texts == []:
            if clean:
                print('Cleaning')
                self.data.loc[:, 'cleaned_text'] = self.data['text'].apply(
            lambda x: preprocess.clean_text(x, russian_words_only=False))
            else:
                self.data.loc[:, 'cleaned_text'] = self.data['text']

            if clean_ner:
                print('Cleaning ners')
                with open('data/cleaned_name.pickle', 'rb') as handle:
                    dict_cleaned_name = pickle.load(handle)
                kp = KeywordProcessor()
                kp.add_keywords_from_dict(dict_cleaned_name)
                clean_text = self.data['cleaned_text'].apply(lambda x: kp.replace_keywords(' '.join(x)).split(' '))
                self.data['cleaned_text'] = clean_text

            if ngram > 1:
                self.ngrams = []
                print('Creating ngrams')
                text_list = [i for i in self.data.loc[:, 'cleaned_text'].values]
                for i in range(ngram):
                    # print(i)
                    text_list, ngram = self.generate_ngram(text_list)
                    self.ngrams.append(ngram)

                self.data.loc[:, 'cleaned_text'] = text_list


            if normalize:
                print('Normalizing')
                normalizer = Normalizer(lemma=lemma)
                self.data.loc[:, 'tokenized_text'] = self.data['cleaned_text'].apply(
                    lambda x: normalizer.normalize(x, return_tokenized=True, simple_tokenize=False))

            print('Removing stopwords')

            self.data.loc[:, 'tokenized_text'] = self.data['tokenized_text'].apply(lambda x: [i for i in x if i not in stopwords])

        else:
            if clean:
                print('Cleaning')
                texts = [preprocess.clean_text(i, russian_words_only=False)
                         for i in texts]

            if clean_ner:
                with open('data/cleaned_name.pickle', 'rb') as handle:
                    dict_cleaned_name = pickle.load(handle)

                kp = KeywordProcessor()
                kp.add_keywords_from_dict(dict_cleaned_name)
                texts = [kp.replace_keywords(line) for line in texts]

            if ngram > 1:
                print('Creating ngrams')
                for ngram_func in self.ngrams:
                    texts = [ngram_func[line] for line in texts]

            if normalize:
                print('Normalizing')
                normalizer = Normalizer(lemma=lemma)
                texts = [normalizer.normalize(i, return_tokenized=True, simple_tokenize=False) for i in texts]
            texts = [[w for w in line if w not in stopwords] for line in texts]
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
    # def build_model_corex(self, num_topics : int):
    #     """
    #     Build model with corex
    #     :param num_topics:
    #     :return:
    #     """
    #     model = ct.Corex(n_hidden=num_topics,
    #                            words=self.corex_words,
    #                            max_iter=33,
    #                            verbose=0,
    #                            seed=1)
    #     model.fit(self.doc_word, words=self.corex_words)
    #     self.model = model

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
    def extract_topics_gensim(self, texts: list = [], load_dict: str = '', doc_term_matrix = None):
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
    def update_gensim_model(self, texts: list = []):
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
        ngram_phraser = Phraser(ngram)
        ngrammed = ngram_phraser[text_list]
        return list(ngrammed), ngram

    @timeit
    def get_stats(self):
        """
        Generate stats: for each text find the dominant topic.
        Also for each topic find number of documents where it is dominant
        :return:
        """

        df_topic_sents_keywords = tm_functions.format_topics_sentences(ldamodel=self.model,
                                                                         corpus=self.doc_term_matrix,
                                                                         texts=self.data['cleaned_text'].values)

        df_dominant_topic = df_topic_sents_keywords.reset_index()
        df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

        top_indices = df_topic_sents_keywords.groupby('Dominant_Topic')['Perc_Contribution'].nlargest(1).reset_index()[
            'level_1']
        topic_counts = df_topic_sents_keywords['Dominant_Topic'].value_counts()

        # Percentage of Documents for Each Topic
        topic_contribution = round(topic_counts / topic_counts.sum(), 4)

        # Topic Number and Keywords
        condition = df_topic_sents_keywords.index.isin(top_indices)
        topic_num_keywords = df_topic_sents_keywords[condition][['Dominant_Topic', 'Topic_Keywords']].reset_index(
            drop=True)

        # Concatenate Column wise
        df_dominant_topics = pd.concat([topic_num_keywords, topic_counts, topic_contribution], axis=1)

        # Change Column names
        df_dominant_topics.columns = ['Dominant_Topic', 'Topic_Keywords', 'Num_Documents', 'Perc_Documents']

        self.df_dominant_topic = df_dominant_topic

    def plot_time_simple(self):
        """
        Prepare data for plotting and plot topic distribution over time
        :return:
        """

        self.data['date'] = self.data['url'].apply(lambda x: pd.to_datetime('-'.join(x.split('/')[4:7])))
        self.data['year_month'] = self.data['date'].values.astype('datetime64[M]')

        self.data['topics'] = [self.model.get_document_topics(i) for i in self.doc_term_matrix]
        self.data['topics_dict'] = self.data['topics'].apply(lambda x: {i[0]: i[1] for i in x})

        for i in range(self.model.num_topics):
            self.data['topic_' + str(i)] = self.data['topics_dict'].apply(lambda x: x[i] if i in x.keys() else 0)

        self.data = self.data.sort_values('year_month')

        self.data.loc[self.data['year_month'] == '1914-09-01 00:00:00', 'year_month'] = pd.Timestamp(year=2014, month=9,
                                                                                                 day=1, hour=0)
        topic_cols = [col for col in self.data.columns if 'topic_' in col]
        a = self.data.groupby(['year_month'])[topic_cols].mean()
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.stackplot(a.index, a.T.values, labels=list(a.columns))
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        plt.show()
