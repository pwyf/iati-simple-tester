#!/usr/bin/env python
from foxpath import test
import unicodecsv
import os
import config
import optparse
import sys

TESTS = config.TESTS
CURRENT_TEST = config.CURRENT_TEST
DIR_FOR_TESTING = config.DIR_FOR_TESTING
PACKAGEGROUP_NAME = config.PACKAGEGROUP_NAME

headers = [
           'result', 
           'iati-identifier', 
           'test-name', 
           'package-name',
           'current-result',
            ]

def get_xml_in_dir(start_string, relative_dir):
    filenames = []

    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    thedir = os.path.join(current_script_dir, os.path.abspath(relative_dir))

    for file in os.listdir(thedir):
        if (file.startswith(start_string) and file.endswith(".xml")):
            abs_filename = os.path.join(thedir, file)
            filenames.append({'absolute_filename': abs_filename,
                              'filename': file,
                              'name': os.path.splitext(file)[0]})
    return filenames

def run_tests(packages, csvfile, tests):

    def write_row(a, package, t_name):
        a['test-name'] = t_name
        a['package-name'] = package['name']
        writer.writerow(a)

    def write_package(package):
        print "Testing and writing for package", package['name']
        for atest in tests:
            for a in test.test_doc_json_out(package['absolute_filename'],
                atest['expression'], CURRENT_TEST)['activities']:

                write_row(a, package, atest['name'])
    
    print "Opening new CSV file, beginning testing"
    
    writer = unicodecsv.DictWriter(csvfile, headers)
    hdict = dict([(h,h) for h in headers])
    writer.writerow(hdict)

    for package in packages:
        write_package(package)

    print "Complete"

def get_tests_from_file(filename):
    reader = unicodecsv.DictReader(file(filename))
    for t in reader:
        yield { "expression": t["test_name"],
                "name": t["test_description"] }

def run_packagegroup_tests(options):
    if options.packagegroup:
        package_group_name = options.packagegroup
    else:
        package_group_name = config.PACKAGEGROUP_NAME

    packages = get_xml_in_dir(package_group_name, DIR_FOR_TESTING)

    def wrapped_run_tests(output_stream):
        if options.tests_file:
            tests = [ t for t in get_tests_from_file(options.tests_file) ]
        else:
            tests = TESTS

        return run_tests(packages, output_stream, tests)

    wrapped_run_tests(sys.stdout)

def get_options():
    parser = optparse.OptionParser()
    parser.add_option("--package-group", dest="packagegroup",
                      action="store")
    parser.add_option("--tests-file", dest="tests_file", action="store")
    options, rest = parser.parse_args()
    return options
 
if __name__ == "__main__":
    options = get_options()
    run_packagegroup_tests(options)
