#!/usr/bin/env python3
# Copyright (C) 2025 Dr. Matthias Kesenheimer - All Rights Reserved.
# You may use, distribute and modify this code under the terms of the GPL3 license.
#
# You should have received a copy of the GPL3 license with this file.
# If not, please write to: info@faultyhardware.de.

# SQL Queries:
# Show only successes and flash-resets:
# color = 'R' or response LIKE '_Warning.flash_reset'

import argparse
import sys
import os.path

# import custom libraries
from findus import Database


class DBTool:
    def __init__(self, args):
        self.args = args

    def run(self):
        if self.args.dbname is not None and self.args.cleanup is not None:
            if not os.path.isfile(self.args.dbname):
                print(f"[-] Database {self.args.dbname} does not exist.")
                sys.exit(1)
            database = Database(sys.argv, dbname=self.args.dbname, dirname=None, resume=True)
            database.cleanup(self.args.cleanup)

        if self.args.dbname is not None and self.args.remove is not None:
            if not os.path.isfile(self.args.dbname):
                print(f"[-] Database {self.args.dbname} does not exist.")
                sys.exit(1)
            database = Database(sys.argv, dbname=self.args.dbname, dirname=None, resume=True)
            database.remove_conditional(self.args.remove)

        if self.args.merge is not None:
            database1 = Database(sys.argv, dbname=self.args.merge[0], dirname=None, resume=True)
            database2 = Database(sys.argv, dbname=self.args.merge[1], dirname=None, resume=True)
            if os.path.isfile(self.args.merge[2]):
                print(f"[-] Database {self.args.merge[2]} already exists. Choose another name.")
                sys.exit(1)
            column_names1 = database1.get_column_names()
            column_names2 = database2.get_column_names()
            if column_names1 != column_names2:
                print("[-] Column names of databases not compatible.")
                sys.exit(1)
            out = Database(sys.argv, dbname=self.args.merge[2], dirname=None, column_names=column_names1)
            toteid = 0
            for eid in range(0, database1.get_base_experiments_count()):
                parameters = database1.get_parameters_of_experiment(eid)
                if parameters != [None]:
                    parameters = (toteid, ) + parameters[1:]
                    print(parameters)
                    out.insert(*parameters)
                    toteid += 1
            for eid in range(0, database2.get_base_experiments_count()):
                parameters = database2.get_parameters_of_experiment(eid)
                if parameters != [None]:
                    parameters = (toteid, ) + parameters[1:]
                    print(parameters)
                    out.insert(*parameters)
                    toteid += 1

        if self.args.dbname is not None and self.args.export is not None:
            if not os.path.isfile(self.args.dbname):
                print(f"[-] Database {self.args.dbname} does not exist.")
                sys.exit(1)
            database = Database(sys.argv, dbname=self.args.dbname, dirname=None, resume=True)

            # Write column names as header if file is new
            if not os.path.exists(self.args.export):
                if self.args.columns:
                    header = ','.join(self.args.columns) + '\n'
                else:
                    header = ','.join(database.get_column_names()) + '\n'
                with open(self.args.export, 'w') as export_file:
                    export_file.write(header)
            
            # Open or create the export file
            with open(self.args.export, 'a' if os.path.exists(self.args.export) else 'w') as export_file:
                for eid in range(0, database.get_base_experiments_count()):
                    parameters = database.get_parameters_of_experiment(eid, column_names=self.args.columns)
                    # Write parameters to file
                    if parameters != [None]:
                        export_file.write(','.join(str(p) for p in parameters) + '\n')
                    print(parameters)

        if self.args.dbname is not None and self.args.show_columns:
            if not os.path.isfile(self.args.dbname):
                print(f"[-] Database {self.args.dbname} does not exist.")
                sys.exit(1)
            database = Database(sys.argv, dbname=self.args.dbname, dirname=None, resume=True)
            print(database.get_column_names())


def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--dbname", required=False, default=None, help="Name of the database")
    parser.add_argument("--cleanup", metavar="COLOR", required=False, default=None, help="Remove experiments with a certain color from the database.")
    parser.add_argument("--remove", required=False, default=None, help="Remove experiments by a certain condition. For example, `id = 1000`, `id > 1000`, `color = \"C\"` or `delay < 6000`.")
    parser.add_argument("--merge", metavar=("DATABASE1", "DATABASE2", "OUTPUT"), required=False, default=None, nargs=3, help="Merge two databases.")
    parser.add_argument("--export", metavar="CSV-FILENAME", required=False, default=None, help="Export the database given by dbname to a csv file.")
    parser.add_argument("--columns", metavar="NAME", required=False, default=None, help="Column names to export, for example 'delay length response'", nargs='+', type=str)
    parser.add_argument("--show-columns", required=False, action='store_true', help="Show the column names of the given database")

    args = parser.parse_args()

    dbtool = DBTool(args)

    try:
        dbtool.run()
    except KeyboardInterrupt:
        print("\nExitting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
