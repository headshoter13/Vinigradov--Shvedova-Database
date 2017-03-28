from elasticsearch import Elasticsearch
import os
import json
from flask import Flask, request, render_template

es = Elasticsearch()

# кладём данные в elasticsearch
def put_data(index):
    doc_types = []
    for a, b, c in os.walk('./mapping'):
        es.indices.create(index = index)
        for file in c:
            body = json.loads(open('./mapping/' + file, 'r', encoding='utf-8').read())
            print(body)
            doc_type = file[:-5]
            print(doc_type)
            # записываем тип документа - пригодится при загружении самих конструкций
            doc_types.append(doc_type)
            print(doc_types)
            # кладём мэппинг
            es.indices.put_mapping(index = index, doc_type = doc_type, body = body)
    # перебираем типы документов
    for doc_type in doc_types:
        print(doc_type)
        for a, b, c in os.walk('./sry'):
            # залезаем в папку, название который совпадает с типом документа, перебираем все файлы
            for i in c:
                print(i)
                body = json.loads(open('./sry/' + i, 'r', encoding='utf-8-sig').read())
                # каждый файл загружаем в es, id - название документа (без .json)
                es.index(index = index, doc_type = doc_type, body = body, id = int(i.strip('.json')))

es.indices.delete(index='constructions_type', ignore=[400, 404])
put_data('constructions_type')

def lists():
    documents = es.cat.count(index="constructions_type")
    n_docs = documents.split()[-1]
    print(n_docs)
    lists = json.loads(open('lists.json', 'r', encoding='utf-8-sig').read())
    if not os.path.exists('./lists'):
            os.makedirs('./lists')
    for list_parameters in lists:
        arr = []
        for parameter in list_parameters:
            print(parameter)
            res = es.search(index = "constructions_type", body = {"query": {"match_all": {} }, "size": n_docs})
            for i in res["hits"]["hits"]:
                if parameter in i["_source"]:
                    option = i["_source"][parameter]
                    if option != '-' and option != '':
                        if option not in arr:
                            arr.append(option)
        with open('./lists/' + list_parameters[0] + '.json', 'w', encoding='utf-8-sig') as outfile:
            json.dump(arr, outfile)
        print(arr)
            
lists()

app = Flask(__name__)
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
     # если окошечки заполнены
    if len(request.args) > 0:
        documents = es.cat.count(index="constructions_type")
        n_docs = documents.split()[-1]

        # сохраняем содержимое заполненных окошек
        year_first_1 = request.args["year_first_1"]
        year_first_2 = request.args["year_first_2"]
        year_last_1 = request.args["year_last_1"]
        year_last_2 = request.args["year_last_2"]
        dic = dict(request.args)
        for i in ["year_first_1", "year_first_2", "year_last_1", "year_last_2", "find"]:
            del dic[i]
        body = {"size" : n_docs, "query": {"bool": {"must": [] }}}
        if year_first_1 != '':
            body["query"]["bool"]["must"].append({"range": {"year_first_using": {"gte": int(year_first_1), "lte": int(year_first_2)}}})
        if year_last_1 != '':
            body["query"]["bool"]["must"].append({"range": {"year_last_using": {"gte": int(year_last_1), "lte": int(year_last_2)}}})
        # начинаем составлять запрос
        for i in dic:
            if dic[i][0] != '':
                body["query"]["bool"]["must"].append({"match_phrase": {i: dic[i][0]}})

        data = []

        # поиск по составленному запросу
        res = es.search(index = "constructions_type",
                            body = body)
        data += [i["_source"] for i in res["hits"]["hits"]]
        

        # если нашли - возращаем страничку с результатами поиска, не нашли - страничку, где написано, что ничего не найдено
        if data != []:
            return render_template('results.html', n_all=n_docs, n_results=len(data), data=sorted(data, key=lambda x: int(x["id_doc"])))
        else:
            return render_template('no_results.html')

    # если окошечки не заполнены, возвращаем страничку с окошечками
    else:
        lists = {}
        for a, b, c in os.walk('./lists'):
            for file in c:
                f = json.loads(open('./lists/' + file, 'r', encoding='utf-8-sig').read())
                lists[file.replace('.json', '')] = f
                print(lists)
        return render_template('search.html', lists=lists)
@app.route('/construction/<id_doc>')
def construction(id_doc):
    # извлекаем инфу о конструкции по её названию
    res = es.search(index = "constructions_type",
                    body = {"query": {"match_phrase": {"id_doc": "%s" % id_doc}}})
    data = res["hits"]["hits"][0]["_source"]

    # ставим в соответствие параметрам в базе параметры на кириллице
    data_new = {}
    parameters = json.loads(open('construction_type.json', 'r', encoding='utf-8-sig').read())
    for part in parameters:
        data_new[part] = []
        for parameter in parameters[part]:
            if data[parameter[0]] != '':
                 data_new[part].append([parameter[1], data[parameter[0]]])


    # возвращаем страничку с заполненными параметрами
    return render_template('construction.html', data=data_new)

# ресурсы, использованные при работе (тоже пока пусто)
@app.route('/resources')
def resources():
    return render_template('resources.html')

# помощь (и тут пусто)
@app.route('/help')
def help():
    return render_template('help.html')

#@app.route('/page/<page_pdf>')
#def help():
 #   res = es.search(index = "constructions_type",
  #                  body = {"query": {"match_phrase": {"page_pdf": "%s" % page_pdf}}})
   # data = res["hits"]["hits"][0]["_source"]

    #return render_template('page.html')

def help():
    return render_template('help.html')
app.run(host='0.0.0.0', port=5009, debug=True)
