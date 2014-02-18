#!/usr/bin/env python

import os, re, subprocess, sys
import fnmatch
import argparse
import shutil

def fetch_files_recursive(directory, filename = None, extension = None):
    matches = []
    
    if isinstance(directory, list):
        directory = directory[0]

    if os.path.isdir(directory):
        for root, dirnames, filenames in os.walk(directory):
            for name in fnmatch.filter(filenames, '*' + extension):
                if (filename is None):
                    matches.append(os.path.join(root, name))
                elif (name == (filename + extension)):
                    matches.append(os.path.join(root, name))
    elif os.path.isfile(directory):
        matches.append(directory)

    return matches


def get_localize_strings_from_files(files):
    # prepare regexes
    localizedStringComment = re.compile('NSLocalizedString\(@"([^"]*)",\s*@"([^"]*)"\s*\)', re.DOTALL)
    localizedStringNil = re.compile('NSLocalizedString\(@"([^"]*)",\s*nil\s*\)', re.DOTALL)
    localized = re.compile('Localized\(@"([^"]*)"\)', re.DOTALL)
    
    # get string list
    uid = 0
    strings = []
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
            for result in localizedStringComment.finditer(content):
                uid += 1
                strings.append((result.group(1), result.group(2), file, uid))
            for result in localizedStringNil.finditer(content):
                uid += 1
                strings.append((result.group(1), '', file, uid))
            for result in localized.finditer(content):
                uid += 1
                strings.append((result.group(1), '', file, uid))

    return strings

def format_localized_strings(strings):
    # find duplicates
    duplicated = []
    filestrings = {}
    for string1 in strings:
        dupmatch = 0
        for string2 in strings:
            if string1[3] == string2[3]:
                continue
            if string1[0] == string2[0]:
                if string1[2] != string2[2]:
                    dupmatch = 1
                break
        if dupmatch == 1:
            dupmatch = 0
            for string2 in duplicated:
                if string1[0] == string2[0]:
                    dupmatch = 1
                    break
            if dupmatch == 0:
                duplicated.append(string1)
        else:
            dupmatch = 0
            if string1[2] in filestrings:
                for fs in filestrings[string1[2]]:
                    if fs[0] == string1[0]:
                        dupmatch = 1
                        break
            else:
                filestrings[string1[2]] = []
            if dupmatch == 0:
                filestrings[string1[2]].append(string1)

    outputstring = ''
    # output filewise
    for key in filestrings.keys():
        outputstring += '/* ' + key + ' */\n' + '\n'
        
        strings = filestrings[key]
        for string in strings:
            if string[1] == '':
                outputstring += '"' + string[0] + '" = "' + string[0] + '";' + '\n\n'
            else:
                outputstring += '/* ' + string[1] + ' */' + '\n'
                outputstring += '"' + string[0] + '" = "' + string[0] + '";' + '\n\n'

        outputstring += '\n'

    outputstring += '\n/* SHARED STRINGS */\n' + '\n'

    # output duplicates
    for string in duplicated:
        if string[1] == '':
            outputstring += '"' + string[0] + '" = "' + string[0] + '";' + '\n\n'
        else:
            outputstring += '/* ' + string[1] + ' */' + '\n'
            outputstring += '"' + string[0] + '" = "' + string[0] + '";' + '\n\n'

    return outputstring

def verify_text_format(content):
    badlines = []
    lines = re.split("\r?\n", content);
    emptylineregex = re.compile(r'^\s*$')
    formatregex    = re.compile(r'^("([^"\\]*(?:\\.[^"\\]*)*)") = ("([^"\\]*(?:\\.[^"\\]*)*)";)')
    commentregex   = re.compile(r'/\*(.)*\*/')
    i = 1
    for line in lines[:]:
        result1 = emptylineregex.search(line)
        result2 = formatregex.search(line)
        result3 = commentregex.search(line)
        
        if (result1 is None and result2 is None and result3 is None):
            badlines.append(i);
        i = i + 1
    
    if (len(badlines) > 0):
        print "Bad Lines In File: " + file
        print badlines
        return False
    return True

def verify_file_format(file):
    with open(file, 'r') as f:
        content = f.read().decode('latin1').encode('utf8')
        return verify_text_format(content)

def get_file_folder_name(file):
    filecomponents = file.split('/')
    foldername = filecomponents[len(filecomponents)-2]
    noextention = foldername.split('.')[0]
    return noextention

def get_file_language_abbr(file):
    filecomponents = file.split('-')
    languagename = filecomponents[len(filecomponents)-1]
    noextention = languagename.split('.')[0]
    return noextention

