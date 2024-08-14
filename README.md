# FastAPI Application with Celery & Celery-Beat

This project includes a FastAPI application integrated with Celery for task management and Celery-Beat for task
scheduling. It uses Docker for containerization and supports both Docker Compose and manual builds.

## Environment Setup

## a) Build with docker-compose

1. **Create Environment Variables:**
    - Create your own `.env` file by using the [sample](envs/.env_sample_for_docker_compose) provided:
      ```sh
      cp envs/.env_sample_for_docker_compose .env
      ```

2. **Build and Start Containers:**
    - In the project directory, run the following command to build and start the services:
      ```sh
      docker-compose up --build
      ```

## b) Build manually

Alternatively, you can start each container separately.

1. **Create Environment Variables:**
    - Use the [sample file](envs/.env_sample_for_manual_builds) for manual builds:
      ```sh
      cp envs/.env_sample_for_manual_builds .env
      set -o allexport
      source .env
      ```

2. **Set Up MySQL Server:**
    - Start the MySQL Docker container:
      ```sh
      docker run -p ${MYSQL_PORT}:3306 --detach --name=$MYSQL_CONTAINER_NAME --env-file=.env mysql
      ```
    - Wait for the MySQL server to be ready (approximately 10 seconds).
    - Create the database schema:
      ```sh
      docker exec -i $MYSQL_CONTAINER_NAME mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE library CHARACTER SET utf8;"
      ```

3. **Set Up Redis:**

    - Start Redis:
      ```sh
      docker run --rm --detach -p ${REDIS_PORT}:6379 --name $REDIS_CONTAINER_NAME redis:latest
      ```
4. **Set Up FastAPI Server:**

    - Build and run the FastAPI backend server:
      ```sh
      docker build -t onurklngc/library-backend:0.0.1 .
      docker stop $LIBRARY_BACKEND_CONTAINER_NAME && docker rm $LIBRARY_BACKEND_CONTAINER_NAME
      docker run --env-file=.env -p ${LIBRARY_BACKEND_PORT}:8081 --name $LIBRARY_BACKEND_CONTAINER_NAME \
      onurklngc/library-backend:0.0.1
      ```

5. **Set Up Celery Applications:**

    - Start Celery Worker:
      ```sh
      docker run --env-file=.env --name $CELERY_CONTAINER_NAME --entrypoint "" onurklngc/library-backend:0.0.1 celery -A celery_app worker -l info
      ```
    - Start Celery Beat:
      ```sh
      docker run --env-file=.env --name $CELERY_BEAT_CONTAINER_NAME --entrypoint "" onurklngc/library-backend:0.0.1 celery -A celery_app beat -l info
      ```

## Accessing the API

Once the FastAPI server is running, you can interact with the API using Swagger UI.
Visit [http://0.0.0.0:8081/docs](http://0.0.0.0:8081/docs) in your browser.

## Checking Celery Jobs

Celery is used in this project for handling asynchronous tasks, such as sending daily reminders for overdue books and
generating weekly reports. These tasks are managed by Celery Worker and scheduled by Celery Beat.

### Monitoring Celery Jobs

- **Daily Overdue Book Reminders:**
    - Celery sends reminders to patrons for overdue books every day.
    - You can monitor the execution of this task by checking the logs of the Celery Worker container. The logs will show
      when reminders are sent and to whom.

- **Weekly Reports:**
    - Every week, Celery generates a report of book checkouts and other relevant statistics.
    - This report generation is also logged, and you can check the output in the Celery Worker logs.

### Viewing Logs

To view the logs where the Celery jobs are printed, use the following command to view real-time logs from the Celery
Worker:
```sh
docker logs -f $CELERY_CONTAINER_NAME
```

These logs will show the execution of scheduled tasks, such as sending daily overdue book reminders and generating
weekly reports. If the tasks are running as expected, you will see log entries indicating their completion.

### Adjusting the Scheduler

If you want to see the job result logs sooner, you can adjust the cron job scheduler in the Celery Beat configuration:

- Modify the scheduling frequency of the tasks to a shorter interval for testing or quicker feedback.

## Testing

1. **Run Unit Tests:**
    - To execute the tests for API endpoints, use:
      ```sh
      pytest
      ```

2. **Populate Database for Testing:**
    - You can populate the database with test data and validate the endpoints by running:
      ```sh
      python tests/populate.py
      ```

## Additional Information

- **Logs and Monitoring:**
    - Logs for Celery Worker and Celery Beat can be monitored in real-time using the `-l info` flag.

- **Scaling and Performance:**
    - The services can be scaled easily by adjusting the `docker-compose.yml` or by running multiple instances of the
      containers.
