Only 2 python files required.

Copy the phenome tools and extensions/lib to a new directory location

i.e. if in a new directory "tools_test",

cp ../holitics_core_agent/phenome/tools/miner_dumper.py ./phenome/tools/
cp ../holitics_core_agent/phenome/extensions/lib/pycgminer.py ./phenome/extensions/lib/

To run:

python3 -m phenome.tools.miner_dumper -ip 10.1.10.13
python3 -m phenome.tools.miner_dumper -ip 10.1.10.13 -antminer
python3 -m phenome.tools.miner_dumper -ip 10.1.10.13 -antminer -cmd version
