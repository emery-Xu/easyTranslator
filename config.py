import json

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
    
    def load_config(self):
        """加载配置，如果配置不存在就创建初始化配置"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {
                "deepl_api_key": "",
                "hotkey": "ctrl+t",
                "target_lang": "ZH",
                "backend": "deepl",
                "ollama_host": "http://localhost:11434",
                "ollama_model": "qwen2.5:7b",
            }
            self.save_config(config)
        return config
    
    def save_config(self, config):
        """保存配置到文件"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)