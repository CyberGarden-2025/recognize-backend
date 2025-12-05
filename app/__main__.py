import uvicorn
from app.settings import SETTINGS


def main():
    uvicorn.run(
        app="app.api.server:app",
        host=SETTINGS.API_HOST,
        port=SETTINGS.API_PORT,
        log_level=SETTINGS.LOGGING_LEVEL.lower(),
        reload=SETTINGS.IS_DEBUG,
        reload_includes=["app"],
    )


if __name__ == "__main__":
    main()
