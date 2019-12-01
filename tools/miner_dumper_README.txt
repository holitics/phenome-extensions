This is the README for the Miner Dumper tool.


RUNNING THE DUMPER TOOL
-----------------------

This can be run from the top level directory of MinerMedic, for example:

python3 -m phenome.tools.miner_dumper -ip 10.1.10.13
python3 -m phenome.tools.miner_dumper -ip 10.1.10.13 -antminer
python3 -m phenome.tools.miner_dumper -ip 10.1.10.13 -antminer -cmd version


RUNNING THE DUMPER TOOL - Standalone
------------------------------------

Only 2 python files are required to get the Dumper to work. 

Copy the phenome tools and extensions/lib to a new directory location,
but keep the phenome subdirectory structure - for example: 

if in a new directory "tools_test",

cp {SOURCE_DIRECTORY}/phenome/tools/miner_dumper.py 		{DEST_DIRECTORY}/phenome/tools/
cp {SOURCE_DIRECTORY}/phenome/extensions/lib/pycgminer.py	{DEST_DIRECTORY}/phenome/extensions/lib/

Then, run as you normally would:

python3 -m phenome.tools.miner_dumper {ARGS}

