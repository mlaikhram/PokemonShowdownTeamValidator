import sys
import re
import os
from zipfile import ZipFile


def writeToEmail(line):
    pass

def create_color_map():
    color_map = {}
    color_dir = os.fsencode('colors')
    for file in os.listdir(color_dir):
        filename = os.fsdecode(file)
        color = filename.replace('.txt', '')
        with open('colors/{}'.format(filename), 'r') as color_file:
            line = color_file.readline()
            while line:
                color_map[line.strip()] = color
                line = color_file.readline()
    return color_map


def get_species_from_text(txt, species_list):
    species = []
    isPokemonName = True
    for line in txt.splitlines():
        if isPokemonName:
            possible_species = re.findall('\(([^)]+)', str(line))
            check_state = 'gender'
            group_check = len(possible_species) - 1
            while group_check >= 0:
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
                    writeToEmail('{} is not a Pokemon'.format(species_name))

            isPokemonName = False
        elif line == b'':
            isPokemonName = True
    return species


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: python Validate.py <Zip File> <Color Limit>')
        sys.exit()

    print("Validating teams in {} with a color limit of {}".format(sys.argv[1], sys.argv[2]))
    color_map = create_color_map()
    with ZipFile(sys.argv[1], 'r') as zip:
        print("{} teams found!".format(len(zip.namelist())))
        for filename in zip.namelist():
            print("Validating {}...".format(filename))
            team = zip.read(filename)
            species = get_species_from_text(team, color_map.keys())
            color_groups = {}
            for pokemon in species:
                print("{}\t\t{}".format(pokemon, color_map[pokemon]))
                if color_map[pokemon] not in color_groups:
                    color_groups[pokemon] = []
                color_groups[pokemon].append(pokemon)
            if len(color_groups) > int(sys.argv[2]):
                print("This team has exceeded the color limit\n")
            else:
                print("This team has been successfully validated against the color limit!\n")