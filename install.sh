#bin/sh

# install dependencies
echo "dependencies install"
sudo apt-get update
sudo apt-get install libudev-dev python-smbus python-spidev i2c-tools

# manual install of utility
echo "talkpp utility installer"
cd utility
gcc -o talkpp talkpp.c -ludev
sudo cp talkpp /usr/local/bin
sudo chmod 775 /usr/local/bin/talkpp

echo "ppd utility installer"
gcc -o ppd ppd.c -ludev
sudo cp ppd /usr/local/bin
sudo chmod 775 /usr/local/bin/ppd

# install of python modules
echo "Python library installer"
cd ..
cd ~/solar_pi0_ws/lora_prj/library
sudo cp bme680.py bme680_cst.py lora.py lora_cst.py rf95.py rf95_cst.py /usr/local/lib/python2.7/dist-packages/
cd ..
echo "done!"
