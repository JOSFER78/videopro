import os
import copy
import threading
import tempfile
from pathlib import Path
import tomlkit

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = _ROOT_DIR / "config.toml"
MASK_PLACEHOLDER = "••••••••••••••••"
SENSITIVE_KEYS = {"api_key", "api_token", "secret_access_key", "tokens", "access_key_id", "replicate_api_token"}

class SynchronizedConfigManager:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SynchronizedConfigManager, cls).__new__(cls)
                    cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self.config_path = CONFIG_PATH
        self.doc = tomlkit.document()
        self.raw_data = {}
        self.load_from_disk()

    def load_from_disk(self):
        with self._lock:
            if not self.config_path.exists():
                example_path = self.config_path.with_name("config.example.toml")
                if example_path.exists():
                    self.config_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
            
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.doc = tomlkit.parse(f.read())
            self.raw_data = self.doc.unwrap()
            self._sync_environment_variables()

    def _sync_environment_variables(self):
        rep_token = self.get("replicate.api_token") or self.get("app.replicate_api_token")
        if rep_token:
            os.environ["REPLICATE_API_TOKEN"] = str(rep_token)
        
        hf_tokens = self.get("huggingface.tokens", [])
        if hf_tokens and isinstance(hf_tokens, list):
            os.environ["HF_TOKEN"] = str(hf_tokens[0])
            
        groq_key = self.get("llm.groq.api_key")
        if groq_key:
            os.environ["GROQ_API_KEY"] = str(groq_key)

    def get(self, key_path: str, default=None):
        with self._lock:
            parts = key_path.split(".")
            val = self.raw_data
            for p in parts:
                if isinstance(val, dict) and p in val:
                    val = val[p]
                else:
                    return default
            return val

    def get_snapshot(self) -> dict:
        with self._lock:
            return copy.deepcopy(self.raw_data)

    def get_masked_for_ui(self) -> dict:
        with self._lock:
            def _mask_dict(d):
                masked = {}
                for k, v in d.items():
                    if isinstance(v, dict):
                        masked[k] = _mask_dict(v)
                    elif k in SENSITIVE_KEYS and isinstance(v, str) and v.strip():
                        masked[k] = MASK_PLACEHOLDER
                    elif k in SENSITIVE_KEYS and isinstance(v, list):
                        masked[k] = [MASK_PLACEHOLDER if isinstance(item, str) and item else item for item in v]
                    else:
                        masked[k] = v
                return masked
            return _mask_dict(self.raw_data)

    def update_key(self, section: str, key: str, value, persist: bool = True):
        with self._lock:
            if value == MASK_PLACEHOLDER:
                return

            if section not in self.doc:
                self.doc[section] = tomlkit.table()

            if key in SENSITIVE_KEYS and isinstance(value, list):
                original_list = self.get(f"{section}.{key}", [])
                new_list = []
                for idx, item in enumerate(value):
                    if item == MASK_PLACEHOLDER and idx < len(original_list):
                        new_list.append(original_list[idx])
                    else:
                        new_list.append(item)
                value = new_list

            self.doc[section][key] = value
            self.raw_data = self.doc.unwrap()
            self._sync_environment_variables()

            if persist:
                self._atomic_persist()

    def _atomic_persist(self):
        with self._lock:
            temp_dir = self.config_path.parent
            with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
                tf.write(tomlkit.dumps(self.doc))
                temp_name = tf.name
            os.replace(temp_name, self.config_path)

config_manager = SynchronizedConfigManager()
