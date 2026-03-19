class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}

    def __str__(self):
        return f"{self.role}: {self.content}"

    def get_role(self):
        return self.role

    def get_content(self):
        return self.content

    def set_role(self, role):
        if role not in ["user", "assistant", "system"]:
            raise ValueError("Invalid role. Must be one of: user, assistant, system")
        self.role = role

    def set_content(self, content):
        self.content = content

    def is_user(self):
        return self.role == "user"

    def is_assistant(self):
        return self.role == "assistant"

    def is_system(self):
        return self.role == "system"

    def flip_role(self):
        if self.role == "user":
            self.role = "assistant"
        elif self.role == "assistant":
            self.role = "user"
