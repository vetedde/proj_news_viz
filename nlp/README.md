news_viz
--------

```
├── config                          <- config files
│       └── ...
│
├── data
│   ├── external                    <- Data from third party sources.
│   ├── interim                     <- Intermediate data that has been transformed.
│   ├── processed                   <- The final, canonical data sets for modeling.
│   └── raw                         <- The original, immutable data dump.
│
├── experiments                     <- Some experiments
│   ├── analtsis_sources
│   │   └── ...
│   │── topic_models
│   │   ├── gensim
│   |   ├── bigartm
│   |   ├── cor_ex
│   |   ├── guided_lda
│   |   ├── sklearn
│   |   └── topsbm        
│
├── models                          <- Trained and serialized models, model predictions, or model summaries
│
├── news_viz                        <- Source code for use in this project         
│   ├── __init__.py                 <- makes src a Python module
│   ├── data_processing             <- scripts to process data
│   │   └── preprocessing_tools.py
│   ├── models                      <- scripts to our models
│   │   └── preprocessing_tools.py
│   ├── ner                         <- scripts to NER
│   │   └── cleanedNames.py 
│   ├── evaluation                  <- scripts to any evaluation (custom metrics, visualization & etc.)
│   │   └── visualization.py
│   └── ...
│
├── notebooks                       <- Jupyter notebooks
│
├── references                      <- Data dictionaries, manuals, and all other explanatory materials.
│
├── requirements.txt                <- The requirements file for reproducing the analysis environment, e.g.
│                                       generated with `pip freeze > requirements.txt`
```
