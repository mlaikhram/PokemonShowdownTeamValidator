import sys
import re
import os
from zipfile import ZipFile
import EmailService


def get_users_list():
    users = {}
    with open('users.txt', 'r') as user_file:
        line = user_file.readline()
        while line:
            user = line.strip().split(':')
            users[user[0]] = user[1]
            line = user_file.readline()
    return users


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


def get_species_from_text(txt, species_list, errors):
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
                    errors.append('{} is not a Pokemon'.format(species_name))

            isPokemonName = False
        elif line == b'':
            isPokemonName = True
    return species


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('usage: python Validate.py <Zip File> <Color Limit> <Team Limit>')
        sys.exit()

    print("Validating teams in {} with a color limit of {} and a team limit of {}".format(sys.argv[1], sys.argv[2], sys.argv[3]))
    errors = {'general': []}
    color_map = create_color_map()
    all_teams = {}
    with ZipFile(sys.argv[1], 'r') as zip:
        print("{} teams found!".format(len(zip.namelist())))
        if len(zip.namelist()) > int(sys.argv[3]):
            errors['general'].append('You have exceeded the max number of teams with {} teams total'.format(len(zip.namelist())))
        for filename in zip.namelist():
            print("Validating {}...".format(filename))
            errors[filename] = []
            team = zip.read(filename)
            species = get_species_from_text(team, color_map.keys(), errors[filename])
            color_groups = {}
            for pokemon in species:
                # print("{}\t\t{}".format(pokemon, color_map[pokemon]))
                if color_map[pokemon] not in color_groups:
                    color_groups[color_map[pokemon]] = []
                color_groups[color_map[pokemon]].append(pokemon)
            if len(color_groups) > int(sys.argv[2]):
                errors[filename].append("This team has exceeded the color limit with {} colors".format(len(color_groups)))

            all_teams[filename] = color_groups

        if len(errors[filename]) > 0:
            print("{} has failed validation\n".format(sys.argv[1]))
        else:
            print("{} has been successfully validated!\n".format(sys.argv[1]))

        username = sys.argv[1].split('/')[-1].replace('.zip', '')
        user_list = get_users_list()
        email = user_list[username]
        if email:
            email_body = "Hi {},\n\nHere is a basic color overview of your teams:\n".format(username)

            for team in all_teams:
                email_body += "\n{}\n".format(team)
                for color in all_teams[team]:
                    email_body += "\t{}\n".format(color)
                    for pokemon in all_teams[team][color]:
                        email_body += "\t\t{}\n".format(pokemon)

            print("Sending validation logs to {}".format(email))
            # print(errors)
            if not (error for error in errors.values() if error != []):
                email_body += "\nCongratulations! Your {} team{} passed validation!\n".format(len(zip.namelist()), ' has' if len(zip.namelist()) == 1 else 's have')

            else:
                email_body += "\nIt looks like your {} team{} failed validation :(.\nHere are the reasons your team failed:\n".format(len(zip.namelist()), ' has' if len(zip.namelist()) == 1 else 's have')

                for error_group in errors:
                    if len(errors[error_group]) > 0:
                        email_body += "\n{}:\n".format(error_group)
                        for error in errors[error_group]:
                            email_body += "\t{}\n".format(error)
                email_body += "\n Please adjust your teams to account for these errors and try submitting again.\n"

            email_body += "\nColor Cup 2020"

            service = EmailService.create_service()
            message = EmailService.create_message("Color Cup 2020 Validation Service",
                                                  email,
                                                  "Color Cup 2020 Teams Validation",
                                                  email_body
                                                  )
            EmailService.send_message(service, 'me', message)

        else:
            print("Username: {} has not been registered for the tournament".format(username))
