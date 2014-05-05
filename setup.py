from setuptools import setup, find_packages


README = open('README.rst').read()


setup(name="ESTester",
      author="Tatiana Al-Chueyr Pereira Martins",
      author_email="tatiana.alchueyr@gmail.com",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
      download_url = 'http://pypi.python.org/pypi/ESTester',
      description=u"Utilities for testing ElasticSearch queries",
      include_package_data=True,
      install_requires=["requests>=2.0.0"],
      license="GNU GPLv2",
      long_description=README,
      packages=find_packages(),
      tests_require=["coverage==3.6", "nose==1.2.1", "pep8==1.4.1", "mock==1.0.1", "pylint==1.0.0"],
      url = "http://github.com/tatiana/estester",
      version="1.3.0a"
)
