from airflow import DAG, dag
from airflow.timetables.trigger import CronTriggerTimetable
from datetime import timedelta

DAG(dag_id="class_default_schedule", schedule=timedelta(days=1))

DAG(dag_id="class_schedule", schedule="@hourly")

DAG(dag_id="class_timetable", schedule=CronTriggerTimetable())

DAG(dag_id="class_schedule_interval", schedule="@hourly")


@dag(schedule=timedelta(days=1))
def decorator_default_schedule():
    pass


@dag(schedule="0 * * * *")
def decorator_schedule():
    pass


@dag(schedule=CronTriggerTimetable())
def decorator_timetable():
    pass


@dag(schedule="0 * * * *")
def decorator_schedule_interval():
    pass
