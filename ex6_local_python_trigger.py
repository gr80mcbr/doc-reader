# An example using the Local Site Driver to downloads a python file and input file, runs a job that will execute the 
# python file using the input file.  An event handler is then set up so once the job completes the event handler job will upload the file.  

# The python file used here simply takes a file with a list of numbers, multiplies by a specified number, and then writes 
# the multiplied numbers to an output file.

import logging
import time
import os

from lwfm.base.Site import Site
from lwfm.base.JobDefn import JobDefn
from lwfm.base.JobStatus import JobStatus, JobStatusValues, JobContext
from lwfm.server.JobStatusSentinelClient import JobStatusSentinelClient
from lwfm.base.SiteFileRef import FSFileRef
from pathlib import Path

siteName = "local"

# Get the directory of the current script
script_directory = os.path.dirname(__file__)

jobFile = os.path.join(script_directory, "test_resources/multiply.py")
inputFile = os.path.join(script_directory, "test_resources/numbers.txt")
inputDest = os.path.join(script_directory, "test_resources/input")
outputFile = os.path.join(script_directory, "test_resources/output/output.txt")
outputDest = os.path.join(script_directory, "test_resources/job/multiplied_numbers.txt")
postProcFile = os.path.join(script_directory, "test_resources/post_processing.py")

multiplier = 5

if __name__ == '__main__':

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    # one Site for this example - construct an interface to the Site
    site = Site.getSiteInstanceFactory(siteName)
    # a "local" Site login is generally a no-op
    site.getAuthDriver().login()

    logging.info("login successful")

    # setting up the destination file ref
    file = os.path.realpath(inputDest)
    file_path = Path(file)

    # downloading the python file which will be executed during the job
    jobFileRef = FSFileRef()
    jobFileRef = FSFileRef.siteFileRefFromPath(jobFile)
    site.getRepoDriver().get(jobFileRef, file_path)
    print(file + " downloaded")

    # uploading the input file that will be passed in as an argument to the python script.
    inputFileRef = FSFileRef()
    inputFileRef = FSFileRef.siteFileRefFromPath(inputFile)
    site.getRepoDriver().get(inputFileRef, file_path)
    print(file + " downloaded")

    # uploading the email file which will send the output after the job completes
    postProcFileRef = FSFileRef()
    postProcFileRef = FSFileRef.siteFileRefFromPath(postProcFile)
    site.getRepoDriver().get(postProcFileRef, file_path)
    print(file + " downloaded")

    # what named computing resources are available on this site?
    logging.info("compute types = " + str(site.getRunDriver().listComputeTypes()))

    # define the Job - use all Job defaults except the actual command to execute
    jobDefn = JobDefn()

    # The entry point is the command line execution, here we are executing our python file, passing in out input file, multiplier number, and where it will write its output.
    jobDefn.setEntryPoint("python " + jobFileRef.getPath() + " " + inputFileRef.getPath() + " " + str(multiplier) + " " + outputFile)

    # submit the Job to the Site
    jobContext = site.getRunDriver().submitJob(jobDefn).getJobContext()

    # define the Job - use all Job defaults except the actual command to execute
    postJobDefn = JobDefn()

    # Here we are setting up a job that will trigger that will run when the job completes.  This will send the output file to 
    postJobDefn.setEntryPoint("python " + postProcFileRef.getPath() + " --output " + outputFile + " --destination " + outputDest)

    postProcContext = JobContext(jobContext) 

    # sets up an event handler so that when the job completes it will run post processing to upload the file to our desired location
    site.getRunDriver().setEventHandler(jobContext, JobStatusValues.COMPLETE, None, postJobDefn, postProcContext, None)
