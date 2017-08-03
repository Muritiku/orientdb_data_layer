from setuptools import setup, find_packages

setup(name='orientdb_data_layer',
      version='0.4.0',
      description='Data layer provider for OrientDB. (ORM/Repository/helpers)',
      long_description='Data layer provider for OrientDB. Easy to use ORM and Repository provider for OrientDB (with using pyorient)',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='orientdb orient pyorient',
      url='http://github.com/Muritiku/orientdb_data_layer',
      author='Anton Dziavitsyn',
      author_email='devitsin@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'pyorient',
      ],
      include_package_data=True,
      zip_safe=False)
