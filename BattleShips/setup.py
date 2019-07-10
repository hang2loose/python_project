import setuptools

with open("README.md", 'r') as f:
    long_description = f.read()

setuptools.setup(
   name='BattleShips',
   version='1.0',
   description='BattleShips Client',
   license="MIT",
   long_description=long_description,
   author='hang2loose, SaveEnergy',
   packages=setuptools.find_packages(),  #same as name
   install_requires=['requests', 'python-socketio', 'appjar'], #external packages as dependencies
)
