import sys
import re
from zipfile import ZipFile


def get_species_from_text(txt, species_list):
    species = []
    isPokemonName = True
    for line in txt.splitlines():
        if isPokemonName:
            print(line)
            possible_species = re.findall('\(([^)]+)', str(line))
            check_state = 'gender'
            group_check = len(possible_species) - 1
            while group_check >= 0:
                print('checking with {}'.format(check_state))
                if check_state == 'gender':
                    if possible_species[group_check] == 'M' or possible_species[group_check] == 'F':
                        group_check -= 1
                    check_state = 'species'

                elif check_state == 'species':
                    if possible_species[group_check] in species_list:
                        species.append(possible_species[group_check])
                        check_state = 'found'
                        break
                    else:
                        check_state = 'not found'
                        break

            if check_state != 'found':
                species_name = str(line).split('@')[0].split('(')[0].strip()
                if species_name in species_list:
                    species.append(species_name)
                else:
                    print('{} is not a Pokemon'.format(species_name))

            isPokemonName = False
        elif line == b'':
            isPokemonName = True
    return species


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('please provide a .zip file to validate')
        sys.exit()

    with ZipFile(sys.argv[1], 'r') as zip:
        print(zip.namelist())
        for filename in zip.namelist():
            print(filename)
            team = zip.read(filename)
            species = get_species_from_text(team, ['Rotom-Heat', 'Smeargle', 'Gengar', 'Excadrill', 'Azumarill', 'Conkeldurr', 'Beedrill', 'Excadrill', 'Rotom-Wash', 'Infernape', 'Porygon2'])
            print(species)