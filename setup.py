from setuptools import setup, find_packages

# python setup.py bdist_wheel
# twine upload dist/*
# twine upload --repository testpypi dist/jaqpotpy-2.0.0b0-py3-none-any.whl


setup(name='jaqpotpy',
      # version='2.0.5-beta0',
      version='1.0.23',
      description='Python client for Jaqpot',
      url='https://github.com/euclia/jaqpotpy',
      author='Pantelis Karatzas',
      author_email='pantelispanka@gmail.com',
      license='Apache License Version 2.0',
      packages=find_packages(exclude=["*.tests"]),
      # packages=['jaqpotpy', 'jaqpotpy.api', 'jaqpotpy.mappers', 'jaqpotpy.utils'
      #           , 'jaqpotpy.entities', 'jaqpotpy.dto', 'jaqpotpy.doa'
      #           , 'jaqpotpy.helpers', 'jaqpotpy.colorlog', 'jaqpotpy.models', 'jaqpotpy.cfg'
      #           , 'jaqpotpy.datasets', 'jaqpotpy.descriptors', 'jaqpotpy.descriptors.molecular'
      #           , 'jaqpotpy.descriptors.graph'],
      install_requires=[
            'pandas', 'requests', 'pydantic', 'rdkit-pypi', 'mordred', 'pyjwt', 'scikit-learn'
            # ,'tornado',
            # 'scikit-learn', 'torch', 'torch-scatter', 'torch-sparse', 'torch-cluster'
            # , 'torch-spline-conv', 'torch-geometric', 'dgl', 'torch_sparse', 'kennard-stone'
      ],
      zip_safe=False)

# .sdf
#