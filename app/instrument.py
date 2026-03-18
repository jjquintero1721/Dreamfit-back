"""
Inicialización de Sentry para error monitoring y performance tracking.
"""
import os
import logging
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Cargar variables de entorno
load_dotenv()

# Configuración de Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))

# Inicializar Sentry si el DSN está configurado
if SENTRY_DSN:
    # Configurar integración de logging (solo logs de ERROR se envían a Sentry)
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            FastApiIntegration(transaction_style="url"),
            sentry_logging,
        ],
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=True,
        enable_tracing=True,
    )

    print(f"Sentry inicializado correctamente")
    print(f"Traces sample rate: {SENTRY_TRACES_SAMPLE_RATE}")
else:
    print("Sentry no inicializado - SENTRY_DSN no configurado")
