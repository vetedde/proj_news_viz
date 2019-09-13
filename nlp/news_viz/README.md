[news_viz] or src
--------

source code for use in this project

```
├── autoTagging                <- Source code for use in this project.
│   ├── __init__.py            <- Makes src a Python module
│   │
│   ├── ner                    <- Scripts to NER
│   │   └── cleanedNames.py 
│   │
│   ├── data_processing        <- Scripts to process data
│   │   └── preprocessing_tools.py
│   │
│   ├── 
```


__________________
how add PATH to jupyter:

        import os
        import sys
        
        
        home_path = os.getenv('HOME') # create home directory
        dir_project = 'proj_news_viz/nlp/structure' # write your main proj directory 

        PATH = os.path.join(home_path, dir_project)
        sys.path.append(PATH)

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
