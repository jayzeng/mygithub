from distutils.core import setup

setup(name='mygithub',
    version="0.0.1",
    description='My GitHub productivity scripts',
    author='Jay Zeng',
    author_email='jayzeng@jay-zeng.com',
    url='git@github.com:jayzeng/mygithub.git',
    scripts=['gitpublish.py'],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Version Control"
    ],
    license='MIT',
    keywords='pip distutils setuptools easy_install',
    requires=["github3.py", "GitPython"]
)
