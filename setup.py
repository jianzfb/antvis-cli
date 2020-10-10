from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='antvis',
      version='0.0.2',
      description='machine learning manage client',
      __short_description__='machine learning manage client',
      url='http://www.mltalker.com',
      author='jian',
      author_email='jian@mltalker.com',
      packages=find_packages(),
      long_description=readme(),
      include_package_data=True,
      zip_safe=False,)