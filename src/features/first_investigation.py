import os
import sqlite3
import pandas as pd
import scipy.stats as scs


def get_data_file():
    """Verify that the input data file exits."""
    if os.path.isfile(processed_filepath):
        return processed_filepath
    else:
        print('Error: no scrubbable data file exists.')
        quit()


class Database(object):

    def __init__(self, path):
        """Initialize a Database object."""
        self.__conn = sqlite3.connect(path)
        self.__cursor = self.__conn.cursor()

    def close(self):
        """Terminate the connection to the database."""
        self.__conn.close()

    def commit(self):
        """Commit changes to the database."""
        self.__conn.commit()

    def select(self, table, fields, qualifications=''):
        """Return the data for the provided criteria."""
        query = 'SELECT %s FROM %s %s;' %(fields, table, qualifications)
        df = pd.read_sql_query(query, self.__conn)
        return df


class Manager(object):

    def __init__(self, path):
        """Initialize a Manager object."""
        self.__db = Database(processed_filepath)
        self.__path = path

    def __del__(self):
        """Destructor for the Manager object."""
        self.__db.close()

    def first_investigation(self):
        """Perform first investigation analysis."""
        ## Get relevant data.
        table = 'dogs'
        # q04_1 = thunderstorm phobia
        # q04_2 = noise phobia
        # q04_9 = separation anxiety
        fields = 'q04_1, q04_2, q04_9'
        df = self.__db.select(table, fields)
        df.columns = ['thunder', 'noise', 'anxiety']
        df['thunder'] = pd.to_numeric(df['thunder'])
        df['noise'] = pd.to_numeric(df['noise'])
        df['anxiety'] = pd.to_numeric(df['anxiety'])
        ## Determine relationships.
        print('\nFirst Investigation:')
        print('The Relationship Between Noise and Anxiety')
        print('\nSums:')
        for index, row in df.sum().iteritems():
            print('%s = %d' %(index,row))
        print('\nModes:')
        for index, row in df.mode().iteritems():
            print('%s = %d' %(index,row))
        pairs = [
            ['thunder', 'noise'],
            ['thunder', 'anxiety'],
            ['noise', 'anxiety']
            ]
        for pair in pairs:
            print('\nContingency Table: (%s|%s)' %(pair[0], pair[1]))
            contingency = pd.crosstab(df[pair[0]], df[pair[1]])
            print(contingency)
            print('\nProbabilities: (%s|%s)' %(pair[0], pair[1]))
            for index, row in contingency.iterrows():
                for index2, row2 in row.iteritems():
                    prob = row2/5017
                    print('%s: %d, %s: %d, P = %.3f'
                          %(contingency.axes[0].name, index, row.axes[0].name,
                            index2, prob))
            print('\nChi-squared Test of Independence: (%s|%s)'
                  %(pair[0], pair[1]))
            c, p, dof, expected = scs.chi2_contingency(contingency,
                                                       correction=False)
            print('chi2 = %f, p = %.2E, dof = %d' %(c, p, dof))
        print('\nContingency Table: (anxiety|noise+thunder)')
        contingency = pd.crosstab(df['anxiety'], [df['noise'], df['thunder']])
        print(contingency)
        print('\nProbabilities: (anxiety|noise+thunder)')
        for index, row in contingency.iterrows():
            for index2, row2 in row.iteritems():
                prob = row2/5017
                print('%s: %d, %s: %d, %s: %d, P = %.3f'
                      %(contingency.axes[0].name, index, row.axes[0].names[0],
                        index2[0], row.axes[0].names[1], index2[1], prob))
        print('\nChi-squared Test of Independence: (anxiety|noise+thunder)')
        c, p, dof, expected = scs.chi2_contingency(contingency,
                                                   correction=False)
        print('chi2 = %f, p = %.2E, dof = %d' %(c, p, dof))
        print('')


def main():
    """
    Runs feature processing scripts to analuze the cleaned data from
    (../processed).
    """
    manager = Manager(get_data_file())
    manager.first_investigation()


if __name__ == '__main__':
    # store necessary paths
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    data_dir = os.path.join(project_dir, 'data')
    processed_filepath = os.path.join(data_dir, 'processed', 'processed.db')

    main()
