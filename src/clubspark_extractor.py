"""
Script to extract different types of membership lists from ClubSpark and if necessary perform
formatting on them before uploading to cloud file storage.
"""

import argparse
from helper import quit_with_error, get_bordered_string, setup_driver, get_divided_string, \
    extract_list_from_clubspark


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Membership List Extractor',
                                     description='Extracts membership list from ClubSpark, performs'
                                                 ' necessary formatting, then uploads file to cloud'
                                                 ' file storage.')
    parser.add_argument('-l', '--list-type', required=True, default='all members',
                        help='The type of list to be extracted from ClubSpark. '
                             'Accepted list types: \'All members\',\'Unpaid members\'')
    parser.add_argument('-f', '--file-type', required=True, default='csv',
                        help='The file type of the list to be extracted from ClubSpark. '
                             'Accepted file types: \'CSV\', \'PDF\'')
    parser.add_argument('-d', '--delete-columns', default=None,
                        help='Comma separated list of column names in extracted CSV list to be '
                             'deleted.')
    parser.add_argument('-u', '--upload-location', required=True, default='box',
                        help='The location of where the extracted list will be uploaded to. '
                        'Accepted upload locations: \'Box\', \'Google Drive\'')
    args = parser.parse_args()

    list_type_arg = args.list_type.lower()
    file_type_arg = args.file_type.lower()
    upload_location_arg = args.upload_location.lower()

    if list_type_arg != 'all members' and list_type_arg != 'unpaid members':
        quit_with_error('Please specify a valid list type. '
                        'Accepted list types: \'All members\', \'Unpaid members\'')

    if file_type_arg != 'csv' and file_type_arg != 'pdf':
        quit_with_error('Please specify a valid file type. Accepted file types: \'CSV\', \'PDF\'')

    if upload_location_arg != 'box' and upload_location_arg != 'google drive':
        quit_with_error('Please specify a valid upload location. '
                        'Accepted upload locations: \'Box\', \'Google Drive\'')

    print(get_bordered_string('CLUBSPARK EXTRACTOR'))
    driver = setup_driver()

    if args.file_type.lower() == 'csv':
        print(get_divided_string('Extract Settings'))
        print(f'List type: {list_type_arg}')
        print(f'File type: {file_type_arg}')
        if args.delete_columns is not None:
            columns_to_delete = args.delete_columns.split(',')
            print(f'Columns to delete: {columns_to_delete}')
            print(f'Upload location: {upload_location_arg}')
            try:
                extract_list_from_clubspark(driver, list_type_arg, file_type_arg,
                                            upload_location_arg, columns_to_delete)
            except Exception as e:
                quit_with_error(f'ClubSpark Extractor failed to execute.\n{e}')
        else:
            print(f'Upload location: {upload_location_arg}')
            try:
                extract_list_from_clubspark(driver, list_type_arg, file_type_arg,
                                            upload_location_arg)
            except Exception as e:
                quit_with_error(f'ClubSpark Extractor failed to execute.\n{e}')
    else:
        print(get_divided_string('Extract Settings'))
        print(f'List type: {list_type_arg}')
        print(f'File type: {file_type_arg}')
        print(f'Upload location: {upload_location_arg}')
        try:
            extract_list_from_clubspark(driver, list_type_arg, file_type_arg, upload_location_arg)
        except Exception as e:
            quit_with_error(f'ClubSpark Extractor failed to execute.\n{e}')
