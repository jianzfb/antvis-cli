from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='antviscli',
      version='0.1.20',
      description='machine learning manage client',
      __short_description__='machine learning manage client',
      url='http://www.vibstring.com',
      author='jian',
      author_email='jian@vibstring.com',
      packages=find_packages(),
      long_description=readme(),
      include_package_data=True,
      zip_safe=False,)
