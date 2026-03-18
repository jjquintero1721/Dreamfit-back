import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.services.coach_code_service import CoachCodeService

scheduler_logger = logging.getLogger("dreamfit_api.scheduler")


class CoachCodeScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._setup_jobs()

    def _setup_jobs(self):

        # CronTrigger: cada 8 horas, iniciando a las 4:00 AM
        trigger = CronTrigger(hour="4,12,20", minute=0)

        self.scheduler.add_job(
            self._update_coach_codes_job,
            trigger=trigger,
            id="update_coach_codes",
            name="Update Coach Codes Every 8 Hours",
            replace_existing=True,
            misfire_grace_time=3600
        )

        scheduler_logger.info(
            "SCHEDULER_JOB_CONFIGURED | Job: update_coach_codes | "
            "Schedule: Every 8 hours (4:00 AM, 12:00 PM, 8:00 PM)"
        )

    async def _update_coach_codes_job(self):
        """
        Tarea programada que actualiza todos los códigos de entrenadores
        """
        execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        scheduler_logger.info(
            f"CRON_JOB_STARTED | Time: {execution_time} | "
            f"Job: update_coach_codes"
        )

        try:
            updated_count = await CoachCodeService.update_all_coach_codes()

            scheduler_logger.info(
                f"CRON_JOB_COMPLETED | Time: {execution_time} | "
                f"CodesUpdated: {updated_count} | Status: SUCCESS"
            )

        except Exception as e:
            scheduler_logger.error(
                f"CRON_JOB_FAILED | Time: {execution_time} | "
                f"Error: {str(e)} | Status: FAILURE"
            )

    def start(self):
        """Inicia el scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            scheduler_logger.info("SCHEDULER_STARTED | Coach code scheduler is now running")

    def shutdown(self):
        """Detiene el scheduler de forma segura"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            scheduler_logger.info("SCHEDULER_SHUTDOWN | Coach code scheduler stopped")

    async def run_now(self):
        """
        Ejecuta la actualización de códigos inmediatamente (útil para pruebas)
        """
        scheduler_logger.info("MANUAL_EXECUTION | Running coach code update manually")
        await self._update_coach_codes_job()