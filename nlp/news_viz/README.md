[news_viz] or src
--------

source code for use in this project

```
├── news_viz                        <- source code for use in this project
│   ├── __init__.py                 <- makes src a Python module
│   │
│   ├── data_processing             <- scripts to process data
│   │   └── preprocessing_tools.py
│   │
│   ├── models                      <- scripts to our models
│   │   └── preprocessing_tools.py
│   │
│   ├── ner                         <- scripts to NER
│   │   └── cleanedNames.py 
│   │
│   ├── evaluation                  <- scripts to any evaluation (custom metrics, visualization & etc.)
│   │   └── visualization.py
│   │
│   ├── 
```

__________________
examples structure:
```
├── autoTagging              <- Source code for use in this project.
│   ├── __init__.py          <- Makes src a Python module
│   │
│   ├── data                 <- Scripts to download or generate data
│   │   └── make_dataset.py 
│   │
│   ├── features             <- Scripts to turn raw data into features for modeling
│   │   └── build_features.py
│   │
│   ├── models               <- Scripts to train models and then use trained models to make
│   │   │                       predictions
│   │   ├── predict_model.py
│   │   └── train_model.py
│   │
│   ├── visualization        <- Scripts to create exploratory and results oriented visualizations
│   │    └── visualize.py
```
