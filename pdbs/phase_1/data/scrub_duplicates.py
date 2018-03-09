"""Scrubs duplicates from raw data."""

import os
import shutil
import csv


# Verify the file to be scrubbed.
print(os.listdir(os.getcwd()))
filename = str(input('Enter file to be scrubbed of duplicates: '))
if not os.path.isfile(filename):
    print('Error: entered filename does not exist')
    quit()

# Create a backup of the original file if does not exist.
backup = filename + '.bak'
if not os.path.isfile(backup):
    print('Creating a backup of the the original file ...')
    shutil.copy(filename, backup)

# Parse the raw data with relevant filters.
dupe_cnt = 0
status_dict = {}
data_dict = {}
dog_dict = {}
with open(backup, 'r') as fin:
    with open(filename, 'w') as fout:
        writer = csv.writer(fout, delimiter=',', lineterminator='\n')
        first_row = True
        for row in csv.reader(fin, delimiter=','):
            write_row = False
            if not first_row:
                user_hash = row[8]
                status = [int(row[10]), int(row[145]), int(row[280]),
                          int(row[415]), int(row[550]), int(row[688])
                ]
                dogs = [row[11], row[146], row[281], row[416], row[551]]
                dogs = [x for x in dogs if x != '']
                if user_hash in status_dict:
                    dupe_cnt += 1
                    if status[5] == 0:
                        # Skip incomplete duplicate.
                        continue
                    if status_dict[user_hash][5] == 0:
                        # Replace incomplete entries with complete entries.
                        write_row = True
                        continue
                    old_dogs = set(dog_dict[user_hash])
                    new_dogs = set(dogs)
                    if not bool(old_dogs.symmetric_difference(new_dogs)):
                        # For matching dog entries, assume the user wanted to
                        # change their existing response.
                        write_row = True
                        continue
                    else:
                        # For mismatched dog entries, see if there are similarities.
                        print('Error: multiple entries for %s' %user_hash)
                        print(dog_dict[user_hash], end=' - ')
                        print(status_dict[user_hash])
                        print(dogs, end=' - ')
                        print(status)
                    #print(bool(set(dogs).symmetric_difference(dog_dict[user_hash])))
                    #if dog_dict[user_hash] == dogs and status_dict[user_hash] == status:
                        #print('MATCH %s %s' %(data_dict[user_hash][0], row[0]))
                        #print(set(data_dict[user_hash][1:]).symmetric_difference(row[1:]))

                else:
                    write_row = True
            else:
                first_row = False
            if write_row:
                data_dict[user_hash] = row
                status_dict[user_hash] = status
                dog_dict[user_hash] = dogs
                #writer.writerow(row)

# Let the user know the script has finished.
print('Dupes: %d' %dupe_cnt)
print('Scrubbing of %s is complete.' %filename)