def create_formatted_combined_strings(inputString, localizationFiles, outputFolder = None):
    i = 0
    if not outputFolder:
        outputFolder = 'GeneratedLocalization/'
    
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    inputLines = re.split("\r?\n", inputString);

    # prepare regexes
    firstregex = re.compile(r'^("([^"\\]*(?:\\.[^"\\]*)*)")')
    secondregex= re.compile(r'("([^"\\]*(?:\\.[^"\\]*)*)";)')

    for file in localizationFiles:
        languagename = get_file_folder_name(file)
        
        with open(file, 'r') as f:
            outputstring = ''
            tempcontent = f.read()
            templines = re.split("\r?\n", tempcontent);
            
            for line in inputLines[:]:
                result1 = firstregex.search(line)
                result1end = secondregex.search(line)
                
                if (result1):
                    foundmatch = 0
                    for line2 in templines[:]:
                        result2 = firstregex.search(line2)
                        result2end = secondregex.search(line2)
                        if (result2 and result2.group(1) == result1.group(1)):
                            foundmatch = 1
                            outputstring += result1.group(1) + ' = ' + result2end.group(1) + '\n'
                    
                    if (foundmatch != 1):
                        outputstring += result1.group(1) + ' = ' + result1end.group(1) + ' /* New */' + '\n'
                else:
                    outputstring += line + '\n'
            
            outfile = open(os.path.abspath(outputFolder) + '/Localization-' + languagename.upper() + '.strings' , 'w')
            outfile.write(outputstring)
            outfile.close()
            i += 1


### Main Functionality ###
parser = argparse.ArgumentParser(description='iOS tool for generating Localization files')
parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')

subparsers = parser.add_subparsers(title='subcommands',
                                   description='valid subcommands',
                                   help='additional help',
                                   dest='command')
generate_parser = subparsers.add_parser('generate', help='Used to generate localization files optionally combining them with previous translations')
generate_parser.add_argument('-n', '--new', action='store_true', help='Creates brand new Localization file from source code')
generate_parser.add_argument('-e', '--existing', nargs=1, action='store', help='Creates new Localization file(s) for each existing file in the app')
generate_parser.add_argument('-i', '--input', nargs=1, action='store', help='Project folder path or individual file')
generate_parser.add_argument('-o', '--output', nargs=1, action='store', help='Output file/folder path')

replace_parser = subparsers.add_parser('replace', help='Replaces existing Localization files with their new matching file')
replace_parser.add_argument('output', nargs=1, action='store', help='Output file/folder path')
replace_parser.add_argument('input', nargs=1, action='store', help='Project folder path or individual file')

args = parser.parse_args()

if args.verbose: print args

if args.command == 'generate':
    if args.verbose: print "Generating localization strings from files"
    
    if args.input:
        strings = get_localize_strings_from_files(fetch_files_recursive(args.input, extension = '.m'))
    else:
        strings = get_localize_strings_from_files(fetch_files_recursive('.', extension = '.m'))

    formattedstring = format_localized_strings(strings)
        
    if args.new:
        if args.output:
            outfile = open(args.output[0], 'w')
            outfile.write(formattedstring)
            outfile.close()
        else:
            print formattedstring
            
        if args.verbose: print "Success: Generated New localization file"
    
    elif args.existing:
        if args.verbose: print "Searching for already existing localization files"
        
        # All Localization Files found in the Directory
    
        localizationFiles = fetch_files_recursive(args.existing, 'Localizable', extension = '.strings')

        if not localizationFiles:
            print "No existing Localization files found. To generate a fresh copy use the list command"
            sys.exit()
    
        badLinesFound = False
        if args.verbose: print "Verifying localization files format"
        for file in localizationFiles:
            if not verify_file_format(file):
                badLinesFound = True

        if args.verbose: print "Verifying the generated localization strings format"
        if not verify_text_format(formattedstring):
            badLinesFound = True
        
        if (badLinesFound):
            if args.verbose: print "Failed to verify input format"
            sys.exit()
        elif args.verbose: print "Success: Verified input format"

        if args.verbose: print "Creating combined localization strings for each existing localization"
        if args.output:
            create_formatted_combined_strings(formattedstring, localizationFiles, args.output[0])
        else:
            create_formatted_combined_strings(formattedstring, localizationFiles)
        
elif args.command == 'replace':
    if args.output:
        currentFiles = fetch_files_recursive(args.output, 'Localizable', extension = '.strings')
        
        if (args.input):
            newFiles = fetch_files_recursive(args.input, extension = '.strings')

            for newFile in newFiles:
                languageAbbr = get_file_language_abbr(newFile).upper()
                
                for oldFile in currentFiles:
                    oldAbbr = get_file_folder_name(oldFile).upper()

                    if languageAbbr == oldAbbr:
                        shutil.copyfile(newFile, oldFile)

