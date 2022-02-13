# Ethereum et ses données

**Pour reproduire le contenu du rendu, il vous faut obligatoirement [Opensearch](https://opensearch.org/ "Opensearch") d'installé.**

## Introduction

J'ai utilisé ce [CSV](https://www.kaggle.com/deepshah16/meme-cryptocurrency-historical-data?select=Ethereum.csv "CSV") contenant donc des données numériques sur la cryptomonnaie Ethereum.
Nous y trouvons :
- (Open) Le prix d'ouverture de l'Ethereum le jour indiqué
- (High) Le prix le plus élevé de l'Ethereum le jour indiqué
- (Low) Le prix le plus bas de l'Ethereum le jour indiqué
- (Close) Le prix de fermeture de l'Ethereum le jour indiqué
- (Volume) Le volume de transactions en dollar en Ethereum le jour indiqué
- (Market Cap) La capitalisation en dollar de l'Ethereum le jour indiqué

Les informations que nous avons commencent le 7 Aout 2015, proche de la date de création d'Ethereum (30 Juillet 2015) et se terminent le 27 Juin 2021.
Comme un document correspond à un jour et que nous avons 2152 valeurs, nous avons donc 2152 jours de données.


## Intégration du dataset

Pour pouvoir intégrer le dataset il a fallu convertir et modifier son contenu permettant d'obtenir la syntaxe recherchée par Opensearch.
Pour cela j'ai trouvé et adapté un script Python à mon dataset qui va me générer un nouveau fichier json:
```python
import json
import pandas

#le fichier que je veux modifier
in_file = "/home/tpuser/Documents/OpenSarchEthereumData/Ethereum.csv"

#le fichier généré avec les modifications
out_file = "/home/tpuser/Documents/OpenSarchEthereumData/dataEthereum.json"

cols = ['Date','Open', 'High', 'Low', 'Close','Volume','Market Cap']

input = pandas.read_csv(in_file)

#convertion des données en format numeric
input.Open = pandas.to_numeric(input['Open'])
input.High = pandas.to_numeric(input['High'])
input.Low = pandas.to_numeric(input['Low'])
input.Close = pandas.to_numeric(input['Close'])
input.Volume = pandas.to_numeric(input['Volume'])
input.Market_cap = pandas.to_numeric(input['Market Cap'])

i = 1

#permet d'écrire et de remplacer le contenu
with open(out_file, 'w+') as outfile:
    for row in input.to_dict('records'):

        #modification du format date EU en EN
        split = row['Date'].split("-")
        print(row['Date'] + " --- "+split[2]+'-'+split[1]+'-'+split[0])
        row['Date'] = split[2]+'-'+split[1]+'-'+split[0]

        #adaptation de la syntaxe
        index_line = '{"index": {"_index": "eth", "_id": %s }}\n' %(i)
        i += 1
        data = json.dumps(dict(list(zip(cols,
        row.values())))) + '\n'
        outfile.write(index_line+data)
```

## Index et import du dataset

Pour importer le dataset, il faut au préalable créer un index

`
curl -u admin:admin --insecure -XPUT "https://localhost:9200/<nom_de_votre_index>?pretty"
`  

Dans un second temps il faut mapper les données pour vérifier la compatibilité des données

*contenu du fichier de mapping (mapping_refactored.json) :*
```
{
  "properties": {
    "Date": {
      "type": "date"
    },"Open": {
      "type": "float"
    },"High": {
      "type": "float"
    },"Low": {
      "type": "float"
    },"Close": {
      "type": "float"
    },"Volume": {
      "type": "float"
    },"Market Cap": {
      "type": "float"
    }
  }
}
```  
`
curl -u admin:admin --insecure -XPUT "https://localhost:9200/<nom_de_votre_index>/_mapping?pretty" -H 'Content-Type: application/json' -d @<nom_de_votre_fichier_de_mapping>.json
`

Nous allons donc maintenant pouvoir indexer nos données dans Opensearch grâce à la méthode bulk :  

`
curl -u admin:admin --insecure -XPUT https://localhost:9200/_bulk -H "Content-Type: application/json" --data-binary @<nom_de_votre_fichier_contenant_les_donnees>.json
`

## Requêtes et Aggrégations

*Je précise que me sers du logiciel Insomnia pour utiliser mes queries*  

Pour introduire le dataset, nous allons commencer par récupérer les données du jour du listing d'Ethereum sur le marché financier de la cryptomonnaie, c'est à dire la date la plus vieille.

**INPUT**
```JSON
{
  "query": {
    "match": {
      "Date": "2015-08-07"
    }
  }
}
```
**OUTPUT**
```JSON
{
	"_index": "eth",
	"_type": "_doc",
	"_id": "2152",
	"_score": 1.0,
	"_source": {
		"Date": "2015-08-07",
		"Open": 2.83161997795105,
		"High": 3.5366098880767822,
		"Low": 2.521120071411133,
		"Close": 2.7721199989318848,
		"Volume": 164329.0,
		"Market Cap": 1.66610555018E8
	}
}
```
Et la plus récente du dataset :

**INPUT**
```JSON
{
  "query": {
    "match": {
      "Date": "2021-06-27"
    }
  }
}
```
**OUTPUT**
```JSON
{
	"_index": "eth",
	"_type": "_doc",
	"_id": "1",
	"_score": 1.0,
	"_source": {
		"Date": "2021-06-27",
		"Open": 1830.99691808,
		"High": 1979.95812503,
		"Low": 1811.24586446,
		"Close": 1978.89466209,
		"Volume": 1.988547474215E10,
		"Market Cap": 2.3047355611835E11
	}
}
```
Une manière plus rapide d'obtenir ces informations :

**INPUT**
```JSON
{
  "query": {
    "terms": {
      "Date": [
        "2015-08-07",
        "2021-06-27"
      ]
    }
  }
}
```

Nous pouvons donc apercevoir une grande différence entre les grandeurs des données des deux dates.
Pour essayer d'y voir un peu plus clair, nous allons voir à quel point les nombres sont plus grands.

...

Connaître la moyenne de prix sur une période donnée permet premièrement de voir à un instant t si la valeur évolue mais permet surtout de savoir où sont placés les supports et résistances dans les marchés financiers.

Pour la moyenne depuis 2015 :  
**INPUT**
```JSON
{
   "aggs":{
      "calcul":{
         "avg":{
	    "field":"Close"
	 }
      }
   }
}
```
**OUTPUT**
```JSON
{
    "aggregations": {
       "calcul": {
          "value": 376.1153092069974
	}
    }
}
```
Pour la moyenne entre les 20 jours précédent une date comprise :

**INPUT**
```JSON
{
    "size": 0,
    "query": {
        "range": {
          "Date": {
            "gte": "2021-06-27||-20d"
          }
        }
    },
    "aggs":{
        "moyenne":{
	    "avg": {
                "field": "Close"
            }
	}
    }
}
```
**OUTPUT**
```JSON
{
    "aggregations": {
	"moyenne": {
	    "value": 2253.8173246837796
	}
    }
}
```

Il est aussi assez intéressant de voir que la valeur minimale par an de l'Ethereum augmente chaque année (à une exception) :

**INPUT**
```JSON
{
  "size": 0,
  "aggs": {
    "logs_per_month": {
      "date_histogram": {
        "field": "Date",
        "interval": "year"
      },
      "aggs":{
          "calcul":{
	      "min":{
	          "field":"Low"
	      }
	   }
       }
      }
   }
}
```
**OUTPUT**
```JSON
{
"aggregations": {
	"logs_per_month": {
		"buckets": [
			{
			    "key_as_string": "2015-01-01T00:00:00.000Z",
			    "key": 1420070400000,
			    "doc_count": 147,
			    "calcul": {
				"value": 0.4208970069885254
			    }
			},
			{
			    "key_as_string": "2016-01-01T00:00:00.000Z",
			    "key": 1451606400000,
			    "doc_count": 366,
			    "calcul": {
				"value": 0.9298350214958191
			    }
			},
			...
}
```
Le *doc_count* correspond au nombre de jours. Normalement la valeur doit se rapprocher du nombre de jours dans une année mais la première et dernière itération possède des nombres éloignés de ce qu'on voulait avoir car le dataset commence et se finit en milieu d'année.

*tous les résultats :*
| Année | Prix minimal |
|:-----:|--------------|
|  2015 |   **$0.42**  |
|  2016 |   **$0.92**  |
|  2017 |   **$7.98**  |
|  2018 |   **$82.82**  |
|  2019 |   **$102.93**  |
|  2020 |   **$95.18**  |
|  2021 |   **$718.10**  |

Même si l'Ethereum a prit énormément de valeurs durant ces dernières années, je me suis donc demandé combien de jour il a perdu ou gagné. Nous pouvons trouver cela en regardant si son prix est a été supérieur entre le début et fin de journée :

**INPUT**
```JSON
{
    "size" : 0,
    "query": {
        "bool": {
            "must": [{
                "script": {
                    "script": "doc['Close'].value > doc['Open'].value"
                }
            }]
        }
    }
}
```
**OUTPUT**
```JSON
"hits": {
   "total": {
      "value": 1079,
         "relation": "eq"
      }
```
Nous en avons 1079, ce qui veut dire qu'il y 50,14% (1079/2152\*100) de jours qui se terminent positifs et 49,86 qui se terminent négatifs.

En général une baisse du prix fait diminuer la capitalisation du marché, pour vérifier cela, je vais faire la moyenne du prix et la moyenne de la capitalisation du marché par mois pour minimiser le nombre d'exeptions.

**INPUT**
```JSON
{
  "size": 0,
  "aggs": {
    "logs_per_month": {
      "date_histogram": {
        "field": "Date",
        "interval": "month"
      },
      "aggs":{
          "prix_moyen":{
              "avg":{
	          "field":"Close"
	      }		
	  },
	  "capitalisation_moyenne":{
	      "avg":{
	          "field":"Market Cap"
	      }
	  }
      }
    }
  }
}
```
**OUTPUT**
```JSON
{
    "key_as_string": "2018-11-01T00:00:00.000Z",
    "key": 1541030400000,
    "doc_count": 30,
    "prix_moyen": {
        "value": 169.04776992797852
    },
    "capitalisation_moyenne": {
	"value": 1.7442884608E10
    }
},
    {
    "key_as_string": "2018-12-01T00:00:00.000Z",
    "key": 1543622400000,
    "doc_count": 31,
    "prix_moyen": {
        "value": 108.99809732744771
    },
    "capitalisation_moyenne": {
        "value": 1.1320000115612904E10
    }
}
...
```

Maintenant, pour touver le nombre d'Ethereum en circulation sur le marché par jour, il suffit de diviser la capitalisation du marché par son prix :

**INPUT**
```JSON
{
  "size": 0,
  "aggs": {
    "logs_per_day": {
      "date_histogram": {
        "field": "Date",
        "interval": "day"
      },
      "aggs":{
          "prix_moyen":{
              "avg":{
	          "field":"Close"
	      }		
	  },
	  "capitalisation_moyenne":{
	      "avg":{
	          "field":"Market Cap"
	      }
	  },
	  "nombre_ethereum":{
	      "bucket_script": {
	          "buckets_path": {
		      "my_var1": "prix_moyen",
		      "my_var2": "capitalisation_moyenne"
		  },
	          "script":"params.my_var2 / params.my_var1"
	      }
	  }
      }
    }
  }
}
```
**OUTPUT**
```JSON
{
    "key_as_string": "2018-04-02T00:00:00.000Z",
    "key": 1522627200000,
    "doc_count": 1,
    "prix_moyen": {
        "value": 386.42498779296875
    },
    "capitalisation_moyenne": {
	"value": 3.8093279232E10
    },
    "nombre_ethereum": {
	"value": 9.857871627185991E7
    }
},
...
```
