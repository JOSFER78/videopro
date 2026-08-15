from loguru import logger
from app.config import config

RUNTIME_CONFIG_SECTIONS = {
    "app": config.app,
    "azure": config.azure,
    "chatterbox": config.chatterbox,
    "elevenlabs": config.elevenlabs,
    "minimax_tts": config.minimax_tts,
    "siliconflow": config.siliconflow,
    "ui": config.ui,
}

def set_runtime_config(section_name: str, key: str, value):
    config_section = RUNTIME_CONFIG_SECTIONS.get(section_name)
    if config_section is None:
        return False
    updated = config.update_config_nonblocking(config_section, key, value)
    if not updated:
        logger.debug(f"deferred WebUI config update: section={section_name}, key={key}")
    return updated

def delete_runtime_config(section_name: str, key: str):
    config_section = RUNTIME_CONFIG_SECTIONS.get(section_name)
    if config_section is None:
        return False
    deleted = config.delete_config_nonblocking(config_section, key)
    if not deleted:
        logger.debug(f"deferred WebUI config delete: section={section_name}, key={key}")
    return deleted

def save_runtime_config():
    saved = config.try_save_config()
    if not saved:
        logger.debug("deferred WebUI config save until active task completes")
    return saved

def run_llm_read_operation(operation_name: str, operation):
    with config.try_runtime_config_lock() as lock_acquired:
        app_config_snapshot = config.snapshot_config_with_pending(config.app)
        if lock_acquired:
            return operation(app_config_snapshot)

    logger.info(f"run read-only LLM operation with active task configuration: operation={operation_name}")
    return operation(app_config_snapshot)
