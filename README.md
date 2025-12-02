# Practice 1:
In this practice, we created an API that enables us to utilize the functions we developed in Seminar 1. We put all this practice inside a Docker so it can easily be run on any device.

1.    For this task, we created a Docker with a _python:3.12-slim_ machine. We used FastAPI to create a simple root endpoint with a simple message to ensure everything is working.
2.    For this task, we initially created a separate Docker with an Ubuntu machine where we would download _ffmpg_. We later decided that it was much simpler and easier to have everything in the same Docker. To do so, we needed to change the Docker image of the first machine from _python:3.12-slim_ to _python:3.12-slim-bullseye_, which supports _devian_, allowing us to download _ffmpeg_.
3.    This task requests that we adapt the code from Seminar 1. We compartmentalized the seminar's functions so they are completely independent from the API and included the Python file in the _main.py_ file.
4.    To prove that our task 3 was successful, we are requested to create 2 endpoints that process some actions from Seminar 1. We decided to create an endpoint for rescaling an image and another for converting an image to black and white. **IMPORTANT:** to be able to access these endpoints, the user must add "_/docs_" to the URL.
5.    As we joined the API and the ffmpeg Docker into one, this task is unnecessary.
