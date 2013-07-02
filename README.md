glacier-sync
============
A simple python script for copying the contents of a folder (all sub-folders and files) to Amazon glacier.

This assumes that you have an AWS account set up - http://aws.amazon.com/

The runtime environment requires Python and the AWS boto library installed - http://boto.readthedocs.org/en/latest/getting_started.html

You are also required to create a .boto configuration file containing your AWS credentials in your user root folder. 
I.E. create ~/.boto and insert your credential info.
http://boto.readthedocs.org/en/latest/getting_started.html#configuring-boto-credentials

To determine where to place the .boto file on windows, run the folowing command in the Python interpreter:
	import os
	os.path.expanduser('~/.boto')

See this tutorial on where to find your AWS credential info - http://aws.amazon.com/articles/Amazon-S3/3998


Running the script
------------------

You can configure the local folder you want to copy to glacier, as well as other options like the AWS region to use, and the glacier vault name to create/use to store your archives (re files), in the sync.py code file directly, or by passing these options in as arguments at the command line.
See:
	python sync.py --help
	
for information on the available options.


Current scope / Future features
-------------------------------

At this stage this script only supports a one way sync fron a local machine to glacier. It does not currently support a reconciliation of files that may be on glacier but not on your local machine, or files that are on glacier that have not been recorded as already uploaded from your local machine.
There is scope to request an archive inventory from glacier that could be used to reconcile files already uploaded with those available on the local machine.
The archives are stored in glacier with the available meta date in the archive description to support future sync'ing and reconciliation. (The source machine name, full file path, and sha1 hash are all available).

Motivation
----------
I created this script as a quick way to get all of my family photos backed up to the cloud in a cost effective way. 
I was moving house and didn't want to risk my WHS backedup drives getting lost/broken and with it all of our photographs lost.
