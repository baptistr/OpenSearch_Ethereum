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