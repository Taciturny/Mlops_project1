FROM public.ecr.aws/lambda/python:3.9

# Install pipenv
RUN pip install pipenv

# Copy the Pipfiles and Pipfile.lock to the container
COPY Pipfile Pipfile.lock /var/task/

# Set the working directory
WORKDIR /var/task

# Install dependencies using pipenv
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of your project files
COPY . /var/task/

# Set the entry point
CMD [ "lambda.lambda_test" ]
