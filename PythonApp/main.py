import json

import requests

import csv


class Permis:
    def __init__(self, id, nume, prenume, categorie, dataDeEmitere, dataDeExpirare, suspendat):
        self.id = id
        self.nume = nume
        self.prenume = prenume
        self.categorie = categorie
        self.dataDeEmitere = dataDeEmitere
        self.dataDeExpirare = dataDeExpirare
        self.suspendat = suspendat

    def __repr__(self):
        return "{0},{1},{2},{3},{4},{5},{6}".format(self.id, self.nume, self.prenume, self.categorie,
                                                    self.dataDeEmitere, self.dataDeExpirare, self.suspendat)

    def __iter__(self):
        return iter(
            [self.id, self.nume, self.prenume, self.categorie, self.dataDeEmitere, self.dataDeExpirare, self.suspendat])


def get_data(api_url, length):
    response = requests.get(f'http://{api_url}/drivers-licenses/list?length={str(length)}')

    if response.status_code != 200:
        print("Nu s-au putut prelua datele")
        exit(1)

    permise_json = json.loads(response.text)

    return [Permis(**permis) for permis in permise_json]


def filter_suspended(permise):
    return [permis for permis in permise if permis.suspendat]


def filter_valid(permise):
    from datetime import date

    valide = []

    azi = date.today()

    for permis in permise:
        zi, luna, an = [int(x) for x in permis.dataDeExpirare.split('/')]
        data_exp = date(an, luna, zi)

        zi, luna, an = [int(x) for x in permis.dataDeEmitere.split('/')]
        data_emitere = date(an, luna, zi)

        if azi < data_exp:
            if azi > data_emitere:
                valide.append(permis)

    return valide


def group_by_category(permise):
    categorie = input("Introdu categoria: ")

    lista = [permis for permis in permise if permis.categorie.lower() == categorie.lower()]

    return lista, categorie, lista.__len__()


def save_to_file(permise, filepath, categorie=None, numar=None):

    filename = filepath + (f'_{categorie}' if categorie else '') + '.csv'

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)

        header = ['Id', 'Nume', 'Prenume', 'Categorie', 'Data De Emitere', 'Data De Expirare', 'Suspendat']
        writer.writerow(header)

        for permis in permise:
            writer.writerow(permis.__iter__())

        if categorie is not None and numar is not None:
            writer.writerow([''])
            writer.writerow(['Total', numar])


if __name__ == '__main__':
    permise = get_data("localhost:30000", 150)

    # 1
    suspendate = filter_suspended(permise)
    save_to_file(suspendate, "csv/suspendate")

    print("Suspendate:")
    print(suspendate)
    print()

    # 2
    valide = filter_valid(permise)
    save_to_file(valide, "csv/valide")

    print("Valide:")
    print(valide)
    print()

    # 3
    permise_categorie, categorie, numar = group_by_category(permise)
    save_to_file(permise_categorie, "csv/categorie", categorie, numar)

    print(f'Categoria {categorie}:')
    print(permise_categorie)
    print()
