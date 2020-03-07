

## How to use

Steps: 

#####1. Type the following in terminal

```
cd && git clone https://github.com/CrizR/archival-utility.git

```

#####2. Add an alias to your bash_profile

```
vim ~/.bash_profile

(press a)  type in the following:

alias archiveutil="python3 /Users/[USERNAME]/archival-utility/run.py"

replace [USERNAME] with your username

(press escape and colon (:) then type wq and press enter)

now enter

. ~/.bash_profile

```

	
#####3. Navigate to the directory above the directory you are planning to archive
Example:

```
folder1 > directory_you_intend_to_archive >
									folder2 > files files
									folder3 > files files

cd folder1

```
#####4. Type in the following to execute

```
   
archiveutil -dir (directory_you_intend_to_archive) -sn (source) 

optional arguments:

-ap (prefix to your asset)
-dp (prefix to archived directories) (i.e PREFIXdirectoryName, __directoryName, ...etc)

```


