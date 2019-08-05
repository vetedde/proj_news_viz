import os
import sys
import re
import subprocess
import logging

import numpy as np
import pandas as pd
import artm

from datetime import timedelta

from luigi import LocalTarget, run, Task, Parameter, IntParameter, DateParameter
from py_scripts import convert_to_vw 

logger = logging.getLogger(__name__)


def check_or_create_local_data_dir_for_date(local_data_dir, date):
    local_dir = os.path.join(local_data_dir, date)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
class CountersToLocalFile(Task):
    """
    Loads preprocessed texts and converts them to a vw format
    """
    in_path = Parameter()
    local_data_dir = Parameter()
    date = Parameter()
    local_vw_file = Parameter()

    def output(self):
        return LocalTarget(os.path.join(self.local_data_dir, self.date, self.local_vw_file))

    def run(self):
        check_or_create_local_data_dir_for_date(self.local_data_dir, self.date)
        texts = pd.read_csv(self.in_path)
        texts['text'] = texts[['article_id', 'text']].apply(lambda x: convert_to_vw.print_line_out(x[0], x[1]), 1)
        out_f = os.path.join(self.local_data_dir, self.date, self.local_vw_file)
        with open(out_f, "w") as f:
            for article in texts['text'].values:
                f.write(article+"\n")

class VWToARTMBatches(Task):
    """
    Input: vw file (vw formatting)
    Output: artm batches dir (locally)
    """

    local_data_dir = Parameter()
    date = Parameter()
    local_vw_file = Parameter()

    def requires(self):
        return CountersToLocalFile(date=self.date)

    def output(self):
        return LocalTarget(os.path.join(self.local_data_dir, self.date, "batches"))

    def run(self):
        check_or_create_local_data_dir_for_date(self.local_data_dir, self.date)
        in_path = os.path.join(self.local_data_dir, self.date, self.local_vw_file)
        out_path = os.path.join(self.local_data_dir, self.date, "batches")

        batch_vectorizer_train = artm.BatchVectorizer(data_path=in_path,
                                                      collection_name='code',
                                                data_format='vowpal_wabbit',
                                                target_folder=out_path)
        dictionary = batch_vectorizer_train.dictionary
        dictionary.filter(min_df=1)
        dictionary.save_text(os.path.join(self.local_data_dir, self.date, "dictionary.txt"))
        #removing vw file (do not need it from now on)
        os.remove(in_path)
    
    
class TrainARTM(Task):
    """
    Trains and saves an ARTM model, score results and theta matrix in local dir
    Output: artm model, scores, theta
    """
    local_data_dir = Parameter()
    date = Parameter()
    n_topics = IntParameter()
    n_workers = IntParameter()

    def requires(self):
        return VWToARTMBatches(date=self.date)

    def output(self):
        return LocalTarget(os.path.join(self.local_data_dir, self.date, "artm.model"))

    def run(self):
        self.basedir = os.path.join(self.local_data_dir, self.date)
        in_dir_batches = os.path.join(self.local_data_dir, self.date, "batches")

        date_prev = None
        use_pretrained = False
        date_list = [date.strip() for date in os.listdir(self.local_data_dir)]
        print(date_list)
        if not date_list:
            raise IOError("Could not run a training. No batches found.")

        if len(date_list) == 1:
            date_prev = None
        else:
            try:
                date_prev = [date for date in date_list if date<self.date][-1]
            except IndexError as e:
                date_prev = date_list[-1]
            use_pretrained = True

        if date_prev:
            self.model_in_file = os.path.join(self.local_data_dir, date_prev, "artm.model")

        else:
            self.model_in_file = None

        self.model_out_file = os.path.join(self.basedir, "artm.model")

        dict_path = os.path.join(self.basedir, "dictionary.txt")
        dictionary = artm.Dictionary()
        dictionary.load_text(dict_path)

        self.batch_vectorizer = artm.BatchVectorizer(data_path=os.path.join(self.basedir, "batches"),
                                        data_format='batches')

        self._init_artm_model(dictionary)
        self._train(use_pretrained)
        self._save_results()
        
    def _init_artm_model(self, dictionary):
        """
        Init a new model, adding regularizers, scores
        """
        self.model = artm.ARTM(num_topics=self.n_topics,
                              cache_theta=True,
                              num_processors=self.n_workers,
                              show_progress_bars=True,
                              seed=12,
                              dictionary=dictionary)
        self._add_regularizers()
        self._add_scores()

    def _add_regularizers(self):
        """
        Add some regularizers to an ARTM model
        """
        self.model.regularizers.add(artm.SmoothSparseThetaRegularizer(name='sparse_theta_regularizer'))
        self.model.regularizers.add(artm.DecorrelatorPhiRegularizer(name='decorrelator_phi_regularizer'))

    def _add_scores(self):
        """
        Output: several png files with scores
        """
        self.model.scores.add(artm.PerplexityScore(name='my_fisrt_perplexity_score'))
        self.model.scores.add(artm.SparsityPhiScore(name='sparsity_phi_score'))
        self.model.scores.add(artm.SparsityThetaScore(name='sparsity_theta_score'))
        self.model.scores.add(artm.TopTokensScore(name='top_tokens'))
                                                  
    def _train(self, use_pretrained):
        """
        Trains an ARTM model
        """
        if use_pretrained:
            #load model
            artm_old = artm.ARTM(self.n_topics)
            artm_old.load(self.model_in_file)

            #getting phi
            phi_old = artm_old.phi_
            #phi to update
            phi_to_update = self.model.get_phi()
            phi_to_update['term'] = phi_to_update.index
            phi_old['term'] = phi_old.index

            #updating weights
            phi_to_update.update(phi_old.drop_duplicates(subset='term', keep='last'), join='left', overwrite=True)
            phi_to_update = phi_to_update.drop('term', 1)

            (_, phi_ref) = self.model.master.attach_model(model=self.model.model_pwt)
            np.copyto(phi_ref, phi_to_update.values)
            num_collection_passes = 10
        else:
            num_collection_passes = 70

        self.model.fit_offline(batch_vectorizer=self.batch_vectorizer,
                                   num_collection_passes=num_collection_passes)

    def _save_results(self):
        """
        Saves theta matrix (article_id -> topics) to a csv file.
        Then saves top_tokens for every class_id and finally dumps images of a perplexity score for every class.
        """
        self.model.theta_columns_naming='title'
        self.model.save(self.model_out_file)

        #theta = self.model.theta_
        theta = self.model.get_theta()
        theta = theta.T
        theta['article_id'] = theta.index
        theta = theta.drop_duplicates(subset='article_id')
        theta['dt'] = self.date
        topic_columns = ["topic_{}".format(col) for col in range(n_topics)]
        theta.to_csv(os.path.join(self.basedir, 'theta.csv'), index=None)
        top_tokens = self.model.score_tracker['top_tokens']
        top_tokens = pd.DataFrame(top_tokens.last_tokens)
        top_tokens.to_csv(os.path.join(self.basedir, "top_tokens.csv"),
                                   encoding='utf8')


if __name__ == '__main__':
    run()

