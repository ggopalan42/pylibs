''' Provides file utilities relevant to Machine Learning tasks. These include:
    - dir2filelist:   Traverse a dir and return a list of file paths
    - dir2train_val:  getting a lit of files from a dir and splitting
                      them into train and val sets
'''

import os


def dir2filelist(dirpath):
    ''' Recursively traverse a dirrectory and return all (absolute) file names

    Args:
        dirpath: Path to the dir that is to be traversed
    Returns:
        List of filenames (absolute filepaths)
    '''
    flist = []
    for dirpath, dirnames, filenames in os.walk(dirpath):
        apath = os.path.abspath(dirpath)
        for filename in filenames:
            flist.append(os.path.join(apath, filename))
    return flist

if __name__ == '__main__':
    # This is purely for testing purposes. Not unit testing, mind you
    dim = dir2filelist('.')
    for f in dim:
        print(f)
