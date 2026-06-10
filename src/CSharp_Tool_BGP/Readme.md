# CSharp Tool BGP

## Description

C Sharp Tool is a tool for extracting features from BGP update files.

These files can be obtained from site collections such as RIPE and Routeviews. After downloading in MRT format, these files need to be converted to ASCII.

## Usage

For execution in Windows environments, the ConsoleApplication1.exe file can be executed directly.

In Linux and MacOS environments, Mono must be used to run the C Sharp Tool.

### Case 1: No arguments passed on the command line

```bash
mono ConsoleApplication1.exe
```

* INPUT: The program will assume the existence of a DUMP file in the same directory where the .exe file is being executed. If the file does not exist, the program will abort with an error message.

* OUTPUT: The program will create two files in the same directory where the .exe file is being executed. The file names will be: DUMP_featureselection.txt and DUMP_out.txt.

### Case 2: With one argument passed on the command line
```bash
mono ConsoleApplication1.exe ./dump_examples/DUMP
```

* INPUT: The program will read the file passed by argument. In the case of the example, the file./dump_examples/DUMP. Any absolute or relative location can be passed. If the file does not exist, the program will abort with an error message.

* OUTPUT: The files created will have the same name and location as the input file, and with the suffixes _featureselection.txt and _out.txt.

## Output

The 37 BGP features were extracted using this C# tool.

* Columns 1-4: time (column 1: hour+minute; column 2: hour; column 3: minute; column 4: second)
* Columns 5-41: features

### List of features extracted from BGP update messages:
```bash
1. Number of announcements
2. Number of withdrawals
3. Number of announced NLRI prefixes
4. Number of withdrawn NLRI prefixes
5. Average AS-path length
6. Maximum AS-path length
7. Average unique AS-path length
8. Number of duplicate announcements
9. Number of implicit withdrawals
10. Number of duplicate withdrawals
11. Maximum edit distance
12. Arrival rate
13. Average edit distance
14-23. Maximum AS-path length = n, where n = (11, ...,20)
24-33. Maximum edit distance = n, where n = (7, ...,16)
34. Number of Interior Gateway Protocol (IGP) packets
35. Number of Exterior Gateway Protocol (EGP) packets
36. Number of incomplete packets
37: Packet size (B)
```

Source: [link](https://www.sfu.ca/~ljilja/cnl/projects/BGP_datasets/index.html)

## Building

```bash
cd src/CSharp_Tool_BGP/ConsoleApplication1
xbuild ConsoleApplication1.csproj
```

xbuild is Mono’s implementation of msbuild and it allows projects that have an msbuild file to be compiled natively on Linux or MacOS.
