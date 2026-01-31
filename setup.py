import setuptools
setuptools.setup(
     name='instabackup',  
     version='0.1',
     entry_points={
         'console_scripts': ['instabackup=instabackup:main'],
     },
     author='Daniel Margolis',
     author_email='dan@af0.net.',
     description='Backup Instapaper to local disk',
     long_description=open('README.md', 'r').read(),
     long_description_content_type='text/markdown',
     url='https://github.com/danmarg/instabackup',
     packages=setuptools.find_packages(
         include=['instabackup', 'instabackup.*'],
     ),
     classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
     ],
     install_requires=[
         'pyinstapaper @ git+https://github.com/danmarg/pyinstapaper.git',
         'retry',
         'setuptools',
    ],
 )
