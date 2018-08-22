from setuptools import setup

setup(
    name='Fingered_Server',
    version='0.0.1',
    install_requires=['woocommerce', 'PIL', 'barcode'],
    packages=['Interface', 'Production', 'Machine'],
    url='https://github.com/profitrolle/DEFYX/tree/master/Fingered_Server',
    license='BEERLICENCED',
    author='Profitrolle',
    author_email='',
    description='Interaction with the actuators packages'
)
