src for ner
-------

* cleanedNames.py
  
        ```
        from news_viz.ner.cleanedNames import KeyProc
        
        cn = KeyProc(main_path=PATH) # add path to run full script from jupyter

        # for example
        text = '''когда дмитрий песков увидел владимира путина и авраама линкольна то подумал о иосифе сталине'''

        print(cn.extractKeywords(text))
        >> ['дмитрий_песков', 'владимир_путин', 'авраам_линкольн', 'иосиф_сталин']
        
        print(cn.replaceKeywords(text))
        >> когда дмитрий_песков увидел владимир_путин и авраам_линкольн то подумал о иосиф_сталин
        ```